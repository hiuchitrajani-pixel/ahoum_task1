import os
import re
import pandas as pd

RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_raw.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_benchmark_cleaned.csv')

PRIMARY_ALLOWED = {
    'linguistic', 'pragmatic', 'safety', 'emotion', 'social', 'behavioral', 'moral', 'clinical', 'other'
}

BLOCKLIST = [
    'astrology', 'hexagram', 'i ching', 'reiki', 'quran', 'sufi', 'kabbalah', 'bhagavad', 'kirtan',
    'pilgrimage', 'dhikr', 'vrata', 'seerah', 'zohar', 'aura', 'chakra', 'channeling', 'mantra',
    'yoga discipline hours', 'festival participation', 'candl', 'scripture', 'sacred text',
    'dance-cardio', 'dance rehearsal', 'macronutrient', 'snacking', 'breakfast-skipping',
    'home-cooked', 'restaurant meals', 'sleep-environment', 'caffeine intake', 'pet-enrichment',
    'eco-tourism', 'lulav', 'rising sign', 'blog-subscriber', 'peer-to-peer lending',
    'robotics-interaction', 'graffiti appreciation', 'museum', 'choir', 'passport', 'blood',
    'hormone', 'polygenic', 'chromatin', 'basophil', 'material properties', 'anatomy knowledge',
    'numeric filing', 'alphabetical filing', 'spatial perception', 'mechanical concepts',
    'mathematical concepts', 'mental arithmetic', 'auditory memory', 'working memory index',
    'iq', 'intelligence quotient', 'network basics', 'computer skills', 'cloud-backup',
    'public-transport', 'commute', 'local-food', 'vision-check', 'drug-use history', 'nationality'
]

SAFETY_HINTS = ['hostility', 'harm', 'hateful', 'violence', 'desperation', 'self-harm', 'risk', 'danger']
EMOTION_HINTS = ['emotion', 'sad', 'grief', 'fear', 'anger', 'joy', 'contentment', 'compassion', 'empathy', 'affect']
LINGUISTIC_HINTS = ['language', 'brevity', 'sentence', 'spelling', 'grammar', 'storytelling', 'clarity']
PRAGMATIC_HINTS = ['listening', 'relationship', 'social desirability', 'communication', 'interaction', 'collaboration', 'feedback', 'assertiveness', 'warmth']
CLINICAL_HINTS = ['depression', 'anxiety', 'burnout', 'hypomania', 'hysteria', 'psychotic', 'disorder']
MORAL_HINTS = ['honesty', 'justice', 'ethic', 'integrity', 'dignity', 'fairness', 'decency']


def clean_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r'^\d+\.\s*', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.rstrip(':').strip()


def infer_category(name: str) -> str:
    n = name.lower()
    if any(term in n for term in BLOCKLIST):
        return 'other'
    if any(k in n for k in SAFETY_HINTS):
        return 'safety'
    if any(k in n for k in EMOTION_HINTS):
        return 'emotion'
    if any(k in n for k in LINGUISTIC_HINTS):
        return 'linguistic'
    if any(k in n for k in PRAGMATIC_HINTS):
        return 'pragmatic'
    if any(k in n for k in CLINICAL_HINTS):
        return 'clinical'
    if any(k in n for k in MORAL_HINTS):
        return 'moral'
    if any(k in n for k in ['social', 'affiliation', 'peer', 'community', 'eye contact', 'relationship building']):
        return 'social'
    if any(k in n for k in ['helpfulness', 'patience', 'adaptability', 'initiative', 'perseverance', 'compromise']):
        return 'behavioral'
    return 'behavioral'


def scoring_direction(name: str) -> str:
    n = name.lower()
    lower_is_better = [
        'hostility', 'harm', 'desperation', 'hateful', 'disrespect', 'dishonesty', 'coarseness',
        'slothfulness', 'burnout', 'inattentiveness', 'withdrawn', 'passive-aggressive', 'impulsivity',
        'depression', 'anxiety', 'psychotic', 'hysteria', 'discontentment', 'moroseness', 'irritability'
    ]
    if any(k in n for k in lower_is_better):
        return 'lower_is_better'
    return 'higher_is_better'


def is_observable(name: str) -> bool:
    return True


def applicability(name: str, category: str) -> str:
    n = name.lower()
    if category == 'other':
        return 'both'
    if category in {'clinical', 'emotion', 'safety'} and any(
        k in n for k in ['empathy', 'compassion', 'warmth', 'listening', 'helpfulness', 'patience']
    ):
        return 'assistant'
    if category in {'clinical', 'emotion', 'safety'} and any(
        k in n for k in ['depression', 'burnout', 'desperation', 'grief', 'fear', 'anger', 'hostility']
    ):
        return 'user'
    return 'both'


def score_description(direction: str, bucket: int) -> str:
    high = {
        1: 'No evidence in the turn.',
        2: 'Weak or ambiguous signal.',
        3: 'Moderate evidence in the text.',
        4: 'Clear evidence in the text.',
        5: 'Strong and repeated evidence in the text.'
    }
    low = {
        1: 'Absent; no negative evidence in the turn.',
        2: 'Very low negative evidence.',
        3: 'Moderate negative evidence.',
        4: 'Clear negative evidence.',
        5: 'Strong and dominant negative evidence.'
    }
    return low[bucket] if direction == 'lower_is_better' else high[bucket]


def main():
    df = pd.read_csv(RAW_PATH)
    df['facet_name'] = df['Facets'].apply(clean_name)
    df = df[df['facet_name'].ne('')].copy()
    df['facet_name_norm'] = df['facet_name'].str.lower()
    df = df.drop_duplicates(subset=['facet_name_norm']).reset_index(drop=True)

    df['category'] = df['facet_name'].apply(infer_category)
    df['observable_from_text'] = df['facet_name'].apply(is_observable)
    df = df[df['category'].isin(PRIMARY_ALLOWED)].copy()

    target_keywords = (
        'hostility|harm|empathy|compassion|emotion|grief|sad|anger|fear|contentment|joy|affect|'
        'language|brevity|sentence|spelling|grammar|storytelling|clarity|listening|relationship|'
        'communication|feedback|assertiveness|warmth|social|collaboration|depression|anxiety|'
        'burnout|disrespect|dishonesty|justice|integrity|patience|helpfulness|adaptability|initiative'
    )
    preferred = df[df['facet_name_norm'].str.contains(target_keywords, regex=True, na=False)].copy()
    remaining = df[~df.index.isin(preferred.index)].copy()
    final = pd.concat([preferred, remaining], ignore_index=True).head(300).copy()

    final['facet_id'] = range(1, len(final) + 1)
    final['scoring_direction'] = final['facet_name'].apply(scoring_direction)
    final['score_scale'] = '-2,-1,0,1,2'
    final['score_min'] = -2
    final['score_max'] = 2
    final['rubric_score_-2'] = final['scoring_direction'].apply(lambda d: score_description(d, 1))
    final['rubric_score_-1'] = final['scoring_direction'].apply(lambda d: score_description(d, 2))
    final['rubric_score_0'] = final['scoring_direction'].apply(lambda d: score_description(d, 3))
    final['rubric_score_1'] = final['scoring_direction'].apply(lambda d: score_description(d, 4))
    final['rubric_score_2'] = final['scoring_direction'].apply(lambda d: score_description(d, 5))
    final['applicable_to'] = final.apply(lambda r: applicability(r['facet_name'], r['category']), axis=1)
    final['facet_group'] = final['category'].replace({'social': 'pragmatic', 'behavioral': 'pragmatic'})
    final['evidence_required'] = final['category'].apply(
        lambda c: 'text_only' if c != 'other' else 'weak_or_non_textual'
    )

    cols = [
        'facet_id', 'facet_name', 'category', 'facet_group', 'scoring_direction', 'score_scale',
        'score_min', 'score_max', 'rubric_score_-2', 'rubric_score_-1', 'rubric_score_0',
        'rubric_score_1', 'rubric_score_2', 'observable_from_text', 'applicable_to', 'evidence_required'
    ]
    final[cols].to_csv(OUT_PATH, index=False)
    print(f'Saved {len(final)} cleaned benchmark facets to {OUT_PATH}')
    print(final['category'].value_counts().to_string())


if __name__ == '__main__':
    main()