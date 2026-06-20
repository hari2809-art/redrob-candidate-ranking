import json

framework_kws = ['langchain', 'llamaindex', 'prompt engineering', 'autogpt', 'openai api']

found = 0
with open('data/candidates.jsonl', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        profile = c.get('profile', {})
        skills = c.get('skills', [])

        summary = (profile.get('summary', '') + ' ' + profile.get('headline', '')).lower()
        skill_names = ' '.join(s.get('name', '').lower() for s in skills)

        summary_hits = sum(1 for kw in framework_kws if kw in summary)
        skill_hits = sum(1 for kw in framework_kws if kw in skill_names)

        if summary_hits >= 2 or skill_hits >= 2:
            found += 1
            if found <= 5:
                cid = c['candidate_id']
                title = profile.get('current_title', '')
                headline = profile.get('headline', '')[:100]
                print(f'{cid} | {title} | summary_hits={summary_hits} skill_hits={skill_hits}')
                print(f'  Headline: {headline}')
                print()

print(f'Total candidates with framework signals: {found}')