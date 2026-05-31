import json
from typing import List, Dict

BATCH_SIZE = 25

SYSTEM_PROMPT = """You are an expert at analyzing conversation text.
Your job is to score a single conversation turn on each given facet.

Score scale:
  1 = Not detectable in the text
  2 = Barely present / slight signals
  3 = Moderately present
  4 = Clearly present
  5 = Strongly dominant throughout

Rules:
- Only use what is in the text. Do not assume anything outside the turn.
- Return ONLY a valid JSON array. No explanation, no extra text.
- Format: [{"facet_id": int, "facet": "string", "score": int, "confidence": float}]
- confidence: 0.0 to 1.0, how certain you are given the available text.
- If you cannot tell from the text, give score 1 with confidence 0.1.
- Every facet in the input must appear in your output.
"""

FEW_SHOT = """
Example:
Turn: "I honestly don't care what you think. Your opinion is worthless."
Facets: [{"facet_id": 1, "facet": "Hostility"}, {"facet_id": 2, "facet": "Assertiveness"}, {"facet_id": 3, "facet": "Compassion"}]

Output:
[
  {"facet_id": 1, "facet": "Hostility",     "score": 5, "confidence": 0.96},
  {"facet_id": 2, "facet": "Assertiveness", "score": 5, "confidence": 0.91},
  {"facet_id": 3, "facet": "Compassion",    "score": 1, "confidence": 0.94}
]
"""


def make_batches(facets: List[Dict], size: int = BATCH_SIZE) -> List[List[Dict]]:
    return [facets[i:i+size] for i in range(0, len(facets), size)]


def build_prompt(turn_text: str, batch: List[Dict]) -> List[Dict]:
    facet_list = json.dumps(
        [{"facet_id": f["facet_id"], "facet": f["facet_name"]} for f in batch],
        indent=2
    )

    user_msg = f"""{FEW_SHOT}
Now score this:
Turn: "{turn_text}"
Facets: {facet_list}

Return ONLY the JSON array."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]