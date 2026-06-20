"""
health_check.py

Quick sanity checks on output/submission.csv against candidates.jsonl.
Run after rank.py to catch issues before submitting.

Usage:
    python health_check.py
"""

import csv
import json

from honeypot_detector import honeypot_penalty

# Load top 100 from submission
with open("output/submission.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

top_ids = {r["candidate_id"]: r for r in rows}

# Load only those candidates from the full dataset
candidates_by_id = {}
with open("data/candidates.jsonl", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in top_ids:
            candidates_by_id[c["candidate_id"]] = c

print(f"Total rows: {len(rows)}")

# ── 1. Honeypot count in top 100 ──────────────────────────────────────────
honeypot_count = 0
for r in rows:
    c = candidates_by_id.get(r["candidate_id"])
    if c and honeypot_penalty(c) > 0:
        honeypot_count += 1
print(f"Candidates with honeypot penalty > 0: {honeypot_count} (threshold: <=10)")

# ── 2. Score distribution ───────────────────────────────────────────────
scores = [float(r["score"]) for r in rows]
print(f"Score range: max={max(scores):.4f} min={min(scores):.4f}")
print(f"Top 10 avg: {sum(scores[:10])/10:.4f} | Bottom 10 avg: {sum(scores[-10:])/10:.4f}")

# Check strictly non-increasing
non_increasing = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
print(f"Scores non-increasing: {non_increasing}")

# Count exact-tied scores (large clusters might indicate weak differentiation)
from collections import Counter
tie_counts = Counter(scores)
biggest_tie = max(tie_counts.values())
print(f"Largest group of identical scores: {biggest_tie}")

# ── 3. Location distribution ──────────────────────────────────────────────
locations = Counter()
for r in rows:
    c = candidates_by_id.get(r["candidate_id"])
    if c:
        locations[c["profile"].get("location", "Unknown")] += 1
print("\nTop locations in top 100:")
for loc, cnt in locations.most_common(10):
    print(f"  {loc}: {cnt}")

# ── 4. Title distribution ──────────────────────────────────────────────────
titles = Counter()
for r in rows:
    c = candidates_by_id.get(r["candidate_id"])
    if c:
        titles[c["profile"].get("current_title", "Unknown")] += 1
print("\nTop titles in top 100:")
for title, cnt in titles.most_common(10):
    print(f"  {title}: {cnt}")

# ── 5. Reasoning length / variety spot-check ────────────────────────────────
lengths = [len(r["reasoning"]) for r in rows]
print(f"\nReasoning length: min={min(lengths)} max={max(lengths)} avg={sum(lengths)/len(lengths):.0f}")

# Check for exact duplicate reasoning strings
reasoning_strs = [r["reasoning"] for r in rows]
dupes = len(reasoning_strs) - len(set(reasoning_strs))
print(f"Duplicate reasoning strings: {dupes}")