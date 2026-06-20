import json
from jd_red_flags import red_flag_penalty

count_framework = 0
count_title = 0
total = 0

with open('data/candidates.jsonl', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        _, flags = red_flag_penalty(c)
        if any('framework' in fl for fl in flags):
            count_framework += 1
        if any('title' in fl for fl in flags):
            count_title += 1
        total += 1

print(f'Total candidates: {total}')
print(f'Framework-enthusiast flagged: {count_framework}')
print(f'Title-chaser flagged: {count_title}')
print(f'Combined (either flag): {count_framework + count_title} (may overlap)')