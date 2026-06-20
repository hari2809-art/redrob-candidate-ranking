# jd_red_flags.py
"""
JD explicitly calls out two "trap" patterns it built into the dataset:

1. Framework enthusiasts — "AI experience" that's primarily recent
   (<12 months) LangChain/OpenAI projects, with no pre-LLM-era
   production ML experience. The JD says these should NOT move forward
   unless they show substantial pre-LLM ML production work.

2. Title-chasers — career trajectory shows Senior -> Staff -> Principal
   escalation via frequent company switches (~every 1.5 years or less).
   JD wants someone who'll stay 3+ years.

Returns a penalty (0.0 - 0.30) to subtract from the final score.
"""

from __future__ import annotations
from datetime import datetime

FRAMEWORK_KEYWORDS = [
    "langchain", "llamaindex", "llama index", "openai api", "gpt-3",
    "gpt-4", "chatgpt", "prompt engineering", "autogpt",
]

PRE_LLM_ML_KEYWORDS = [
    "model", "pipeline", "deployed", "production", "classification",
    "regression", "ranking", "recommendation", "feature engineering",
    "training", "xgboost", "lightgbm", "embedding", "retrieval",
    "search", "nlp", "deep learning", "neural network",
]

TITLE_RANK = {
    "intern": 0, "junior": 0, "associate": 0,
    "engineer": 1, "scientist": 1, "analyst": 1,
    "senior": 2,
    "staff": 3, "lead": 3, "principal": 4,
    "director": 4, "vp": 4, "head": 4, "chief": 5,
}


def _title_rank(title: str) -> int:
    title_l = title.lower()
    best = 1  # default mid-level
    for kw, rank in TITLE_RANK.items():
        if kw in title_l:
            best = max(best, rank)
    return best


def _parse_date(s: str | None):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


def _is_framework_enthusiast(candidate: dict) -> bool:
    """
    Three patterns:

    (a) Career description: recent role (<12mo) heavy on LangChain/OpenAI
        language, no older role with pre-LLM ML production signal.

    (b) Skills list: dominated by shallow-duration framework skills with
        no offsetting solid ML/retrieval skill.

    (c) Headline/summary: non-engineering title + "AI enthusiast" /
        "Building with LLMs" / "Generative AI explorer" language in
        headline or summary — the most common pattern in this dataset
        (5,739 candidates). These are professionals from unrelated fields
        who have recently started exploring LLMs without production ML
        background.
    """
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    profile = candidate.get("profile", {})

    # --- Check (a): recent-role description pattern ---
    if career:
        recent = career[0]
        recent_desc = recent.get("description", "").lower()
        is_recent_short = recent.get("duration_months", 999) < 12
        recent_is_framework_heavy = sum(
            1 for kw in FRAMEWORK_KEYWORDS if kw in recent_desc
        ) >= 2

        if is_recent_short and recent_is_framework_heavy:
            older_text = " ".join(r.get("description", "") for r in career[1:]).lower()
            if not any(kw in older_text for kw in PRE_LLM_ML_KEYWORDS):
                return True

    # --- Check (b): skills-list pattern ---
    framework_skill_names = {
        "langchain", "llamaindex", "llama index",
        "prompt engineering", "autogpt",
    }
    framework_skills = [
        s for s in skills
        if s.get("name", "").lower() in framework_skill_names
    ]
    other_skills = [s for s in skills if s not in framework_skills]

    if framework_skills:
        avg_fw_duration = sum(
            s.get("duration_months", 0) for s in framework_skills
        ) / len(framework_skills)
        if avg_fw_duration <= 12 and len(framework_skills) >= len(skills) * 0.4:
            has_solid_other = any(
                s.get("duration_months", 0) >= 24
                and any(kw in s.get("name", "").lower() for kw in PRE_LLM_ML_KEYWORDS)
                for s in other_skills
            )
            if not has_solid_other:
                return True

    # --- Check (c): non-engineering title + AI-enthusiast headline/summary ---
    # Target: ~5,739 candidates with non-ML titles + "AI enthusiast" language.
    # Must be strict to avoid flagging real engineers who mention LangChain
    # as one tool among many in a genuine ML career.
    NON_ENGINEERING_TITLES = {
        "project manager", "operations manager", "graphic designer",
        "mechanical engineer", "civil engineer", "marketing",
        "hr", "human resources", "accountant", "sales", "recruiter",
        "content writer", "business analyst", "product manager",
        "finance", "legal", "supply chain",
    }
    ENTHUSIAST_PHRASES = [
        "ai enthusiast", "building with llms", "generative ai explorer",
        "exploring ai", "exploring genai", "llm enthusiast",
        "learning ai", "chatgpt enthusiast",
    ]

    current_title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    summary = profile.get("summary", "").lower()
    combined_text = headline + " " + summary

    is_non_engineering = any(t in current_title for t in NON_ENGINEERING_TITLES)
    # Require 2+ enthusiast phrases to avoid false positives on real engineers
    enthusiast_hit_count = sum(1 for p in ENTHUSIAST_PHRASES if p in combined_text)
    is_enthusiast = enthusiast_hit_count >= 2

    # OR: 1 phrase but the title is clearly non-technical
    CLEARLY_NON_TECHNICAL = {
        "graphic designer", "accountant", "hr", "human resources",
        "recruiter", "content writer", "sales", "marketing",
        "civil engineer", "mechanical engineer",
    }
    is_clearly_non_technical = any(t in current_title for t in CLEARLY_NON_TECHNICAL)
    is_enthusiast = is_enthusiast or (is_clearly_non_technical and enthusiast_hit_count >= 1)

    if is_non_engineering and is_enthusiast:
        # Final gate: do they have genuine ML production background?
        all_career_text = " ".join(
            r.get("description", "") for r in career
        ).lower()
        # Require 4+ production ML signals to pass (not just 3) — be conservative
        has_real_ml = sum(
            1 for kw in PRE_LLM_ML_KEYWORDS if kw in all_career_text
        ) >= 4
        if not has_real_ml:
            return True

    return False


def _is_title_chaser(candidate: dict) -> bool:
    """
    >=2 roles, each <=18 months, with strictly increasing title rank
    (junior -> senior -> staff -> principal pattern via job-hopping).
    """
    career = candidate.get("career_history", [])
    if len(career) < 2:
        return False

    # career_history[0] = most recent. Reverse to chronological order.
    chrono = list(reversed(career))

    short_tenure_count = sum(1 for r in chrono if r.get("duration_months", 999) <= 18)
    if short_tenure_count < 2:
        return False

    ranks = [_title_rank(r.get("title", "")) for r in chrono]

    # Check for a strictly increasing run of length >= 2, where both
    # roles in the run are short-tenure
    max_run = 1
    for i in range(1, len(ranks)):
        if (
            ranks[i] > ranks[i - 1]
            and chrono[i].get("duration_months", 999) <= 18
            and chrono[i - 1].get("duration_months", 999) <= 18
        ):
            max_run = max(max_run, 2)

    return max_run >= 2


def red_flag_penalty(candidate: dict) -> tuple[float, list[str]]:
    """
    Returns (penalty 0.0-0.30, list of triggered flag names for reasoning).
    """
    penalty = 0.0
    flags = []

    if _is_framework_enthusiast(candidate):
        penalty += 0.18
        flags.append("framework-enthusiast (recent LangChain/OpenAI-only, no pre-LLM ML)")

    if _is_title_chaser(candidate):
        penalty += 0.12
        flags.append("title-escalation via frequent job switches")

    return round(min(penalty, 0.30), 4), flags