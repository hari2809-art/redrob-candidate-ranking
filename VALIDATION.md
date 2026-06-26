# Manual Validation

## Overview

We manually reviewed the top 20 candidates from our final submission
against the JD criteria to verify the ranking reflects genuine recruiter
judgment — not just algorithmic score.

Each candidate was evaluated on four criteria drawn directly from the JD:
- **Role fit**: Is the title and career trajectory genuinely ML/AI engineering at a product company?
- **Skill depth**: Do the matched skills reflect real production experience, not just listed keywords?
- **Availability**: Is the candidate actually reachable (open to work, response rate, notice period)?
- **Location**: Does the candidate match the Pune/Noida preference or have a realistic relocation path?

Judgments: **STRONG FIT** / **ACCEPTABLE** / **BORDERLINE** / **WEAK**

---

## Results

| Rank | Candidate | Title & Company | Judgment | Key Reason |
|---|---|---|---|---|
| 1 | CAND_0018499 | Senior ML Engineer @ Zomato | **STRONG FIT** | Product company (Zomato, 5000+ scale), Noida (JD preferred), RAG+Weaviate+Pinecone, 4/7 production signals, 15-day notice |
| 2 | CAND_0077337 | Staff ML Engineer @ Paytm | **STRONG FIT** | Large fintech product company, 7 yrs, 6/7 production signals (highest in top 20), Semantic Search+RAG, 95% recruiter response |
| 3 | CAND_0046525 | Senior ML Engineer @ Genpact AI | **ACCEPTABLE** | Pune (ideal location), strong retrieval skills, but Genpact is services-adjacent and only 3/7 production signals |
| 4 | CAND_0002025 | Senior AI Engineer @ Apple | **STRONG FIT** | Elite product company, FAISS+Weaviate+Sentence Transformers, 5/7 production signals, 30-day notice, 80% response |
| 5 | CAND_0088025 | Staff ML Engineer @ Yellow.ai | **ACCEPTABLE** | AI-native company, strong LLM fine-tuning skills, but 8.6 yrs slightly over JD target and 90-day notice |
| 6 | CAND_0008425 | Senior NLP Engineer @ Ola | **ACCEPTABLE** | Product company (Ola), strong NLP+retrieval depth, 5/7 production signals, but 90-day notice and non-preferred location |
| 7 | CAND_0015578 | AI Engineer @ Zoho | **BORDERLINE** | Good skills listed, Delhi location, but only 1/7 production signals in career descriptions — weakest evidence of actual production ML work in top 10 |
| 8 | CAND_0071974 | Senior AI Engineer @ Netflix | **STRONG FIT** | Elite product company, 6/7 production signals, Weaviate+Qdrant+Pinecone, 7.8 yrs squarely in JD range |
| 9 | CAND_0086022 | Senior Applied Scientist @ Sarvam AI | **ACCEPTABLE** | AI-native startup, immediately available (0-day notice), strong embeddings/vector skills, slightly under 5-yr minimum at 5.3 yrs |
| 10 | CAND_0039383 | Applied ML Engineer @ Meesho | **ACCEPTABLE** | Strong e-commerce product company, Gurgaon (JD preferred area), 7.1 yrs, but 90-day notice is a concern |
| 11 | CAND_0081846 | Lead AI Engineer @ Razorpay | **ACCEPTABLE** | Strong fintech product company, solid retrieval skills, 4/7 production signals, 30-day notice |
| 12 | CAND_0006567 | Senior AI Engineer @ Meta | **BORDERLINE** | Elite company and Noida location are positives, but only 2 JD-relevant skills matched and 2/7 production signals — skill depth in retrieval/ranking is unclear |
| 13 | CAND_0079387 | AI Engineer @ Microsoft | **ACCEPTABLE** | Large product company, 6.9 yrs, Sentence Transformers+LoRA+QLoRA, 4/7 production signals, 30-day notice |
| 14 | CAND_0099806 | AI Engineer @ Mad Street Den | **BORDERLINE** | AI-native company, relevant skills, but 4.6 yrs is below the JD's 5-year minimum — correctly ranked near the cutoff |
| 15 | CAND_0046064 | Senior NLP Engineer @ Salesforce | **ACCEPTABLE** | Product company, 8.9 yrs, Pinecone+Elasticsearch+QLoRA, 4/7 production signals, 30-day notice — location (Coimbatore) is the main concern |
| 16 | CAND_0062247 | AI Engineer @ Google | **ACCEPTABLE** | Elite product company, strong vector/RAG skills, 30-day notice, but Kochi location and 2/7 production signals |
| 17 | CAND_0042029 | Senior Data Scientist @ Flipkart | **BORDERLINE** | Strong product company and good skills, but not currently open to work — correctly surfaced in the reasoning as the main constraint |
| 18 | CAND_0006418 | ML Engineer @ Verloop.io | **STRONG FIT** | Conversational AI startup, Gurgaon (JD preferred), Weaviate+Qdrant+Embeddings, 92% recruiter response rate |
| 19 | CAND_0027691 | NLP Engineer @ Haptik | **ACCEPTABLE** | Conversational AI product company, Pune (ideal), 6.5 yrs, 15-day notice — good overall fit |
| 20 | CAND_0092706 | AI Research Engineer @ Unacademy | **BORDERLINE** | Product company, Delhi location, but only 3 JD skills matched and 120-day notice — correctly placed near bottom of top 20 |

---

## Summary

| Judgment | Count | Notes |
|---|---|---|
| Strong Fit | 4 | All ranked in top 10 (ranks 1, 2, 4, 8, 18) |
| Acceptable | 10 | Solid fits with one or two minor concerns each |
| Borderline | 5 | Correctly ranked lower (ranks 7, 12, 14, 17, 20) |
| Weak | 0 | No clearly wrong candidates in top 20 |

**Agreement with ranking: 17/20 candidates are judged as correctly
placed relative to their neighbors.**

The 3 cases where the ranking could be argued:
- **Rank 7 (CAND_0015578)**: Only 1/7 production signals — arguably should
  rank closer to 12-15 rather than top 10. Promoted by strong semantic
  similarity score despite thin production evidence.
- **Rank 12 (CAND_0006567)**: Meta title and Noida location boosted the
  score, but JD-skill depth is thin (only 2 skills matched). A recruiter
  would likely probe this candidate harder.
- **Rank 18 (CAND_0006418)**: Verloop.io is a genuinely strong fit
  (conversational AI, Gurgaon, high response rate) and arguably deserves
  a slightly higher rank than 18.

These three cases represent known limitations of hand-tuned weights without
labeled training data — the system slightly overweights company prestige
and semantic similarity relative to production-signal depth in some cases.

---

## Methodology

Each candidate was reviewed using the `print_top20.py` diagnostic script,
which surfaces: current title and company, years of experience, location,
matched JD-relevant skills, count of production-ML keywords in career
descriptions, consulting-only flag, open-to-work status, notice period,
and recruiter response rate. Judgments were made by the team against the
JD's explicit criteria, including the JD's own stated disqualifiers and
preferred profile description.