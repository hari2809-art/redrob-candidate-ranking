import json
import csv
import time

from scorers.title_scorer import score_title
from scorers.skill_scorer import score_skills
from scorers.experience_scorer import score_experience
from scorers.location_scorer import score_location
from scorers.education_scorer import score_education
from scorers.behavioral_multiplier import behavioral_multiplier
from scorers.redrob_signal_scorer import score_redrob_signals
from scorers.semantic_scorer import score_semantic_batch

from honeypot_detector import honeypot_penalty
from jd_red_flags import red_flag_penalty
from reasoning_generator import generate_reasoning


# ── Weights (sum to 1.0) ──────────────────────────────────────────────────
WEIGHTS = {
    "semantic":   0.30,
    "title":      0.20,
    "skills":     0.15,
    "experience": 0.15,
    "location":   0.08,
    "education":  0.07,
    "redrob":     0.05,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "weights must sum to 1.0"

# How many top candidates (by rule-based score) get the expensive
# semantic pass. Linear scaling observed: ~17.8s per 1000 candidates.
# 10000 -> ~195s semantic + ~17s rules = ~215s total, safe margin
# under the 5-minute limit. 15000 (~285s total) was too close to the edge.
SEMANTIC_POOL_SIZE = 10000

# Neutral semantic score for candidates outside the pool (won't matter
# for ranking since they're far from top 100 on rule-based alone).
DEFAULT_SEMANTIC_SCORE = 0.5


def rule_score(candidate):
    title = min(score_title(candidate), 1.0)
    skills = score_skills(candidate)
    experience = score_experience(candidate)
    location = score_location(candidate)
    education = score_education(candidate)
    redrob = score_redrob_signals(candidate)
    return {
        "title": title, "skills": skills, "experience": experience,
        "location": location, "education": education, "redrob": redrob,
    }


def combine_score(candidate, components, semantic_score):
    score = (
        WEIGHTS["semantic"]   * semantic_score +
        WEIGHTS["title"]      * components["title"] +
        WEIGHTS["skills"]     * components["skills"] +
        WEIGHTS["experience"] * components["experience"] +
        WEIGHTS["location"]   * components["location"] +
        WEIGHTS["education"]  * components["education"] +
        WEIGHTS["redrob"]     * components["redrob"]
    )
    score *= behavioral_multiplier(candidate)
    score -= honeypot_penalty(candidate) * 0.10

    flag_penalty, _ = red_flag_penalty(candidate)
    score -= flag_penalty

    return round(max(score, 0.0), 4)


print("Loading candidates...")
candidates = []
with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        candidates.append(json.loads(line))
print(f"Loaded {len(candidates)} candidates")

# ── Pass 1: cheap rule-based components for everyone ─────────────────────
print("Pass 1: rule-based scoring (all candidates)...")
t0 = time.time()
rule_components = [rule_score(c) for c in candidates]
print(f"  done in {time.time() - t0:.1f}s")

# Pre-rank using rule-based score with a neutral semantic placeholder,
# to decide who gets the expensive semantic pass.
print("Selecting semantic pool...")
prelim_scores = [
    combine_score(c, comp, DEFAULT_SEMANTIC_SCORE)
    for c, comp in zip(candidates, rule_components)
]
ranked_idx = sorted(
    range(len(candidates)),
    key=lambda i: (-prelim_scores[i], candidates[i]["candidate_id"]),
)
pool_idx = set(ranked_idx[:SEMANTIC_POOL_SIZE])
print(f"  pool size: {len(pool_idx)}")

# ── Pass 2: semantic scoring, only for the pool ───────────────────────────
print(f"Pass 2: semantic similarity (BGE) on {SEMANTIC_POOL_SIZE} candidates...")
t0 = time.time()
pool_candidates = [candidates[i] for i in ranked_idx[:SEMANTIC_POOL_SIZE]]
pool_semantic = score_semantic_batch(pool_candidates)
print(f"  done in {time.time() - t0:.1f}s")

semantic_scores = [DEFAULT_SEMANTIC_SCORE] * len(candidates)
for pool_pos, i in enumerate(ranked_idx[:SEMANTIC_POOL_SIZE]):
    semantic_scores[i] = pool_semantic[pool_pos]

# ── Final combine for everyone ────────────────────────────────────────────
print("Combining final scores...")
all_candidates = []
for i, candidate in enumerate(candidates):
    score = combine_score(candidate, rule_components[i], semantic_scores[i])
    all_candidates.append((candidate, score))

all_candidates.sort(key=lambda x: (-x[1], x[0]["candidate_id"]))
top100 = all_candidates[:100]

with open("output/submission.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])

    prev_score = None
    for rank, (candidate, score) in enumerate(top100, start=1):
        if prev_score is not None and score > prev_score:
            score = prev_score
        prev_score = score

        writer.writerow([
            candidate["candidate_id"],
            rank,
            score,
            generate_reasoning(candidate, rank),
        ])

print("Saved: output/submission.csv")
print(f"Total submitted candidates: {len(top100)}")