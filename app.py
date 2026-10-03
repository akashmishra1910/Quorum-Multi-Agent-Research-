"""
Multi-Agent Research System — Streamlit UI (minimal, warm light theme)

Run with:
    streamlit run app.py

Keep this file next to agents.py, tools.py and pipeline.py.
Optional: put the provided .streamlit/config.toml next to it for the base theme.
"""

import html
import re
import textwrap
import time

import streamlit as st

# The agents/chains you shared live in agents.py
from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quorum · Multi-Agent Research",
    page_icon="◐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# Styling  (tweak the colour variables at the top to re-theme everything)
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg: #F4F1EA;        /* warm paper background */
  --card: #FBFAF6;      /* slightly lighter surface */
  --ink: #26231F;       /* main text */
  --muted: #8A8478;     /* secondary text */
  --line: #E4DFD3;      /* borders */
  --accent: #C2674A;    /* terracotta accent */
  --sage: #7A9A82;      /* "done" colour */
}

html, body, .stApp, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--ink);
}
.stApp { background: var(--bg); }

/* hide default chrome */
#MainMenu, footer, .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }

.block-container { max-width: 820px; padding-top: 3.5rem; padding-bottom: 4rem; }

/* ---------- hero ---------- */
.eyebrow {
  text-align: center; font-size: .72rem; letter-spacing: .22em;
  text-transform: uppercase; color: var(--accent); font-weight: 600;
  margin-bottom: .9rem;
}
.hero-title {
  text-align: center; font-size: 2.7rem; line-height: 1.15;
  font-weight: 700; letter-spacing: -.03em; margin: 0 0 .7rem 0;
}
.hero-title span { color: var(--accent); }
.hero-sub {
  text-align: center; color: var(--muted); font-size: 1.02rem;
  max-width: 520px; margin: 0 auto 2.4rem auto; line-height: 1.6;
}

/* ---------- input ---------- */
[data-testid="stForm"] { border: none; padding: 0; background: transparent; }
.stTextInput div[data-baseweb="input"] {
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; box-shadow: 0 1px 2px rgba(38,35,31,.04);
  transition: border-color .2s, box-shadow .2s;
}
.stTextInput div[data-baseweb="input"]:focus-within {
  border-color: var(--accent); box-shadow: 0 0 0 4px rgba(194,103,74,.12);
}
.stTextInput div[data-baseweb="base-input"] { background: transparent; }
.stTextInput input { padding: .85rem 1rem; font-size: 1rem; color: var(--ink); }
.stTextInput input::placeholder { color: #B1AA9B; }

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
  border-radius: 12px; font-weight: 600; font-size: .9rem;
  border: 1px solid var(--line); background: var(--card); color: var(--ink);
  padding: .55rem 1.1rem; transition: all .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--ink); color: var(--ink); transform: translateY(-1px);
}
/* primary (the "Research" button) */
button[kind="primary"], button[kind="primaryFormSubmit"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--ink) !important; color: var(--bg) !important;
  border: 1px solid var(--ink) !important; height: 3rem; width: 100%;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  background: #3b362f !important; color: #fff !important;
}

/* example chips */
.chips-label { color: var(--muted); font-size: .78rem; margin: 1.1rem 0 .4rem 0; text-align: center; }

/* ---------- step tracker ---------- */
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: .7rem; margin: 2rem 0 1rem 0; }
.step {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  padding: .95rem 1rem; transition: all .3s ease; opacity: .55;
}
.step .num { font-size: .68rem; letter-spacing: .14em; color: var(--muted); font-weight: 600; }
.step .name { font-weight: 600; margin-top: .25rem; font-size: .98rem; }
.step .desc { color: var(--muted); font-size: .78rem; margin-top: .15rem; }
.step.active { opacity: 1; border-color: var(--accent); box-shadow: 0 6px 20px rgba(194,103,74,.12); }
.step.active .num { color: var(--accent); }
.step.active .num::after { content: " ●"; animation: pulse 1.1s ease-in-out infinite; }
.step.done { opacity: 1; background: #F0F3EC; border-color: #D5DDCF; }
.step.done .num { color: var(--sage); }
.step.done .num::after { content: " ✓"; }
@keyframes pulse { 0%,100% { opacity: .25; } 50% { opacity: 1; } }
@media (max-width: 640px) { .steps { grid-template-columns: repeat(2, 1fr); } .hero-title { font-size: 2.1rem; } }

/* ---------- result cards ---------- */
.topic-line { color: var(--muted); font-size: .85rem; margin: 2.2rem 0 .8rem 0; }
.topic-line b { color: var(--ink); font-weight: 600; }
.score-card {
  background: var(--card); border: 1px solid var(--line); border-radius: 20px;
  padding: 1.5rem 1.7rem; display: flex; gap: 1.6rem; align-items: center;
  box-shadow: 0 1px 2px rgba(38,35,31,.04);
}
.score-num { font-size: 3.2rem; font-weight: 700; letter-spacing: -.04em; line-height: 1; white-space: nowrap; }
.score-num small { font-size: 1.1rem; color: var(--muted); font-weight: 500; letter-spacing: 0; }
.score-meta { border-left: 1px solid var(--line); padding-left: 1.6rem; }
.score-label { font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
.score-verdict { margin-top: .35rem; color: #4a453d; font-size: .95rem; line-height: 1.55; }
.pills { display: flex; gap: .5rem; margin: .9rem 0 1.4rem 0; flex-wrap: wrap; }
.pill {
  background: transparent; border: 1px solid var(--line); border-radius: 999px;
  padding: .28rem .8rem; font-size: .78rem; color: var(--muted);
}

/* bordered containers (report / feedback) */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--card); border-color: var(--line) !important; border-radius: 18px;
}
[data-testid="stVerticalBlockBorderWrapper"] h1,
[data-testid="stVerticalBlockBorderWrapper"] h2,
[data-testid="stVerticalBlockBorderWrapper"] h3 { letter-spacing: -.02em; font-weight: 650; }
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] li { line-height: 1.75; color: #3a362f; }

/* tabs */
button[data-baseweb="tab"] { font-weight: 500; color: var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--ink); font-weight: 600; }
div[data-baseweb="tab-highlight"] { background-color: var(--accent); }
div[data-baseweb="tab-border"] { background-color: var(--line); }

/* expanders */
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 14px; background: var(--card); }

/* timing bars */
.t-row { display: flex; align-items: center; gap: 1rem; margin: .8rem 0; }
.t-name { width: 70px; font-size: .85rem; color: var(--muted); }
.t-track { flex: 1; height: 10px; background: #EBE6DB; border-radius: 999px; overflow: hidden; }
.t-fill { height: 100%; background: var(--accent); border-radius: 999px; }
.t-val { width: 55px; text-align: right; font-size: .82rem; font-weight: 600; }

.footer-note { text-align: center; color: #B1AA9B; font-size: .74rem; margin-top: 3rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def md(s: str):
    """Render an HTML snippet (dedented so markdown never treats it as code)."""
    st.markdown(textwrap.dedent(s).strip(), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
STEPS = [
    ("01", "Search", "Finding sources"),
    ("02", "Read", "Scraping best page"),
    ("03", "Write", "Drafting report"),
    ("04", "Review", "Critic scoring"),
]


def render_steps(placeholder, active: int):
    """active = index of the running step; 4 means everything is done."""
    cards = []
    for i, (num, name, desc) in enumerate(STEPS):
        state = "done" if i < active else "active" if i == active else ""
        cards.append(
            f'<div class="step {state}"><div class="num">{num}</div>'
            f'<div class="name">{name}</div><div class="desc">{desc}</div></div>'
        )
    placeholder.markdown(f'<div class="steps">{"".join(cards)}</div>', unsafe_allow_html=True)


def extract_text(agent_result) -> str:
    """Final text answer from a LangChain agent result."""
    content = agent_result["messages"][-1].content
    if isinstance(content, list):
        content = " ".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return content


def parse_score(critique: str):
    m = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", critique)
    return float(m.group(1)) if m else None


def parse_verdict(critique: str) -> str:
    m = re.search(r"One line verdict:\s*(.+)", critique, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip().split("\n")[0] if m else ""


def run_pipeline(topic: str, steps_ph) -> dict:
    results, timings = {}, {}

    # 1) Search agent
    render_steps(steps_ph, 0)
    t = time.time()
    search_out = build_search_agent().invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    results["search"] = extract_text(search_out)
    timings["Search"] = time.time() - t

    # 2) Reader agent
    render_steps(steps_ph, 1)
    t = time.time()
    reader_out = build_reader_agent().invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', pick the most "
                    "relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:3000]}",
                )
            ]
        }
    )
    results["scraped"] = extract_text(reader_out)
    timings["Read"] = time.time() - t

    # 3) Writer
    render_steps(steps_ph, 2)
    t = time.time()
    combined = (
        f"SEARCH RESULTS:\n{results['search']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{results['scraped']}"
    )
    results["report"] = writer_chain.invoke({"topic": topic, "research": combined})
    timings["Write"] = time.time() - t

    # 4) Critic
    render_steps(steps_ph, 3)
    t = time.time()
    results["critique"] = critic_chain.invoke({"report": results["report"]})
    timings["Review"] = time.time() - t

    render_steps(steps_ph, 4)
    results["timings"] = timings
    return results


# ----------------------------------------------------------------------------
# Hero + input
# ----------------------------------------------------------------------------
md(
    """
    <div class="eyebrow">Quorum · Multi-Agent Research</div>
    <div class="hero-title">Research anything,<br><span>thoughtfully.</span></div>
    <div class="hero-sub">Four AI agents search, read, write and critique, so you get a sourced report in minutes.</div>
    """
)

topic_to_run = None

with st.form("research_form", border=False):
    c1, c2 = st.columns([5, 1.6], vertical_alignment="center")
    with c1:
        topic_input = st.text_input(
            "Topic",
            placeholder="What would you like to research?",
            label_visibility="collapsed",
        )
    with c2:
        submitted = st.form_submit_button("Research →", type="primary")

if submitted:
    if topic_input.strip():
        topic_to_run = topic_input.strip()
    else:
        st.warning("Please enter a topic first.")

md('<div class="chips-label">or try one of these</div>')
examples = [
    "Latest advances in agentic AI",
    "Future of quantum computing",
    "Renewable energy trends in India",
]
chip_cols = st.columns(len(examples))
for col, ex in zip(chip_cols, examples):
    if col.button(ex, key=f"chip_{ex}", use_container_width=True):
        topic_to_run = ex

# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
if topic_to_run:
    steps_ph = st.empty()
    try:
        st.session_state["results"] = run_pipeline(topic_to_run, steps_ph)
        st.session_state["topic"] = topic_to_run
    except Exception as e:
        steps_ph.empty()
        st.error(f"Something went wrong: {e}")

# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
if "results" in st.session_state:
    r = st.session_state["results"]
    shown_topic = st.session_state.get("topic", "")

    score = parse_score(r["critique"])
    verdict = parse_verdict(r["critique"])
    total = sum(r["timings"].values())
    words = len(r["report"].split())

    md(f'<div class="topic-line">Report on <b>{html.escape(shown_topic)}</b></div>')

    score_txt = f"{score:g}<small> / 10</small>" if score is not None else "—"
    verdict_html = html.escape(verdict) if verdict else "Review complete."
    md(
        f"""
        <div class="score-card">
          <div class="score-num">{score_txt}</div>
          <div class="score-meta">
            <div class="score-label">Critic verdict</div>
            <div class="score-verdict">{verdict_html}</div>
          </div>
        </div>
        <div class="pills">
          <span class="pill">⏱ {total:.1f}s total</span>
          <span class="pill">{words} words</span>
          <span class="pill">4 agents</span>
        </div>
        """
    )

    tab_report, tab_feedback, tab_research, tab_time = st.tabs(
        ["Report", "Feedback", "Research", "Timings"]
    )

    with tab_report:
        with st.container(border=True):
            st.markdown(r["report"])
        fname = re.sub(r"[^a-z0-9]+", "_", shown_topic.lower()).strip("_")[:40] or "report"
        st.download_button(
            "Download .md",
            data=r["report"],
            file_name=f"{fname}.md",
            mime="text/markdown",
        )

    with tab_feedback:
        with st.container(border=True):
            st.markdown(r["critique"])

    with tab_research:
        with st.expander("Search agent output"):
            st.markdown(r["search"])
        with st.expander("Reader agent output (scraped content)"):
            st.markdown(r["scraped"])

    with tab_time:
        longest = max(r["timings"].values()) or 1
        rows = "".join(
            f'<div class="t-row"><div class="t-name">{k}</div>'
            f'<div class="t-track"><div class="t-fill" style="width:{v / longest * 100:.0f}%"></div></div>'
            f'<div class="t-val">{v:.1f}s</div></div>'
            for k, v in r["timings"].items()
        )
        md(rows)

    if st.button("↺  New research"):
        st.session_state.pop("results", None)
        st.session_state.pop("topic", None)
        st.rerun()

md('<div class="footer-note">Quorum · openai/gpt-oss-120b · Groq · LangChain</div>')