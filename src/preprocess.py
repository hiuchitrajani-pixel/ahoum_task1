import pandas as pd
import re
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_raw.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'facets_cleaned.csv')


def clean_name(name):
    name = str(name).strip()
    name = re.sub(r'^\d+\.\s*', '', name)
    name = name.rstrip(':').strip()
    return name


def get_category(name):
    n = name.lower()

    if any(k in n for k in ['spiritual', 'sufi', 'quran', 'yoga', 'meditation', 'prayer',
                            'holiness', 'sacred', 'sikh', 'buddhist', 'islamic', 'hindu',
                            'jewish', 'gnostic', 'kabbalah', 'ching', 'astrology', 'aura',
                            'ego dissolution', 'satya', 'pilgrimage', 'reiki', 'vrata',
                            'bhagavad', 'kirtan', 'dhikr']):
        return 'spiritual'

    if any(k in n for k in ['serotonin', 'hormone', 'basophil', 'chromatin', 'immune',
                            'metabolic', 'polygenic', 'caffeine sensitivity', 'sleep apnea',
                            'parathyroid', 'fsh', 'chronic pain']):
        return 'physiological'

    if any(k in n for k in ['depression', 'anxiety', 'burnout', 'hypomania', 'hysteria',
                            'psychoticism', 'disorder']):
        return 'clinical'

    if any(k in n for k in ['leadership', 'delegation', 'collaboration', 'teamwork',
                            'feedback', 'ethical leadership']):
        return 'professional'

    if any(k in n for k in ['happiness', 'joy', 'sadness', 'anger', 'fear', 'emotion',
                            'mood', 'affect', 'contentment', 'bliss', 'desperation',
                            'grief', 'empathy', 'compassion']):
        return 'emotion'

    if any(k in n for k in ['memory', 'reasoning', 'intelligence', 'cognitive', 'attention',
                            'perception', 'spatial', 'numerical', 'iq', 'processing',
                            'analogy', 'logical']):
        return 'cognitive'

    if any(k in n for k in ['openness', 'conscientiousness', 'hexaco', 'big five',
                            'enneagram', 'mbti', 'judging', 'perceiving']):
        return 'personality'

    if any(k in n for k in ['diet', 'nutrition', 'macronutrient', 'eating', 'cooking',
                            'snack', 'breakfast', 'caffeine intake', 'sleep', 'exercise',
                            'dance', 'fitness', 'training', 'cardio']):
        return 'lifestyle'

    if any(k in n for k in ['social', 'relationship', 'communication', 'affiliation',
                            'interaction', 'cultural', 'community', 'peer', 'eye contact',
                            'listening']):
        return 'social'

    if any(k in n for k in ['moral', 'ethics', 'honesty', 'justice', 'integrity',
                            'dignity', 'fairness', 'virtue', 'decency']):
        return 'moral'

    if any(k in n for k in ['linguistic', 'language', 'brevity', 'sentence', 'storytelling',
                            'spelling', 'grammar']):
        return 'linguistic'

    return 'behavioral'


def get_scoring_direction(name):
    n = name.lower()

    negative = [
        'hostility', 'aggression', 'dishonesty', 'disrespect', 'burnout',
        'inefficiency', 'slothfulness', 'coarseness', 'hatefulness', 'acidity',
        'moroseness', 'immaturity', 'cunningness', 'impudence', 'passive-aggressive',
        'desperation', 'ethnocentrism', 'martyrdom', 'brazenness', 'compulsive',
        'sensationalism', 'cantankerousness', 'withdrawn', 'servility', 'naivety',
        'discontentment', 'drug-use'
    ]
    if any(k in n for k in negative):
        return 'lower_is_better'

    neutral = ['style', 'type', 'orientation', 'count', 'ratio', 'frequency', 'rate',
               'preference', 'index', 'hexagram', 'enneagram']
    if any(k in n for k in neutral):
        return 'neutral'

    return 'higher_is_better'


def can_score_from_text(name, category):
    if category == 'physiological':
        return False

    skip = ['passport', 'subscription', 'museum', 'music-lessons', 'choir', 'blood',
            'hormone', 'gene', 'polygenic', 'chromatin', 'sleep apnea', 'commute',
            'digital-nomad', 'basophil', 'caffeine sensitivity']

    return not any(k in name.lower() for k in skip)


def main():
    df = pd.read_csv(RAW_PATH)

    df['facet_name'] = df['Facets'].apply(clean_name)
    df = df[df['facet_name'].str.strip() != ''].reset_index(drop=True)

    df['facet_id'] = range(1, len(df) + 1)
    df['category'] = df['facet_name'].apply(get_category)
    df['scoring_direction'] = df['facet_name'].apply(get_scoring_direction)
    df['score_scale'] = '1,2,3,4,5'
    df['score_min'] = 1
    df['score_max'] = 5

    rubric_low = {
        'higher_is_better': 'Completely absent; no evidence in the conversation.',
        'lower_is_better': 'Not present at all; no negative signals.',
        'neutral': 'Minimal / lowest observable level.'
    }

    rubric_high = {
        'higher_is_better': 'Strongly present; multiple clear signals in the text.',
        'lower_is_better': 'Dominant throughout the conversation turn.',
        'neutral': 'Clearly at the highest observable level.'
    }

    df['rubric_score_1'] = df['scoring_direction'].map(rubric_low)
    df['rubric_score_5'] = df['scoring_direction'].map(rubric_high)
    df['observable_from_text'] = df.apply(
        lambda r: can_score_from_text(r['facet_name'], r['category']), axis=1
    )
    df['applicable_to'] = df['category'].apply(
        lambda c: 'user' if c in ['physiological', 'lifestyle', 'spiritual'] else 'both'
    )

    final = df[['facet_id', 'facet_name', 'category', 'scoring_direction', 'score_scale',
                'score_min', 'score_max', 'rubric_score_1', 'rubric_score_5',
                'observable_from_text', 'applicable_to']]

    final.to_csv(OUT_PATH, index=False)
    print(f"Saved cleaned CSV to: {OUT_PATH}")
    print(final.head())


if __name__ == '__main__':
    main()