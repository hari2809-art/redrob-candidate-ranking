"""
app.py — NovaMind AI Candidate Ranking Demo
India Runs Hackathon | Track 1: Data & AI
Team: Gurram Harinath, Ponna Chaitanya, Boggula Hrudayananda Reddy
"""

import csv
import json
import streamlit as st

st.set_page_config(
    page_title="NovaMind AI — Candidate Ranker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

section.main > div { padding-top: 1rem; }

.hero {
    background: linear-gradient(135deg, #21295C 0%, #065A82 60%, #1C7293 100%);
    border-radius: 16px;
    padding: 32px 36px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 { color: white; font-size: 28px; margin: 0 0 6px 0; }
.hero p { color: #9FD8CB; margin: 0; font-size: 15px; }
.hero-sub { color: #CBD5E1; font-size: 13px; margin-top: 4px; }

.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
}
.metric-card {
    flex: 1;
    background: white;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 4px solid #1C7293;
    text-align: center;
}
.metric-card.green { border-top-color: #0F766E; }
.metric-card.red   { border-top-color: #B91C1C; }
.metric-card.amber { border-top-color: #B45309; }
.metric-card.blue  { border-top-color: #1D4ED8; }
.metric-num { font-size: 26px; font-weight: 700; color: #21295C; line-height: 1; }
.metric-label { font-size: 11px; color: #64748B; margin-top: 4px; font-weight: 500; letter-spacing: 0.3px; }

.section-title {
    font-size: 17px;
    font-weight: 700;
    color: #21295C;
    margin: 0 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.cand-card {
    background: white;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #E2E8F0;
    position: relative;
    overflow: hidden;
}
.cand-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 5px;
    background: #1C7293;
}
.cand-card.top10::before  { background: linear-gradient(180deg, #0F766E, #14B8A6); }
.cand-card.top50::before  { background: #1C7293; }
.cand-card.lower::before  { background: #94A3B8; }

.rank-num {
    display: inline-block;
    background: #21295C;
    color: white;
    font-size: 13px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-right: 8px;
}
.rank-num.top10 { background: linear-gradient(90deg, #0F766E, #14B8A6); }
.rank-num.top50 { background: #1C7293; }
.rank-num.lower { background: #94A3B8; }

.cand-title { font-size: 16px; font-weight: 700; color: #21295C; }
.cand-company { font-size: 14px; color: #475569; }

.score-box {
    background: #F0FDF9;
    border: 1.5px solid #14B8A6;
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 15px;
    font-weight: 700;
    color: #0F766E;
    white-space: nowrap;
}

.tag {
    display: inline-block;
    background: #F1F5F9;
    color: #334155;
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 12px;
    font-weight: 500;
    margin: 3px 3px 3px 0;
}
.tag.loc  { background: #EFF6FF; color: #1D4ED8; }
.tag.yoe  { background: #F0FDF4; color: #166534; }
.tag.ind  { background: #FDF4FF; color: #7E22CE; }
.tag.skill { background: #FFF7ED; color: #C2410C; }

.bar-bg {
    background: #E2E8F0;
    border-radius: 4px;
    height: 6px;
    margin: 10px 0 10px 0;
    overflow: hidden;
}
.bar-fill {
    height: 6px;
    border-radius: 4px;
    background: linear-gradient(90deg, #0F766E, #14B8A6);
    transition: width 0.3s;
}
.bar-fill.mid { background: linear-gradient(90deg, #1C7293, #38BDF8); }
.bar-fill.low { background: #94A3B8; }

.reasoning {
    font-size: 13.5px;
    color: #475569;
    line-height: 1.6;
    margin-top: 8px;
}
.concern {
    font-size: 12.5px;
    color: #B45309;
    background: #FFFBEB;
    border-left: 3px solid #F59E0B;
    padding: 5px 10px;
    border-radius: 0 6px 6px 0;
    margin-top: 6px;
}

.arch-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    height: 100%;
}
.arch-card h4 { color: #21295C; margin-top: 0; }
.arch-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 13.5px;
    color: #475569;
}
.arch-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #1C7293;
    margin-top: 5px;
    flex-shrink: 0;
}

.trap-card {
    background: #F8FAFC;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
    border-left: 3px solid #1C7293;
}
.trap-card h5 { margin: 0 0 4px 0; color: #21295C; font-size: 13px; }
.trap-card p  { margin: 0; font-size: 12.5px; color: #475569; }
.trap-badge {
    display: inline-block;
    background: #DCFCE7;
    color: #166534;
    border-radius: 12px;
    padding: 1px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 4px;
}

.sidebar-team {
    background: linear-gradient(135deg, #21295C, #065A82);
    border-radius: 10px;
    padding: 14px;
    color: white;
    text-align: center;
    margin-bottom: 16px;
}
.sidebar-team h3 { color: #9FD8CB; margin: 0 0 8px 0; font-size: 13px; letter-spacing: 1px; }
.sidebar-team p  { margin: 2px 0; font-size: 13px; color: white; }
.sidebar-team .leader { font-weight: 700; color: #9FD8CB; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
JD_SKILLS = [
    "embeddings","faiss","pinecone","qdrant","weaviate","milvus",
    "elasticsearch","rag","sentence-transformers","sentence transformers",
    "ndcg","mrr","lora","qlora","transformers","nlp",
    "information retrieval","semantic search","vector","hybrid search",
    "pgvector","opensearch","bm25",
]

@st.cache_data
def load_data():
    rows = list(csv.DictReader(open("output/submission.csv", encoding="utf-8")))
    profiles = {}
    try:
        ids = {r["candidate_id"] for r in rows}
        with open("data/candidates.jsonl", encoding="utf-8") as f:
            for line in f:
                c = json.loads(line)
                if c["candidate_id"] in ids:
                    profiles[c["candidate_id"]] = c
                if len(profiles) == len(ids):
                    break
    except FileNotFoundError:
        pass
    return rows, profiles

rows, profiles = load_data()
all_scores = [float(r["score"]) for r in rows]

def get_matched_skills(c):
    skills = c.get("skills", [])
    matched = []
    for s in skills:
        name = s.get("name", "")
        if any(kw in name.lower() for kw in JD_SKILLS):
            matched.append(name)
    return matched[:5]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-team">
        <h3>🚀 TEAM</h3>
        <p class="leader">Gurram Harinath</p>
        <p style="font-size:11px; color:#9FD8CB;">Leader</p>
        <p>Ponna Chaitanya</p>
        <p>Boggula Hrudayananda Reddy</p>
        <p style="font-size:12px; color:#9FD8CB; margin-top:8px; font-weight:700;">NovaMind AI</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Filters")
    show_n = st.slider("Show top N", 5, 100, 20, step=5)
    keyword = st.text_input("🔍 Search by keyword", placeholder="e.g. Pune, NLP, FAISS, Zomato")
    min_score = st.slider(
        "Min score",
        min_value=round(min(all_scores), 2),
        max_value=round(max(all_scores), 2),
        value=round(min(all_scores), 2),
        step=0.01,
    )

    st.markdown("---")
    st.markdown("**India Runs Hackathon 2026**")
    st.markdown("Track 1: Data & AI")
    st.markdown("Intelligent Candidate Discovery")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎯 Redrob Candidate Ranking System</h1>
    <p>AI-powered shortlisting for <strong>Senior AI Engineer</strong> @ Redrob AI (Series A · Pune/Noida)</p>
    <p class="hero-sub">Two-stage hybrid pipeline · Rule-based scoring + BGE semantic embeddings · 100,000 candidates ranked</p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="metric-row">
    <div class="metric-card blue">
        <div class="metric-num">100K</div>
        <div class="metric-label">CANDIDATES RANKED</div>
    </div>
    <div class="metric-card green">
        <div class="metric-num">100</div>
        <div class="metric-label">SHORTLISTED</div>
    </div>
    <div class="metric-card">
        <div class="metric-num">~2.5m</div>
        <div class="metric-label">RUNTIME (CPU)</div>
    </div>
    <div class="metric-card green">
        <div class="metric-num">0</div>
        <div class="metric-label">HONEYPOTS IN TOP 100</div>
    </div>
    <div class="metric-card amber">
        <div class="metric-num">4,158</div>
        <div class="metric-label">RED FLAGS CAUGHT</div>
    </div>
    <div class="metric-card red">
        <div class="metric-num">0</div>
        <div class="metric-label">DUPLICATE REASONING</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = [r for r in rows if float(r["score"]) >= min_score]
if keyword:
    kw = keyword.lower()
    filtered = [r for r in filtered if kw in r["reasoning"].lower() or kw in r["candidate_id"].lower()]
display = filtered[:show_n]

# ── Candidates ────────────────────────────────────────────────────────────────
st.markdown(f"""
<p class="section-title">🏆 Top Candidates
<span style="font-size:13px; font-weight:400; color:#64748B;">
— showing {len(display)} of {len(filtered)} matching</span></p>
""", unsafe_allow_html=True)

for r in display:
    rank = int(r["rank"])
    score = float(r["score"])
    cid = r["candidate_id"]
    reasoning = r["reasoning"]

    tier = "top10" if rank <= 10 else ("top50" if rank <= 50 else "lower")

    c = profiles.get(cid, {})
    p = c.get("profile", {})
    title    = p.get("current_title", cid)
    company  = p.get("current_company", "")
    yoe      = p.get("years_of_experience", "")
    location = p.get("location", "")
    industry = p.get("current_industry", "")
    matched_skills = get_matched_skills(c) if c else []

    # Score bar percentage
    bar_pct = int((score - min(all_scores)) / (max(all_scores) - min(all_scores)) * 100)
    bar_pct = max(5, bar_pct)
    bar_class = "top10" if rank <= 10 else ("mid" if rank <= 50 else "low")

    # Tags
    tags = ""
    if location: tags += f'<span class="tag loc">📍 {location}</span>'
    if yoe:      tags += f'<span class="tag yoe">⏱ {yoe} yrs</span>'
    if industry: tags += f'<span class="tag ind">🏢 {industry}</span>'
    for sk in matched_skills[:3]:
        tags += f'<span class="tag skill">⚡ {sk}</span>'

    # Concern extraction
    concern_html = ""
    if "Worth checking:" in reasoning or "Main gap:" in reasoning or "concern" in reasoning.lower():
        parts = reasoning.split(".")
        for part in parts:
            if any(w in part.lower() for w in ["worth checking", "main gap", "concern", "notice period", "not open", "outside india", "below", "above"]):
                concern_html = f'<div class="concern">⚠️ {part.strip()}.</div>'
                reasoning = reasoning.replace(part + ".", "").strip()
                break

    st.markdown(f"""
    <div class="cand-card {tier}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
            <div>
                <span class="rank-num {tier}">#{rank}</span>
                <span class="cand-title">{title}</span>
                {"<span class='cand-company'> &nbsp;@ " + company + "</span>" if company else ""}
            </div>
            <span class="score-box">Score: {score:.4f}</span>
        </div>
        <div style="margin: 8px 0 4px 0;">{tags}</div>
        <div class="bar-bg"><div class="bar-fill {bar_class}" style="width:{bar_pct}%"></div></div>
        <div class="reasoning">{reasoning}</div>
        {concern_html}
    </div>
    """, unsafe_allow_html=True)

# ── Architecture ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">⚙️ How It Works</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="arch-card">
        <h4>Stage 1 — Rule-Based (all 100K)</h4>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Title & role fit (0.20)</strong> — Detects wrong titles, consulting-only careers</div></div>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Skills match (0.15)</strong> — Synonym-aware, also scans career descriptions</div></div>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Experience (0.15)</strong> — YOE band, product-company tenure, production signals</div></div>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Location (0.08)</strong> — Pune/Noida preferred, relocation-aware</div></div>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Education (0.07)</strong> — Institution tier + field relevance</div></div>
        <div class="arch-item"><div class="arch-dot"></div><div><strong>Redrob signals (0.05)</strong> — Completeness, GitHub, saves</div></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="arch-card">
        <h4>Stage 2 — Semantic Reranking (top 10K)</h4>
        <div class="arch-item"><div class="arch-dot" style="background:#0F766E"></div><div><strong>BGE-small-en-v1.5 (0.30)</strong> — Highest single weight. Cosine similarity between JD and full candidate profile</div></div>
        <div class="arch-item"><div class="arch-dot" style="background:#0F766E"></div><div>Catches meaning beyond keywords — e.g. "built semantic search from scratch" matches even without "RAG" listed as a skill</div></div>
        <div class="arch-item"><div class="arch-dot" style="background:#0F766E"></div><div>Pool-size validated: 5K, 10K, and 15K all produced identical top-100 results</div></div>
        <div class="arch-item"><div class="arch-dot" style="background:#0F766E"></div><div>Behavioral multiplier (0.65×–1.0×): recency, response rate, notice period, open-to-work</div></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="arch-card">
        <h4>JD Trap Detection</h4>
        <div class="trap-card">
            <h5>🚫 Keyword Stuffers</h5>
            <p>AI skills + wrong title (Marketing Manager etc.)</p>
            <span class="trap-badge">Handled via title_scorer.py</span>
        </div>
        <div class="trap-card">
            <h5>🚫 Honeypot Profiles</h5>
            <p>Salary min&gt;max, impossible tenure, expert+0mo skills</p>
            <span class="trap-badge">0 reached top 100</span>
        </div>
        <div class="trap-card">
            <h5>🚫 Framework Enthusiasts</h5>
            <p>LangChain-only, no pre-LLM ML background</p>
            <span class="trap-badge">4,051 flagged</span>
        </div>
        <div class="trap-card">
            <h5>🚫 Title-Chasers</h5>
            <p>Senior→Staff→Principal via short-tenure switches</p>
            <span class="trap-badge">107 flagged</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<center><span style='color:#94A3B8; font-size:13px;'>"
    "🚀 Team NovaMind AI &nbsp;|&nbsp; India Runs Hackathon 2026 &nbsp;|&nbsp; Track 1: Data & AI"
    "</span></center>",
    unsafe_allow_html=True,
)