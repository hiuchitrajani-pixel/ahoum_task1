import json
import logging
import os
import time
from typing import Dict, List, Optional

import pandas as pd
import requests

from prompt_builder import build_prompt, make_batches

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/chat')
MODEL_NAME = os.getenv('MODEL_NAME', 'qwen2.5:1.5b')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '20'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY', '2.0'))
FACETS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_benchmark_cleaned.csv')


def load_facets(path: str = FACETS_CSV) -> List[Dict]:
    df = pd.read_csv(path)
    df = df[df['observable_from_text'] == True].reset_index(drop=True)
    return df.to_dict(orient='records')


def call_llm(messages: List[Dict]) -> Optional[str]:
    payload = {
        'model': MODEL_NAME,
        'messages': messages,
        'stream': False,
        'options': {'temperature': 0.0, 'top_p': 0.9}
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=180)
            r.raise_for_status()
            return r.json()['message']['content']
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f'Could not connect to Ollama at {OLLAMA_URL}. Start it with: ollama serve')
        except Exception as e:
            log.warning(f'Attempt {attempt}/{MAX_RETRIES} failed: {e}')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return None


def _strip_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        text = '\n'.join(lines[1:])
        if text.endswith('```'):
            text = text[:-3].strip()
    return text


def _fallback(batch: List[Dict]) -> List[Dict]:
    return [
        {
            'facet_id': f['facet_id'],
            'facet_name': f['facet_name'],
            'category': f['category'],
            'score': 0,
            'confidence': 0.0,
            'evidence': 'no response'
        }
        for f in batch
    ]


def parse_llm_output(raw: str, batch: List[Dict]) -> List[Dict]:
    try:
        parsed = json.loads(_strip_json(raw))
        by_id = {item.get('facet_id'): item for item in parsed if isinstance(item, dict)}
        results = []
        for f in batch:
            item = by_id.get(f['facet_id'], {})
            score = item.get('score', 0)
            confidence = item.get('confidence', 0.0)
            evidence = str(item.get('evidence', 'not inferable'))[:80]

            try:
                score = int(score)
            except Exception:
                score = 0

            try:
                confidence = float(confidence)
            except Exception:
                confidence = 0.0

            results.append({
                'facet_id': f['facet_id'],
                'facet_name': f['facet_name'],
                'category': f['category'],
                'score': max(-2, min(2, score)),
                'confidence': max(0.0, min(1.0, confidence)),
                'evidence': evidence
            })
        return results
    except Exception as e:
        log.error(f'Parse failed: {e}')
        return _fallback(batch)


def filter_facets_for_speaker(facets: List[Dict], speaker: str) -> List[Dict]:
    if speaker not in {'user', 'assistant'}:
        return facets
    return [f for f in facets if f.get('applicable_to', 'both') in {'both', speaker}]


def compute_final_turn_score(facet_scores: List[Dict]) -> Dict:
    if not facet_scores:
        return {'final_turn_score': 0.0, 'final_turn_confidence': 0.0}

    weighted_sum = 0.0
    confidence_sum = 0.0

    for item in facet_scores:
        score = item.get('score', 0)
        conf = item.get('confidence', 0.0)
        weighted_sum += score * conf
        confidence_sum += conf

    if confidence_sum == 0:
        return {'final_turn_score': 0.0, 'final_turn_confidence': 0.0}

    final_score = weighted_sum / confidence_sum
    avg_conf = confidence_sum / len(facet_scores)

    return {
        'final_turn_score': round(final_score, 3),
        'final_turn_confidence': round(avg_conf, 3)
    }


def evaluate_turn(
    turn_text: str,
    conversation_id: str = 'conv_001',
    turn_index: int = 0,
    speaker: str = 'user',
    facets: Optional[List[Dict]] = None
) -> Dict:
    facets = load_facets() if facets is None else facets
    facets = filter_facets_for_speaker(facets, speaker)
    batches = make_batches(facets, BATCH_SIZE)
    all_scores = []

    log.info(f'[{conversation_id} turn {turn_index}] scoring {len(facets)} facets in {len(batches)} batches')

    for i, batch in enumerate(batches, start=1):
        messages = build_prompt(turn_text, batch)
        raw = call_llm(messages)
        scores = parse_llm_output(raw, batch) if raw is not None else _fallback(batch)
        all_scores.extend(scores)
        log.info(f'[{conversation_id} turn {turn_index}] batch {i}/{len(batches)} done')

    final_summary = compute_final_turn_score(all_scores)

    return {
        'conversation_id': conversation_id,
        'turn_index': turn_index,
        'speaker': speaker,
        'turn_text': turn_text,
        'model': MODEL_NAME,
        'facet_scores': all_scores,
        'total_facets': len(all_scores),
        'final_turn_score': final_summary['final_turn_score'],
        'final_turn_confidence': final_summary['final_turn_confidence'],
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }


def evaluate_conversation(turns: List[Dict], conv_id: Optional[str] = None) -> List[Dict]:
    conv_id = conv_id or 'conversation'
    facets = load_facets()
    results = []
    for idx, turn in enumerate(turns):
        results.append(evaluate_turn(
            turn_text=turn['text'],
            conversation_id=conv_id,
            turn_index=idx,
            speaker=turn.get('speaker', 'user'),
            facets=facets
        ))
    return results


def compute_conversation_final_score(results: List[Dict]) -> Dict:
    if not results:
        return {'final_conversation_score': 0.0, 'final_conversation_confidence': 0.0}

    score_sum = 0.0
    conf_sum = 0.0

    for r in results:
        score_sum += r.get('final_turn_score', 0.0) * r.get('final_turn_confidence', 0.0)
        conf_sum += r.get('final_turn_confidence', 0.0)

    if conf_sum == 0:
        return {'final_conversation_score': 0.0, 'final_conversation_confidence': 0.0}

    return {
        'final_conversation_score': round(score_sum / conf_sum, 3),
        'final_conversation_confidence': round(conf_sum / len(results), 3)
    }