import json
import os
from typing import Dict, List

import pandas as pd


def aggregate_scores(results: List[Dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        for fs in result['facet_scores']:
            rows.append({
                'conversation_id': result['conversation_id'],
                'turn_index': result['turn_index'],
                'speaker': result['speaker'],
                'turn_snippet': result['turn_text'][:120],
                'facet_id': fs['facet_id'],
                'facet_name': fs['facet_name'],
                'category': fs['category'],
                'score': fs['score'],
                'confidence': fs['confidence'],
                'evidence': fs.get('evidence', ''),
                'final_turn_score': result.get('final_turn_score', 0.0),
                'final_turn_confidence': result.get('final_turn_confidence', 0.0)
            })
    return pd.DataFrame(rows)


def summary_stats(df: pd.DataFrame) -> Dict:
    overall = {
        'mean_score': round(df['score'].mean(), 3),
        'mean_confidence': round(df['confidence'].mean(), 3),
        'mean_final_turn_score': round(df['final_turn_score'].mean(), 3),
        'mean_final_turn_confidence': round(df['final_turn_confidence'].mean(), 3),
        'total_turn_rows': int(df[['conversation_id', 'turn_index']].drop_duplicates().shape[0]),
        'total_facets': int(df['facet_id'].nunique())
    }
    per_category = (
        df.groupby('category')
        .agg(mean_score=('score', 'mean'), mean_confidence=('confidence', 'mean'), n=('facet_id', 'count'))
        .round(3)
        .reset_index()
        .to_dict(orient='records')
    )
    return {'overall': overall, 'per_category': per_category}


def save_results(results: List[Dict], out_dir: str = '../conversations') -> str:
    os.makedirs(out_dir, exist_ok=True)
    conv_id = results[0]['conversation_id'] if results else 'unknown'
    out_path = os.path.join(out_dir, f'{conv_id}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'meta': {'total_turns': len(results)}}, f, indent=2, ensure_ascii=False)
    return out_path


def export_csv(results: List[Dict], out_path: str) -> str:
    aggregate_scores(results).to_csv(out_path, index=False)
    return out_path


def load_results(path: str) -> List[Dict]:
    with open(path, encoding='utf-8') as f:
        return json.load(f)['results']