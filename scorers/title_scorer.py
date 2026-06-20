# scorers/title_scorer.py

AI_TITLES = {
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "research engineer",
    "software engineer",
    "backend engineer",
    "data engineer",
    "nlp engineer",
    "applied scientist"
}

BAD_TITLES = {
    "marketing",
    "accountant",
    "hr",
    "operations",
    "customer support",
    "civil engineer",
    "mechanical engineer",
    "business analyst",
    "sales"
}

CONSULTING_COMPANIES = {
    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "accenture",
    "capgemini",
    "mindtree"
}


def score_title(candidate):

    current_title = (
        candidate["profile"]
        .get("current_title", "")
        .lower()
    )

    for bad in BAD_TITLES:
        if bad in current_title:
            return 0.0

    score = 0.0

    for title in AI_TITLES:
        if title in current_title:
            score += 1.0
            break

    for role in candidate.get("career_history", []):

        company = role.get("company", "").lower()

        if company not in CONSULTING_COMPANIES:

            desc = role.get("description", "").lower()

            if (
                "machine learning" in desc
                or "model" in desc
                or "deployed" in desc
                or "production" in desc
                or "nlp" in desc
            ):
                score += 0.5
                break

    return min(score, 1.5)