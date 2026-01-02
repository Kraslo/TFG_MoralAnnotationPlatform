import spacy
from moralstrength.moralstrength import word_moral_value

nlp = spacy.load("en_core_web_sm")

MORAL_FOUNDATIONS = ["care", "fairness", "loyalty", "authority", "purity"]

def detect_moral_polarity(text):
    """
    Analyzes a full article and returns, for each moral foundation:
    - polarity: virtue / vice / none
    - intensity: 0–1 scaled strength (absolute deviation from 5)
    - hits: number of lexicon words detected
    """
    doc = nlp(text)

    # Collect scores per foundation
    foundation_scores = {mf: [] for mf in MORAL_FOUNDATIONS}

    # Scan each word and extract lexicon score
    for token in doc:
        lemma = token.lemma_.lower()

        for mf in MORAL_FOUNDATIONS:
            score = word_moral_value(lemma, mf)
            if score != -1:  # valid lexicon word
                foundation_scores[mf].append(score)

    result = {}

    for mf in MORAL_FOUNDATIONS:
        scores = foundation_scores[mf]

        if not scores:
            result[mf] = {
                "polarity": "none",
                "intensity": 0.0,
                "hits": 0
            }
            continue

        avg_score = sum(scores) / len(scores)

        # Polarity determination
        if avg_score < 5:
            polarity = "vice"
        elif avg_score > 5:
            polarity = "virtue"
        else:
            polarity = "none"

        # Polarity intensity: how far from neutral 5
        intensity = abs(avg_score - 5) / 4   # scale to 0–1

        result[mf] = {
            "polarity": polarity,
            "intensity": round(intensity, 3),
            "hits": len(scores)
        }

    return result
