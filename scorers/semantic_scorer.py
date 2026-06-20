# scorers/semantic_scorer.py
"""
Semantic similarity scorer using BGE embeddings.

Computes cosine similarity between the job description and a
candidate's combined profile text (headline + summary + title +
skills + career descriptions). Catches semantic matches that
keyword-based scorers miss — e.g. "Approximate Nearest Neighbor
Search" or "Dense Passage Retrieval" mapping to "vector retrieval".

The model and JD embedding are loaded ONCE at module import time.
Use score_semantic_batch() for the full 100K run — it's far faster
than calling score_semantic() in a loop.
"""

from __future__ import annotations

# Force PyTorch backend (avoid slow/unused TensorFlow code paths being
# imported alongside sentence-transformers, which adds overhead).
import os
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Use all available CPU cores for encoding
torch.set_num_threads(os.cpu_count())

# Load model once (module-level — happens on first import)
_MODEL = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")

# Cap sequence length — biggest speed lever on CPU.
_MODEL.max_seq_length = 96

# JD text — concise summary of the Senior AI Engineer @ Redrob role.
# Replace with the exact text from job_description.docx for best results.
JD_TEXT = """
Senior AI Engineer, founding AI engineering team at Redrob AI, a Series A
AI-native talent intelligence platform. Owns the intelligence layer:
ranking, retrieval, and matching systems deciding what recruiters and
candidates see.

Must have: production experience with embeddings-based retrieval systems
(sentence-transformers, OpenAI embeddings, BGE, E5) deployed to real users,
including embedding drift, index refresh, and retrieval-quality regression.
Production experience with vector databases or hybrid search infrastructure
(Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS).
Strong Python and code quality. Hands-on experience designing evaluation
frameworks for ranking systems: NDCG, MRR, MAP, offline-to-online
correlation, A/B test interpretation.

Ideal background: 6-8 years total experience, 4-5 years in applied ML/AI
roles at product companies, not pure services. Has shipped at least one
end-to-end ranking, search, or recommendation system to real users at
meaningful scale. Strong opinions on hybrid vs dense retrieval, offline vs
online evaluation, and when to fine-tune vs prompt an LLM, grounded in
systems actually built.

Nice to have: LLM fine-tuning with LoRA, QLoRA, or PEFT. Learning-to-rank
models, XGBoost-based or neural. Prior exposure to HR-tech, recruiting tech,
or marketplace products. Distributed systems or large-scale inference
optimization. Open-source contributions in AI/ML.

Location: Pune or Noida, India, hybrid, or willing to relocate from
Hyderabad, Mumbai, or Delhi NCR. Sub-30-day notice period preferred.
""".strip()

# Pre-compute JD embedding once
_JD_EMBEDDING = _MODEL.encode([JD_TEXT], normalize_embeddings=True)

# Rescaling bounds for BGE cosine similarity -> 0-1 score.
# Tune these after inspecting real score distributions on your data
# (print min/max/mean of raw cosine sims over a sample of 1000).
_SIM_LOW, _SIM_HIGH = 0.30, 0.80


def _build_candidate_text(candidate: dict) -> str:
    profile = candidate.get("profile", {})
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])

    skill_text = ", ".join(s.get("name", "") for s in skills)

    # Only use the most recent 1-2 roles' descriptions, truncated.
    # Full career history across many roles is unnecessary for semantic
    # matching and is the main cause of slow encoding on CPU.
    career_text = " ".join(
        c.get("description", "")[:200] for c in career[:2]
    )

    parts = [
        profile.get("headline", "")[:200],
        profile.get("summary", "")[:300],
        profile.get("current_title", ""),
        skill_text[:300],
        career_text,
    ]
    text = " ".join(p for p in parts if p)
    # Hard cap overall text length (characters) as a final safety net
    return text[:1000]


def score_semantic(candidate: dict) -> float:
    """Single-candidate version — convenient but slow for 100K rows."""
    text = _build_candidate_text(candidate)
    if not text.strip():
        return 0.0

    emb = _MODEL.encode([text], normalize_embeddings=True)
    sim = float(cosine_similarity(_JD_EMBEDDING, emb)[0][0])
    rescaled = (sim - _SIM_LOW) / (_SIM_HIGH - _SIM_LOW)
    return float(np.clip(rescaled, 0.0, 1.0))


def score_semantic_batch(candidates: list[dict]) -> list[float]:
    """
    Batched version — MUCH faster for 100K candidates.
    Encodes all candidate texts in one call with batching.
    """
    texts = [_build_candidate_text(c) for c in candidates]
    embs = _MODEL.encode(
        texts,
        normalize_embeddings=True,
        batch_size=256,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    sims = cosine_similarity(_JD_EMBEDDING, embs)[0]
    rescaled = np.clip((sims - _SIM_LOW) / (_SIM_HIGH - _SIM_LOW), 0.0, 1.0)
    return rescaled.tolist()