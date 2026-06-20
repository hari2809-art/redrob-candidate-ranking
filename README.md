# Redrob Candidate Ranking System

### India Runs Hackathon — Track 1 (Data & AI)
### Intelligent Candidate Discovery & Ranking — Senior AI Engineer @ Redrob AI

**Team NovaMind AI**
| Role | Name |
|---|---|
| Team Leader | Gurram Harinath |
| Member | Ponna Chaitanya |
| Member | Boggula Hrudayananda Reddy |

---

## Overview

This system ranks 100,000 candidate profiles to identify the top 100 best-fit
people for a Senior AI Engineer role at Redrob AI, a Series A AI-native
recruitment platform based in Pune/Noida.

The job description is deliberately written without a fixed checklist. It
explicitly states that the "right answer" is **not** "find candidates whose
skills section contains the most AI keywords" — that is a trap built into
the dataset. Instead, the brief asks for a system that understands the gap
between what a job description says and what it actually means. A candidate
who has shipped a recommendation system at a product company is a genuine
fit even if their skills list never says "RAG" or "Pinecone." A candidate
whose title is "Marketing Manager" is not a fit, no matter how many AI
keywords appear on their profile.

This system is built around that principle: multiple rule-based signals
that understand career trajectory and role fit, combined with a semantic
(embedding-based) layer that captures meaning beyond exact keywords, plus
explicit detectors for each trap pattern the job description describes.

---

## Architecture: Two-Stage Pipeline

Given the constraints — 100,000 candidates, CPU only, a 5-minute time
limit, 16 GB RAM — running a transformer embedding model on every candidate
is too slow (an early, unoptimized attempt projected 4+ hours). The system
instead uses a two-stage "retrieve then rerank" architecture, the same
pattern used in production search and recommendation systems, which is
exactly the kind of system the job description describes wanting someone
to build.

```
                    ┌─────────────────────────────┐
                    │   100,000 candidates          │
                    │   (candidates.jsonl)          │
                    └───────────────┬───────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  STAGE 1: Rule-based scoring      │
                    │  (ALL 100,000 candidates, ~15s)   │
                    │                                    │
                    │  • Title & role fit                │
                    │  • Skills match (synonym-aware)    │
                    │  • Experience profile              │
                    │  • Location fit                    │
                    │  • Education tier                  │
                    │  • Redrob platform signals          │
                    │  • Honeypot detection               │
                    │  • Red-flag detection (JD traps)    │
                    └────────────────┬────────────────┘
                                     │
                          Top 10,000 by Stage 1 score
                                     │
                    ┌────────────────▼────────────────┐
                    │  STAGE 2: Semantic reranking      │
                    │  (Top 10,000 only, ~2.5–3 min)    │
                    │                                    │
                    │  BGE-small-en-v1.5 embeddings:    │
                    │  cosine similarity between JD     │
                    │  and candidate profile text       │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  Combine: weighted final score    │
                    │  × behavioral multiplier          │
                    │  − honeypot/red-flag penalties    │
                    └────────────────┬────────────────┘
                                     │
                              Sort, take top 100
                                     │
                    ┌────────────────▼────────────────┐
                    │  Generate per-candidate reasoning │
                    │  → output/submission.csv          │
                    └────────────────────────────────┘
```

**Why 10,000 and not 100,000 or 1,000?** Stage 1 already captures the major
JD signals — title, skills, experience, location — for every candidate. A
candidate who scores in the bottom 90% on Stage 1 (wrong title, no relevant
skills, wrong location) has no realistic path to the final top 100
regardless of semantic similarity. This was validated empirically: pool
sizes of 5,000, 10,000, and 15,000 were each tested end-to-end, and all
three produced an identical final top-100 list. 10,000 (10% of the dataset)
was selected as the configuration with the best safety margin under the
5-minute compute limit.

---

## Scoring Components

| Component | Weight | What it captures |
|---|---|---|
| **Semantic similarity (BGE)** | 0.30 | Embedding cosine similarity between the job description and the candidate's headline, summary, title, skills, and recent career descriptions. Catches meaning beyond exact keyword matches — for example, "built semantic search infrastructure from scratch" matches the JD even without the word "embeddings" appearing anywhere. |
| **Title & role fit** | 0.20 | Whether the current title and career trajectory reflect an AI/ML engineering role at a product company, with production-ML signal detection and a penalty for consulting-only careers. |
| **Skills match** | 0.15 | Synonym-aware matching against the JD's must-have skill groups (embeddings, vector databases, hybrid search, evaluation metrics, Python) and nice-to-have groups (LoRA/QLoRA, learning-to-rank, distributed systems). |
| **Experience profile** | 0.15 | Years of experience relative to the JD's 5–9 year band, with bonuses for product-company tenure and production-deployment signals, and penalties for consulting-heavy or research-only careers. |
| **Location fit** | 0.08 | Pune/Noida scored highest, followed by Hyderabad/Mumbai/Delhi NCR, then other Indian cities (relocation-aware), then international locations. |
| **Education** | 0.07 | Institution tier (as provided in the dataset) and field-of-study relevance. |
| **Redrob platform signals** | 0.05 | Profile completeness, recruiter response rate, interview completion rate, recruiter saves, GitHub activity. |

After the weighted sum, two adjustments are applied:

- **Behavioral multiplier (0.65×–1.0×)** — down-weights candidates based on
  recency of platform activity, open-to-work status, recruiter response
  rate, and notice period. This directly implements the JD's own
  instruction: *"a perfect-on-paper candidate who hasn't logged in for 6
  months and has a 5% recruiter response rate is, for hiring purposes, not
  actually available."*
- **Penalty subtraction** — a honeypot penalty (up to 0.10) and a red-flag
  penalty (up to 0.30) are subtracted directly from the final score.

---

## Trap Detection

The job description explicitly describes patterns built into the dataset
to filter out naive ranking approaches. Each has a dedicated detector.

### 1. Keyword stuffers — `scorers/title_scorer.py`
A candidate with "RAG, Pinecone, LLM" in their skills list but a title of
"Marketing Manager" or "HR Manager" receives a near-zero title score
regardless of their skill list. Title/role fit is weighted highest among
the rule-based components (0.20) specifically so this pattern cannot
dominate the ranking.

### 2. Honeypot profiles — `honeypot_detector.py`
Profiles with internally impossible data: expected salary with `min > max`,
total career-history duration far exceeding the stated years of
experience, multiple "expert" skills listed with 0 months duration, or a
single role lasting longer than the candidate's entire career.

**Result: 0 honeypot-flagged candidates in the final top 100** (the
submission spec's threshold is ≤10).

### 3. Framework enthusiasts — `jd_red_flags.py`
The JD states: *"If your 'AI experience' consists primarily of recent
(under 12 months) projects using LangChain to call OpenAI — we will
probably not move forward, unless you can demonstrate substantial
pre-LLM-era ML production experience."*

This detector checks three independent patterns: (a) a recent, short-tenure
role heavy on LangChain/OpenAI/prompt-engineering language with no older
role showing pre-LLM production ML signals; (b) a skills list dominated by
shallow-duration framework names with no offsetting solid ML/retrieval
skill; and (c) a non-engineering current title (e.g. Project Manager,
Graphic Designer, Operations Manager) combined with "AI enthusiast" /
"building with LLMs" language in the headline or summary and no genuine
production ML background. Pattern (c) was added after diagnosing that the
strongest version of this signal in the dataset lives in the
headline/summary fields rather than career-history text.

**Result: 4,051 candidates flagged dataset-wide; 0 reached the final top
100.**

### 4. Title-chasers — `jd_red_flags.py`
The JD states: *"If your career trajectory shows you optimizing for
'Senior' → 'Staff' → 'Principal' titles by switching companies every 1.5
years, we're not a fit."* Detected as two or more short-tenure (≤18 month)
roles with strictly increasing seniority.

**Result: 107 candidates flagged dataset-wide.**

### 5. Consulting-only careers, with the JD's explicit exception
The JD states that consulting-only careers (TCS, Infosys, Wipro, etc.) are
a mismatch *unless* the candidate is currently at one of these firms but
has prior product-company experience. The detector in
`scorers/experience_scorer.py` checks whether **all** career history is
consulting; if even one role is at a product company, no penalty is
applied — matching the JD's stated exception precisely.

---

## Reasoning Generation — `reasoning_generator.py`

Each of the top 100 candidates receives a reasoning string built entirely
from real profile fields, with no fabricated claims. Each reasoning string:

- Cites specific facts: years of experience, current title and company,
  location, and the candidate's actual JD-relevant skills, prioritized by
  must-have vs. nice-to-have and then by proficiency and duration
- Connects explicitly to the JD (for example, "matching the JD's preferred
  Pune/Noida hub")
- Surfaces one honest concern when present — a detected red flag, thin
  skill overlap, a consulting-heavy history, a long notice period, a low
  recruiter response rate, not-open-to-work status, missing production
  signals, experience outside the 5–9 year band, or a non-India location
  (the JD notes no visa sponsorship for international candidates)
- Varies sentence structure across rank tiers (1–10, 11–40, 41–75, 76–100)
  so the reasoning does not read as templated when sampled
- For lower-ranked candidates with genuinely strong skills, attributes the
  rank to availability or behavioral factors rather than mischaracterizing
  strong skills as weak, keeping the tone of the reasoning consistent with
  the actual driver of the score

---

## How to Run

```bash
pip install -r requirements.txt
python rank.py
```

This produces `output/submission.csv` (candidate_id, rank, score,
reasoning) in approximately 2.5–3 minutes on a standard CPU.

To validate the output format:

```bash
python data/validate_submission.py output/submission.csv
```

To run sanity checks (honeypot count, score distribution, location/title
diversity, reasoning variation):

```bash
python health_check.py
```

---

## Results Summary

- **0** honeypot-flagged candidates in the final top 100 (threshold: ≤10)
- **0** duplicate reasoning strings across the top 100
- Score range: approximately 0.97–1.16, smoothly non-increasing by rank
- The top 100 spans 19 distinct titles and 25+ distinct cities, concentrated
  around the JD's preferred Pune/Noida/Delhi NCR hub as expected, while
  still including relocation-eligible candidates from other Indian cities
- **4,158** total red-flag detections dataset-wide (4,051 framework
  enthusiasts, 107 title-chasers), with 0 reaching the final top 100
- Total runtime: approximately 2.5–3 minutes, comfortably within the
  5-minute compute limit

---

## Project Structure

```
india-runs-ai-challenge/
├── data/
│   ├── candidates.jsonl
│   └── validate_submission.py
├── output/
│   └── submission.csv
├── scorers/
│   ├── title_scorer.py
│   ├── skill_scorer.py
│   ├── experience_scorer.py
│   ├── location_scorer.py
│   ├── education_scorer.py
│   ├── redrob_signal_scorer.py
│   ├── behavioral_multiplier.py
│   └── semantic_scorer.py
├── honeypot_detector.py
├── jd_red_flags.py
├── reasoning_generator.py
├── health_check.py
├── rank.py
├── requirements.txt
└── README.md
```

---

## Design Decisions & Future Work

- **Hand-tuned weights.** Component weights reflect the emphasis the JD
  places on each requirement (production embeddings/retrieval experience is
  listed first and most strongly under "things you absolutely need") rather
  than being learned from labeled data. With ground-truth relevance
  judgments, a learning-to-rank model — for example, LightGBM trained with
  an NDCG objective — could replace the hand-tuned weighted sum. This was
  not pursued because no labeled relevance data was available for this
  challenge.
- **Semantic pool size.** Resolved during development: pool sizes of 5,000,
  10,000, and 15,000 were each tested end-to-end and produced identical
  top-100 results, confirming 10,000 as a safe and sufficient configuration.
- **JD text for the semantic scorer.** Resolved during development: the
  embedding text was updated from an initial paraphrase to language drawn
  directly from the actual job description, deliberately excluding "do not
  want" language to avoid inflating similarity scores for candidates who
  match the JD's own red-flag descriptions.
- **Framework-enthusiast detector.** Resolved during development: the
  initial implementation, which checked only career-history descriptions,
  flagged 0 candidates. Diagnosis showed the strongest signal for this
  pattern lives in the `headline` and `summary` fields. The detector was
  extended to three independent patterns and now flags 4,051 candidates
  dataset-wide, with confirmation that none reach the final top 100.
