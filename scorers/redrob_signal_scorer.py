def score_redrob_signals(candidate):

    signals = candidate.get("redrob_signals", {})

    score = 0.0

    score += (
        signals.get(
            "profile_completeness_score",
            0
        ) / 100
    ) * 0.20

    score += (
        signals.get(
            "recruiter_response_rate",
            0
        )
    ) * 0.20

    score += (
        signals.get(
            "interview_completion_rate",
            0
        )
    ) * 0.20

    score += min(
        signals.get(
            "saved_by_recruiters_30d",
            0
        ) / 20,
        1
    ) * 0.15

    score += min(
        signals.get(
            "search_appearance_30d",
            0
        ) / 100,
        1
    ) * 0.10

    github = signals.get(
        "github_activity_score",
        -1
    )

    if github > 0:
        score += (
            github / 100
        ) * 0.15

    return min(score, 1.0)