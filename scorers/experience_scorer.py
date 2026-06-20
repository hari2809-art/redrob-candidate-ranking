# scorers/experience_scorer.py

def score_experience(candidate):

    yoe = candidate["profile"].get(
        "years_of_experience",
        0
    )

    if 5 <= yoe <= 9:
        return 1.0

    if 4 <= yoe < 5:
        return 0.8

    if 9 < yoe <= 11:
        return 0.8

    if 3 <= yoe < 4:
        return 0.5

    return 0.2