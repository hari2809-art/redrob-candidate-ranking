# scorers/education_scorer.py

def score_education(candidate):

    education = candidate.get("education", [])

    if not education:
        return 0.5

    best = 0.5

    tier_map = {
        "tier_1": 1.0,
        "tier_2": 0.8,
        "tier_3": 0.6,
        "tier_4": 0.5,
        "unknown": 0.5
    }

    for edu in education:

        tier = edu.get("tier", "unknown")

        best = max(
            best,
            tier_map.get(tier, 0.5)
        )

    return best