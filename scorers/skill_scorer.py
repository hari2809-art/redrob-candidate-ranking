# scorers/skill_scorer.py

# Each entry: canonical concept -> list of surface forms that should match
MUST_HAVE_GROUPS = {
    "python":               ["python"],
    "embeddings":           ["embeddings", "embedding", "sentence embedding",
                              "text embedding", "dense retrieval"],
    "sentence_transformers": ["sentence-transformers", "sentence transformers",
                              "sbert"],
    "bge_e5":               ["bge", "e5", "bge-small", "bge-large"],
    "vector_db":            ["pinecone", "qdrant", "weaviate", "faiss",
                              "milvus", "vector database", "vector store",
                              "vector search", "pgvector"],
    "search":               ["elasticsearch", "opensearch", "bm25",
                              "hybrid search", "sparse retrieval"],
    "eval_metrics":         ["ndcg", "mrr", "map", "precision@", "recall@"],
    "rag":                  ["rag", "retrieval augmented", "retrieval-augmented"],
}

NICE_TO_HAVE_GROUPS = {
    "fine_tuning":   ["lora", "qlora", "peft", "fine-tuning llms",
                      "fine-tuning", "fine tune", "rlhf"],
    "ltr":           ["xgboost", "lightgbm", "learning to rank", "ltr",
                      "lambdamart", "ranknet"],
    "distributed":   ["distributed systems", "spark", "ray", "kafka"],
    "ml_core":       ["pytorch", "tensorflow", "transformers",
                      "hugging face", "huggingface", "scikit-learn"],
    "nlp":           ["nlp", "natural language processing", "bert", "llm",
                      "large language model"],
    "ranking":       ["ranking", "reranking", "re-ranking", "recommendation",
                      "search relevance", "cross-encoder", "cross encoder"],
}

MUST_HAVE_SCORE = 0.08
NICE_TO_HAVE_SCORE = 0.04


def _match_any(text, surface_forms):
    return any(form in text for form in surface_forms)


def score_skills(candidate):

    skills = candidate.get("skills", [])

    score = 0.0
    matched_must_groups = set()
    matched_nice_groups = set()

    for skill in skills:
        name = skill.get("name", "").lower()

        for group, forms in MUST_HAVE_GROUPS.items():
            if group in matched_must_groups:
                continue
            if _match_any(name, forms):
                score += MUST_HAVE_SCORE
                matched_must_groups.add(group)

        for group, forms in NICE_TO_HAVE_GROUPS.items():
            if group in matched_nice_groups:
                continue
            if _match_any(name, forms):
                score += NICE_TO_HAVE_SCORE
                matched_nice_groups.add(group)

    # Also scan career-history descriptions for must-have concepts the
    # candidate may have used but not listed as a discrete "skill".
    # Half credit since this is a softer signal.
    career_text = " ".join(
        r.get("description", "") for r in candidate.get("career_history", [])
    ).lower()

    for group, forms in MUST_HAVE_GROUPS.items():
        if group in matched_must_groups:
            continue
        if _match_any(career_text, forms):
            score += MUST_HAVE_SCORE * 0.5
            matched_must_groups.add(group)

    return min(score, 1.0)