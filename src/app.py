# src/app.py
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(
    page_title="NIYAMR — Legislative AI Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Developer-supplied local PDF path (your uploaded file)
ORIGINAL_PDF = "/mnt/data/ukpga_20250022_en.pdf"

# Paths to cached outputs
SUMMARY_PATH = Path("cache/summary.json")
SECTIONS_PATH = Path("cache/sections.json")
RULES_PATH = Path("cache/rule_checks.json")

# ---------- THEME / STYLES ----------
PRIMARY_ORANGE = "#ff7a2d"
PRIMARY_PURPLE = "#6b21a8"
CARD_BG = "#1f1b2e"  # dark card background for contrast
TEXT_LIGHT = "#EDE7F6"

st.markdown(
    f"""
<style>
/* Background */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(180deg, rgba(107,33,168,0.06) 0%, rgba(255,122,45,0.02) 100%);
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {PRIMARY_PURPLE}22, {PRIMARY_ORANGE}11);
}}

/* Headers and accents */
h1, h2, h3 {{
    color: {PRIMARY_PURPLE};
}}

.big-agent {{
    font-size: 28px;
    font-weight: 700;
    color: {PRIMARY_ORANGE};
}}

/* Cards */
.card {{
    background: {CARD_BG};
    padding: 16px;
    border-radius: 12px;
    color: {TEXT_LIGHT};
    box-shadow: 0 6px 18px rgba(15, 12, 20, 0.5);
    margin-bottom: 12px;
}}

.kv {{
    color: #C7B8F0;
    font-weight: 600;
}}

.badge-pass {{
    background-color: #16a34a;
    color: white;
    padding: 6px 10px;
    border-radius: 10px;
    font-weight: 700;
}}

.badge-fail {{
    background-color: #dc2626;
    color: white;
    padding: 6px 10px;
    border-radius: 10px;
    font-weight: 700;
}}

.badge-partial {{
    background-color: #f59e0b;
    color: white;
    padding: 6px 10px;
    border-radius: 10px;
    font-weight: 700;
}}

.small-muted {{
    color: #bdb6e6;
    font-size: 12px;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def load_json_safe(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None

def format_rule_badge(status: str):
    if status.lower() == "pass":
        return f'<span class="badge-pass">PASS</span>'
    if status.lower() == "fail":
        return f'<span class="badge-fail">FAIL</span>'
    return f'<span class="badge-partial">PARTIAL</span>'

def pretty_dump(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)

def combined_report(summary, sections, rules):
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "sections": sections,
        "rule_checks": rules
    }

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("🤖", unsafe_allow_html=True)
    st.markdown("<div class='big-agent'>NIYAMR — Legislative AI Agent</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Navigation**")
    page = st.radio("", ["Dashboard", "Summary", "Extracted Sections", "Rule Checks", "Download"], index=0)
    st.markdown("---")
    st.markdown("**Sources**")
    if Path(ORIGINAL_PDF).exists():
        # show local path - dev tool will convert to url if needed
        st.markdown(f"[View original Act PDF]({ORIGINAL_PDF})")
    else:
        st.write("Original PDF: Not found")
    st.markdown("**Cache files**")
    st.write(f"summary.json: {'✅' if SUMMARY_PATH.exists() else '❌'}")
    st.write(f"sections.json: {'✅' if SECTIONS_PATH.exists() else '❌'}")
    st.write(f"rule_checks.json: {'✅' if RULES_PATH.exists() else '❌'}")
    st.markdown("---")
    st.caption("This UI displays cached outputs only — no LLM calls from the app.")

# ---------- Load data ----------
summary = load_json_safe(SUMMARY_PATH) or []
sections = load_json_safe(SECTIONS_PATH) or {}
rules = load_json_safe(RULES_PATH) or []

# ---------- Pages ----------
st.markdown("<br>", unsafe_allow_html=True)

if page == "Dashboard":
    col1, col2, col3 = st.columns([1.6, 1, 1])
    with col1:
        st.markdown(f"<div class='card'>\
            <h3 style='color:{PRIMARY_ORANGE}'>Agent Snapshot</h3>\
            <p class='small-muted'>Summary • Sections • Rule checks</p>\
            <p style='margin-top:8px'>{len(summary) if summary else 0} bullets • {len(sections)} sections</p>\
            </div>", unsafe_allow_html=True)

    with col2:
        # compute pass/fail counts
        pass_count = sum(1 for r in rules if r.get("status") == "pass")
        fail_count = sum(1 for r in rules if r.get("status") == "fail")
        partial_count = sum(1 for r in rules if r.get("status") == "partial")
        st.markdown(f"<div class='card'><h4>Rule Summary</h4><p class='kv'>PASS: {pass_count}</p><p class='kv'>FAIL: {fail_count}</p><p class='kv'>PARTIAL: {partial_count}</p></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='card'><h4>Files</h4><p class='kv'>Uploaded Act</p><p class='small-muted'>{Path(ORIGINAL_PDF).name if Path(ORIGINAL_PDF).exists() else 'N/A'}</p></div>", unsafe_allow_html=True)

    st.markdown("### Summary Preview")
    if summary:
        # show first 6 bullets if list or parse string
        if isinstance(summary, list):
            bullets = summary
        elif isinstance(summary, dict):
            # if stored as dict with text
            bullets = summary.get("bullets") or [summary.get("text")]
        else:
            # string — try split on newlines or bullets
            text = summary if isinstance(summary, str) else pretty_dump(summary)
            bullets = [line.strip() for line in text.split("\n") if line.strip()][:6]

        for b in bullets[:6]:
            st.markdown(f"<div class='card'><p>{b}</p></div>", unsafe_allow_html=True)
    else:
        st.info("summary.json not found or empty.")

elif page == "Summary":
    st.markdown(f"<h2 style='color:{PRIMARY_PURPLE}'>Summary</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if summary:
        if isinstance(summary, (list, tuple)):
            for s in summary:
                st.markdown(f"- {s}")
        elif isinstance(summary, dict):
            # print human-friendly if possible
            content = summary.get("text") or summary.get("bullets") or pretty_dump(summary)
            if isinstance(content, list):
                for s in content:
                    st.markdown(f"- {s}")
            else:
                st.markdown(content)
        else:
            st.markdown(summary)
    else:
        st.info("No summary found (cache/summary.json).")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Extracted Sections":
    st.markdown(f"<h2 style='color:{PRIMARY_PURPLE}'>Extracted Sections</h2>", unsafe_allow_html=True)
    if sections:
        for key, value in sections.items():
            label = key.replace("_", " ").title()
            with st.expander(label, expanded=False):
                if value == "Not found":
                    st.warning("Not found in the Act.")
                else:
                    st.markdown(f"<div class='card'><pre style='white-space:pre-wrap'>{value}</pre></div>", unsafe_allow_html=True)
    else:
        st.info("No sections found (cache/sections.json).")

elif page == "Rule Checks":
    st.markdown(f"<h2 style='color:{PRIMARY_PURPLE}'>Rule Checks</h2>", unsafe_allow_html=True)
    if rules:
        for r in rules:
            badge = format_rule_badge(r.get("status", "fail"))
            st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><strong>{r.get('rule')}</strong><div class='small-muted'>{r.get('evidence')}</div></div><div>{badge}</div></div><hr><div>{r.get('explanation')}</div><div class='small-muted' style='margin-top:8px'>Confidence: {r.get('confidence')}%</div></div>", unsafe_allow_html=True)
    else:
        st.info("No rule checks found (cache/rule_checks.json).")

elif page == "Download":
    st.markdown(f"<h2 style='color:{PRIMARY_PURPLE}'>Download Full Report</h2>", unsafe_allow_html=True)
    report = combined_report(summary, sections, rules)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.download_button(
        "⬇️ Download combined report (JSON)",
        data=pretty_dump(report),
        file_name=f"niyamr_report_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
        mime="application/json"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Built with ❤️ — Offline viewer for cached AI outputs. Theme: Orange + Purple.</div>", unsafe_allow_html=True)
