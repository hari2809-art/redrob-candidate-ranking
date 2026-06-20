"""
reasoning_generator.py

Generates per-candidate reasoning strings for the submission CSV.

Stage 4 manual review checks (from submission_spec):
  1. Specific facts (YOE, title, named skills, signal values)
  2. JD connection (not generic praise)
  3. Honest concerns (acknowledge gaps)
  4. No hallucination (only claims actually in profile)
  5. Variation (10 sampled rows must differ structurally)
  6. Rank consistency (tone matches rank)

This module builds each reasoning from real profile fields, varies
sentence structure based on rank tier, and always surfaces at least
one concern unless the candidate is genuinely clean.
"""

from jd_red_flags import red_flag_penalty

# JD-relevant skill keywords we look for to call out by name
JD_SKILL_KEYWORDS = [
    "embeddings", "sentence-transformers", "sentence transformers",
    "bge", "e5", "faiss", "pinecone", "qdrant", "weaviate", "milvus",
    "elasticsearch", "vector database", "hybrid search", "rag",
    "ndcg", "mrr", "map", "ranking", "retrieval", "reranking",
    "lora", "qlora", "fine-tuning llms", "fine-tuning", "xgboost",
    "pytorch", "transformers", "nlp", "llm",
]

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "mindtree", "tech mahindra",
}

PREFERRED_LOCATIONS = {"pune", "noida", "gurgaon", "gurugram", "delhi", "ncr"}


# Must-have skills get priority in reasoning over nice-to-have ones
# (mirrors the MUST_HAVE_GROUPS in skill_scorer.py)
MUST_HAVE_KEYWORDS = {
    "python", "embeddings", "embedding", "sentence-transformers",
    "sentence transformers", "sbert", "bge", "e5", "pinecone", "qdrant",
    "weaviate", "faiss", "milvus", "vector database", "vector store",
    "vector search", "elasticsearch", "hybrid search", "ndcg", "mrr",
    "map", "rag", "retrieval augmented", "information retrieval",
    "semantic search",
}

PROFICIENCY_ORDER = {"expert": 3, "advanced": 2, "intermediate": 1, "beginner": 0}


def _matched_skills(candidate: dict) -> list[str]:
    """
    Return JD-relevant skill names from this candidate's profile,
    ordered so must-have skills (embeddings/retrieval/vector DB/eval
    metrics) come before nice-to-haves, and within each tier the
    highest-proficiency / longest-duration skills come first.
    """
    skills = candidate.get("skills", [])
    must, nice = [], []

    for s in skills:
        name = s.get("name", "")
        name_l = name.lower()
        for kw in JD_SKILL_KEYWORDS:
            if kw in name_l or name_l in kw:
                rank_key = (
                    PROFICIENCY_ORDER.get(s.get("proficiency", ""), 0),
                    s.get("duration_months", 0),
                )
                if any(mh in name_l or name_l in mh for mh in MUST_HAVE_KEYWORDS):
                    must.append((rank_key, name))
                else:
                    nice.append((rank_key, name))
                break

    must.sort(key=lambda x: x[0], reverse=True)
    nice.sort(key=lambda x: x[0], reverse=True)

    ordered = [n for _, n in must] + [n for _, n in nice]
    return ordered


def _has_production_signal(candidate: dict) -> bool:
    text = " ".join(r.get("description", "") for r in candidate.get("career_history", [])).lower()
    return any(kw in text for kw in ["production", "deployed", "shipped", "real users", "scale"])


def _is_consulting_heavy(candidate: dict) -> bool:
    career = candidate.get("career_history", [])
    if not career:
        return False
    consulting = sum(1 for r in career if any(f in r.get("company", "").lower() for f in CONSULTING_FIRMS))
    return consulting / len(career) >= 0.5


def _identify_concern(candidate: dict, matched_skills: list[str]) -> str | None:
    """Return a single honest concern string, or None if profile is genuinely clean."""
    signals = candidate.get("redrob_signals", {})

    # Red flags (framework-enthusiast, title-chaser) are the JD's explicit
    # "traps" — surface these first if present.
    _, flags = red_flag_penalty(candidate)
    if flags:
        return flags[0]

    notice = signals.get("notice_period_days", 0)
    response_rate = signals.get("recruiter_response_rate", 0)
    open_to_work = signals.get("open_to_work_flag", True)

    if not matched_skills:
        return "no direct embeddings/retrieval skills listed on the profile, so fit is based on title and trajectory alone"

    if len(matched_skills) <= 2:
        return f"only {len(matched_skills)} JD-relevant skill(s) listed ({matched_skills[0]}), so retrieval-specific depth is unclear"

    if _is_consulting_heavy(candidate):
        return "most of the career history is at consulting/IT-services firms rather than product companies"

    if notice >= 90:
        return f"notice period is {notice} days, longer than ideal for an immediate hire"

    if response_rate < 0.15:
        return f"recruiter response rate is low ({response_rate:.0%}), so outreach may be slow"

    if not open_to_work:
        return "profile is not currently marked open to work"

    country = candidate["profile"].get("country", "").lower()
    if country and country not in ("india", "in"):
        location = candidate["profile"].get("location", "Unknown")
        return (
            f"based in {location} (outside India); JD treats non-India "
            f"candidates case-by-case with no visa sponsorship"
        )

    if not _has_production_signal(candidate):
        return "career descriptions don't explicitly mention production deployment of these systems"

    yoe = candidate["profile"].get("years_of_experience", 0)
    if yoe < 5:
        return f"at {yoe:.1f} yrs, slightly below the JD's 5-9 year target range"
    if yoe > 9:
        return f"at {yoe:.1f} yrs, somewhat above the JD's 5-9 year target range, though the JD says this isn't a hard cutoff"

    return None


def _article(word: str) -> str:
    return "an" if word and word[0].lower() in "aeiou" else "a"


def _location_phrase(candidate: dict) -> str:
    loc = candidate["profile"].get("location", "Unknown")
    loc_l = loc.lower()
    if any(p in loc_l for p in PREFERRED_LOCATIONS):
        return f"based in {loc}, matching the JD's preferred Pune/Noida hub"
    return f"based in {loc}"


def generate_reasoning(candidate: dict, rank: int) -> str:
    """
    Build a reasoning string for this candidate at this rank.
    Varies sentence structure by rank tier so 10 sampled rows differ.
    """
    profile = candidate["profile"]
    title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")

    matched = _matched_skills(candidate)
    concern = _identify_concern(candidate, matched)
    loc_phrase = _location_phrase(candidate)

    skills_phrase = (
        f"hands-on with {', '.join(matched[:3])}"
        if matched else "no JD-aligned retrieval skills surfaced"
    )

    # Vary sentence templates by rank tier so reviewers see real variation
    if rank <= 10:
        base = f"{title} ({yoe:.1f} yrs, currently at {company}) — {skills_phrase}; {loc_phrase}."
        if concern:
            base += f" Worth checking: {concern}."
        else:
            base += " Career history shows production ML work, strong overall fit."

    elif rank <= 40:
        base = f"{yoe:.1f} years as {_article(title)} {title}, {loc_phrase}. {skills_phrase.capitalize()}."
        if concern:
            base += f" Main gap: {concern}."

    elif rank <= 75:
        base = (
            f"{title} with {yoe:.1f} yrs — {skills_phrase}. "
            f"Included mainly on title/experience fit; {loc_phrase}."
        )
        if concern:
            base += f" {concern.capitalize()}."

    else:
        # Don't mischaracterize skills as "weak"/"adjacent" if the candidate
        # actually has solid JD-relevant skills — the low rank here is more
        # often driven by availability/behavioral signals than skill gaps.
        if matched:
            base = f"{title}, {yoe:.1f} yrs — {skills_phrase}. "
            if concern:
                base += f"{concern.capitalize()}, which is the main reason this candidate sits near the cutoff rather than higher."
            else:
                base += "Solid skill overlap, but overall score is lower than higher-ranked candidates on other factors (title fit, experience profile, or semantic match to the JD)."
        else:
            base = f"{title}, {yoe:.1f} yrs. {skills_phrase.capitalize()}. "
            if concern:
                base += f"{concern.capitalize()}, so ranked as filler near the cutoff."
            else:
                base += "Ranked low primarily due to weak JD-skill overlap compared to higher-ranked candidates."

    return base