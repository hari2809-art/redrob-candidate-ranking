# honeypot_detector.py

def honeypot_penalty(candidate):

    penalty = 0

    total_exp = (
        candidate["profile"]
        .get("years_of_experience", 0)
    )

    # impossible role duration
    for role in candidate.get(
        "career_history",
        []
    ):

        duration = role.get(
            "duration_months",
            0
        )

        if duration > (total_exp * 12) + 6:
            penalty += 1

    # fake expert skills

    expert_zero = 0

    for skill in candidate.get(
        "skills",
        []
    ):

        if (
            skill.get("proficiency")
            == "expert"
            and
            skill.get("duration_months", 0)
            == 0
        ):
            expert_zero += 1

    if expert_zero >= 3:
        penalty += expert_zero

    # too many jobs for too little experience

    if (
        total_exp < 2
        and
        len(candidate.get(
            "career_history",
            []
        )) > 5
    ):
        penalty += 1

    return penalty