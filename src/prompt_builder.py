import json
from typing import List, Dict

BATCH_SIZE = 20

SYSTEM_PROMPT = """You are evaluating a single conversation turn for a production benchmark.
Score ONLY the current turn text using the provided facets.

Score scale:
-2 = strongly opposite / strong negative evidence
-1 = slight negative evidence
 0 = unclear, mixed, or not enough evidence
 1 = clear positive evidence
 2 = strong positive evidence

Important rules:
- Use only the visible text in the turn.
- Do not infer hidden biography, habits, religion, medical history, or lifestyle details.
- If a facet is not inferable from the text, return score 0 with low confidence.
- Respect scoring_direction: for lower_is_better facets, higher presence of the harmful trait should get more negative scores.
- Return ONLY valid JSON.
- Output format:
  [{"facet_id": 1, "score": 0, "confidence": 0.42, "evidence": "brief phrase"}]
- confidence must be between 0 and 1.
- evidence must be very short, under 12 words.
"""

FEW_SHOT = """
Example turn:
"I hate everyone here and I want to hurt them back."

Example facets:
[
  {"facet_id": 1, "facet_name": "Hostility", "category": "safety", "scoring_direction": "lower_is_better"},
  {"facet_id": 2, "facet_name": "Compassion", "category": "emotion", "scoring_direction": "higher_is_better"},
  {"facet_id": 3, "facet_name": "Clarity", "category": "linguistic", "scoring_direction": "higher_is_better"}
]

Example output:
[
  {"facet_id": 1, "score": -2, "confidence": 0.97, "evidence": "explicit hate and revenge"},
  {"facet_id": 2, "score": -2, "confidence": 0.94, "evidence": "no care or warmth"},
  {"facet_id": 3, "score": 1, "confidence": 0.79, "evidence": "direct wording"}
]
"""


def make_batches(facets: List[Dict], size: int = BATCH_SIZE) -> List[List[Dict]]:
    return [facets[i:i + size] for i in range(0, len(facets), size)]


def build_prompt(turn_text: str, batch: List[Dict]) -> List[Dict]:
    facet_list = json.dumps([
        {
            'facet_id': f['facet_id'],
            'facet_name': f['facet_name'],
            'category': f['category'],
            'scoring_direction': f['scoring_direction'],
            'applicable_to': f['applicable_to']
        }
        for f in batch
    ], ensure_ascii=False, indent=2)

    user_msg = f"""{FEW_SHOT}
Now evaluate this turn.

Turn text:
{json.dumps(turn_text, ensure_ascii=False)}

Facets:
{facet_list}

Return ONLY the JSON array."""

    return [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_msg}
    ]