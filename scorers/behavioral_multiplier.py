def behavioral_multiplier(candidate):

    signals = candidate.get("redrob_signals", {})

    multiplier = 1.0

    if signals.get("open_to_work_flag", False):
        multiplier += 0.05

    if signals.get("verified_email", False):
        multiplier += 0.02

    if signals.get("verified_phone", False):
        multiplier += 0.02

    if signals.get("linkedin_connected", False):
        multiplier += 0.02

    response_rate = signals.get("recruiter_response_rate", 0)

    if response_rate > 0.5:
        multiplier += 0.05

    interview_rate = signals.get("interview_completion_rate", 0)

    if interview_rate > 0.7:
        multiplier += 0.05

    github_score = signals.get("github_activity_score", -1)

    if github_score > 50:
        multiplier += 0.05

    return multiplier