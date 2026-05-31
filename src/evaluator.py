import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["GOTO_NUM_THREADS"] = "1"

import json
import time
import logging
from typing import List, Dict, Optional

import requests
import pandas as pd

from prompt_builder import make_batches, build_prompt

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:1.5b")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
FACETS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_cleaned.csv')


def load_facets(path=FACETS_CSV) -> List[Dict]:
    df = pd.read_csv(path)
    df = df[df['observable_from_text'] == True].reset_index(drop=True)
    log.info(f"loaded {len(df)} observable facets")
    return df.to_dict(orient='records')


def call_llm(messages: List[Dict]) -> Optional[str]:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except Exception as e:
            log.warning(f"attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    return None


def parse_llm_output(raw: str, batch: List[Dict]) -> List[Dict]:
    try:
        text = raw.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            text = text.rsplit("```", 1)[0].strip()

        parsed = json.loads(text)
        returned_ids = {item.get("facet_id") for item in parsed}
        results = []

        for f in batch:
            if f["facet_id"] in returned_ids:
                match = next(item for item in parsed if item.get("facet_id") == f["facet_id"])
                results.append({
                    "facet_id": f["facet_id"],
                    "facet_name": f["facet_name"],
                    "category": f["category"],
                    "score": max(1, min(5, int(match.get("score", 1)))),
                    "confidence": max(0.0, min(1.0, float(match.get("confidence", 0.5))))
                })
            else:
                log.warning(f"facet {f['facet_id']} missing from output, using fallback")
                results.append({
                    "facet_id": f["facet_id"],
                    "facet_name": f["facet_name"],
                    "category": f["category"],
                    "score": 1,
                    "confidence": 0.0
                })

        return results

    except Exception as e:
        log.error(f"parse failed: {e}\nraw: {raw[:300]}")
        return [
            {
                "facet_id": f["facet_id"],
                "facet_name": f["facet_name"],
                "category": f["category"],
                "score": 1,
                "confidence": 0.0
            }
            for f in batch
        ]


def evaluate_turn(
    turn_text: str,
    conversation_id: str = "conv_001",
    turn_index: int = 0,
    speaker: str = "user",
    facets: Optional[List[Dict]] = None
) -> Dict:
    if facets is None:
        facets = load_facets()

    batches = make_batches(facets, BATCH_SIZE)
    all_scores = []

    log.info(f"[{conversation_id} turn {turn_index}] {len(facets)} facets, {len(batches)} batches")

    for i, batch in enumerate(batches):
        messages = build_prompt(turn_text, batch)
        raw = call_llm(messages)

        if raw is None:
            log.error(f"batch {i} failed, using fallback scores")
            scores = [
                {
                    "facet_id": f["facet_id"],
                    "facet_name": f["facet_name"],
                    "category": f["category"],
                    "score": 1,
                    "confidence": 0.0
                }
                for f in batch
            ]
        else:
            scores = parse_llm_output(raw, batch)

        all_scores.extend(scores)
        log.info(f"batch {i+1}/{len(batches)} done")

    return {
        "conversation_id": conversation_id,
        "turn_index": turn_index,
        "speaker": speaker,
        "turn_text": turn_text,
        "model": MODEL_NAME,
        "facet_scores": all_scores,
        "total_facets": len(all_scores),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def evaluate_conversation(turns: List[Dict], conv_id: str = None) -> List[Dict]:
    if conv_id is None:
        conv_id = f"conv_{int(time.time())}"

    facets = load_facets()
    results = []

    for idx, turn in enumerate(turns):
        result = evaluate_turn(
            turn_text=turn["text"],
            conversation_id=conv_id,
            turn_index=idx,
            speaker=turn.get("speaker", "user"),
            facets=facets
        )
        results.append(result)

    return results


if __name__ == "__main__":
    import sys

    text = sys.argv[1] if len(sys.argv) > 1 else "I'm really struggling. Everything feels hopeless and I don't know what to do."
    result = evaluate_turn(text)
    print(json.dumps(result, indent=2))