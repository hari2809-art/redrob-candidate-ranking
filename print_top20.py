"""
print_top20.py

Prints a readable summary of your top 20 candidates for manual review.
Run this, read each profile, and decide: Strong Fit / Acceptable / Borderline / Weak

Usage: python print_top20.py
"""

import csv
import json

# Load your top 20 from submission
rows = list(csv.DictReader(open("output/submission.csv", encoding="utf-8")))
top20_ids = {r["candidate_id"]: r for r in rows[:20]}

# Load their full profiles
candidates = {}
with open("data/candidates.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in top20_ids:
            candidates[c["candidate_id"]] = c
        if len(candidates) == 20:
            break

CONSULTING = {"tcs","infosys","wipro","accenture","cognizant","capgemini","hcl"}

print("=" * 90)
print("MANUAL VALIDATION SHEET — Team NovaMind AI")
print("For each candidate: judge as STRONG FIT / ACCEPTABLE / BORDERLINE / WEAK")
print("=" * 90)

for r in rows[:20]:
    cid = r["candidate_id"]
    c = candidates.get(cid)
    if not c:
        continue

    p = c["profile"]
    sig = c["redrob_signals"]
    career = c.get("career_history", [])
    skills = c.get("skills", [])

    # Key JD-relevant skills
    jd_skills = ["embeddings","faiss","pinecone","qdrant","weaviate","milvus",
                 "elasticsearch","rag","sentence-transformers","ndcg","mrr",
                 "lora","qlora","transformers","nlp","information retrieval",
                 "semantic search","vector","hybrid search"]
    matched = [s["name"] for s in skills
               if any(kw in s["name"].lower() for kw in jd_skills)]

    companies = [r2["company"] for r2 in career]
    is_consulting = all(any(f in co.lower() for f in CONSULTING) for co in companies)

    prod_text = " ".join(r2.get("description","") for r2 in career).lower()
    prod_signals = sum(1 for kw in ["production","deployed","shipped","scale","retrieval","ranking","embedding"]
                       if kw in prod_text)

    print(f"\nRank {r['rank']:>3} | Score {r['score']} | {cid}")
    print(f"  Title    : {p.get('current_title')} @ {p.get('current_company')} ({p.get('current_company_size')})")
    print(f"  YOE      : {p.get('years_of_experience')} yrs | Location: {p.get('location')}, {p.get('country')}")
    print(f"  Industry : {p.get('current_industry')}")
    print(f"  JD Skills: {', '.join(matched[:6]) if matched else 'NONE MATCHED'}")
    print(f"  Prod sigs: {prod_signals}/7 keywords in career descriptions")
    print(f"  Consulting only: {'YES ⚠️' if is_consulting else 'No'}")
    print(f"  Open to work: {sig.get('open_to_work_flag')} | Notice: {sig.get('notice_period_days')}d | Response: {sig.get('recruiter_response_rate',0):.0%}")
    print(f"  Reasoning: {r['reasoning'][:100]}...")
    print(f"  → YOUR JUDGMENT: [ STRONG FIT / ACCEPTABLE / BORDERLINE / WEAK ]")
    print("-" * 90)