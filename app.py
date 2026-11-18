"""
Bug Explanation and Fix Assistant - Main Streamlit Application
A professional web interface for analyzing, explaining, and fixing code bugs.
"""

import streamlit as st
import os
import sys
import json

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from modules.language_detector import detect_language, get_supported_languages
from modules.bug_analyzer import BugAnalyzer
from modules.prompt_manager import PromptManager
from modules.response_formatter import format_for_display

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bug Fix Assistant",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Header banner */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.4rem 0 0 0;
        opacity: 0.92;
        font-size: 1.05rem;
    }

    /* Result cards */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s;
    }
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    }
    .result-card h4 {
        margin-top: 0;
        color: #4a5568;
    }

    /* Severity badges */
    .severity-critical {
        background: #fed7d7; color: #c53030;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 600; font-size: 0.85rem;
        display: inline-block;
    }
    .severity-high {
        background: #feebc8; color: #c05621;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 600; font-size: 0.85rem;
        display: inline-block;
    }
    .severity-medium {
        background: #fefcbf; color: #975a16;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 600; font-size: 0.85rem;
        display: inline-block;
    }
    .severity-low {
        background: #c6f6d5; color: #276749;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 600; font-size: 0.85rem;
        display: inline-block;
    }

    /* Meta info bar */
    .meta-bar {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.88rem;
        color: #718096;
    }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] {
        background: #f8f9fb;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-weight: 600;
    }

    /* About section cards */
    .about-card {
        background: linear-gradient(135deg, #667eea11, #764ba211);
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }

    /* Step columns */
    .step-wrong  { border-left: 3px solid #e53e3e; padding-left: 0.8rem; }
    .step-change { border-left: 3px solid #ecc94b; padding-left: 0.8rem; }
    .step-works  { border-left: 3px solid #38a169; padding-left: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if "analyzer" not in st.session_state:
    st.session_state.analyzer = BugAnalyzer()
if "prompt_manager" not in st.session_state:
    st.session_state.prompt_manager = PromptManager()
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = None

analyzer: BugAnalyzer = st.session_state.analyzer
prompt_manager: PromptManager = st.session_state.prompt_manager


# ──────────────────────────────────────────────
# Helper: severity icon
# ──────────────────────────────────────────────
def _severity_icon(level: str) -> str:
    mapping = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }
    return mapping.get(level.lower() if level else "", "⚪")


def _severity_badge(level: str) -> str:
    css_class = f"severity-{level.lower()}" if level else "severity-medium"
    icon = _severity_icon(level)
    return f'<span class="{css_class}">{icon} {level.upper() if level else "UNKNOWN"}</span>'


def _confidence_color(level: str) -> str:
    mapping = {"high": "🟢", "medium": "🟡", "low": "🟠"}
    return mapping.get(level.lower() if level else "", "⚪")


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    mode = "AI" if os.getenv("GEMINI_API_KEY") else "Demo"
    mode_color = "#38a169" if mode == "AI" else "#ecc94b"
    st.markdown(
        f"**Current Mode:** <span style='color:{mode_color};font-weight:700'>"
        f"{'🤖 AI-Powered' if mode == 'AI' else '🎭 Demo / Offline'}</span>",
        unsafe_allow_html=True,
    )

    st.divider()
    page = st.radio(
        "📂 Navigation",
        ["🔍 Bug Analyzer", "⚖️ Prompt Comparison", "📝 Prompt Viewer", "ℹ️ About"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### 🌐 Supported Languages")
    langs = get_supported_languages()
    for lang in langs:
        st.markdown(f"- {lang}")


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown(
    '<div class="main-header">'
    "<h1>🐛 Bug Explanation &amp; Fix Assistant</h1>"
    "<p>Paste your buggy code and error message — get a clear explanation and a working fix.</p>"
    "</div>",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════
# Result display helper (shared by pages)
# ══════════════════════════════════════════════
def display_results(result: dict) -> None:
    """Render a full analysis result with expandable sections A–G."""

    formatted = format_for_display(result)

    # ── Meta bar ──
    meta = formatted.get("_meta", {})
    if meta:
        m1, m2, m3 = st.columns(3)
        m1.metric("Mode", meta.get("mode", "—"))
        m2.metric("Prompt Version", meta.get("prompt_version", "—"))
        m3.metric("Analysis Time", f"{meta.get('analysis_time', 0):.2f}s")

    # A. Error Identification
    error_id = formatted.get("error_identification", {})
    with st.expander("🅰️ Error Identification", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"**Type**\n\n`{error_id.get('error_type', '—')}`")
        c2.markdown(f"**Location**\n\n`{error_id.get('location', '—')}`")
        sev = error_id.get("severity", "medium")
        c3.markdown(f"**Severity**\n\n{_severity_badge(sev)}", unsafe_allow_html=True)
        c4.markdown(f"**Summary**\n\n{error_id.get('summary', '—')}")

    # B. Root Cause
    root = formatted.get("root_cause", {})
    with st.expander("🅱️ Root Cause Analysis"):
        st.markdown(root.get("explanation", "_No explanation available._"))
        prob_code = root.get("problematic_code", "")
        if prob_code:
            st.markdown("**Problematic Code:**")
            st.code(prob_code, language="text")
        rule = root.get("language_rule", "")
        if rule:
            st.info(f"📏 **Language Rule:** {rule}")

    # C. Corrected Code
    fix = formatted.get("corrected_code", {})
    with st.expander("🅲 Corrected Code", expanded=True):
        code_text = fix.get("code", "")
        if code_text:
            st.code(code_text, language="text")
            # Copy button (Streamlit native)
            if st.button("📋 Copy corrected code", key="copy_fix"):
                st.toast("Code copied to clipboard area above ☝️")
        changes = fix.get("changes", [])
        if changes:
            st.markdown("**Changes Made:**")
            for ch in changes:
                st.markdown(f"- {ch}")

    # D. Simple Explanation
    simple = formatted.get("simple_explanation", {})
    with st.expander("🅳 Simple Explanation"):
        st.markdown(simple.get("text", "_No explanation._"))
        analogy = simple.get("analogy", "")
        if analogy:
            st.success(f"💡 **Analogy:** {analogy}")

    # E. Step-by-Step Debugging
    steps = formatted.get("debugging_steps", [])
    with st.expander("🅴 Step-by-Step Debugging"):
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"### Step {i}")
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.markdown(
                        f'<div class="step-wrong"><strong>❌ What\'s Wrong</strong><br>'
                        f'{step.get("wrong", "—")}</div>',
                        unsafe_allow_html=True,
                    )
                with sc2:
                    st.markdown(
                        f'<div class="step-change"><strong>🔄 What Changed</strong><br>'
                        f'{step.get("changed", "—")}</div>',
                        unsafe_allow_html=True,
                    )
                with sc3:
                    st.markdown(
                        f'<div class="step-works"><strong>✅ Why It Works</strong><br>'
                        f'{step.get("works", "—")}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown("_No debugging steps available._")

    # F. Prevention Tips
    tips = formatted.get("prevention_tips", [])
    with st.expander("🅵 Prevention Tips"):
        if tips:
            for tip in tips:
                st.markdown(f"- {tip}")
        else:
            st.markdown("_No tips available._")

    # G. Confidence & Limitations
    conf = formatted.get("confidence", {})
    with st.expander("🅶 Confidence & Limitations"):
        level = conf.get("level", "medium")
        st.markdown(
            f"**Confidence Level:** {_confidence_color(level)} **{level.upper()}**"
        )
        assumptions = conf.get("assumptions", [])
        if assumptions:
            st.markdown("**Assumptions:**")
            for a in assumptions:
                st.markdown(f"- {a}")
        limitations = conf.get("limitations", [])
        if limitations:
            st.markdown("**Limitations:**")
            for lim in limitations:
                st.warning(lim)


# ══════════════════════════════════════════════
# Shared code-input widget
# ══════════════════════════════════════════════
def _code_input_widgets(key_prefix: str = "main"):
    """Return (code, error_message, selected_language) from common input widgets."""
    code = st.text_area(
        "📝 Paste your code",
        height=250,
        placeholder="def greet(name):\n    print('Hello ' + name)\n\ngreet(42)",
        key=f"{key_prefix}_code",
    )
    error_msg = st.text_area(
        "⚠️ Error message (optional but recommended)",
        height=100,
        placeholder="TypeError: can only concatenate str (not \"int\") to str",
        key=f"{key_prefix}_error",
    )

    lang_options = ["Auto-Detect"] + get_supported_languages()
    language = st.selectbox(
        "🌐 Language",
        lang_options,
        key=f"{key_prefix}_lang",
    )
    return code, error_msg, language


def _resolve_language(code: str, language: str):
    """Resolve Auto-Detect to a concrete language, returning (lang, detection_info | None)."""
    if language == "Auto-Detect":
        detection = detect_language(code)
        detected_lang = detection.get("language", "python")
        confidence = detection.get("confidence", 0)
        return detected_lang, detection
    return language, None


# ══════════════════════════════════════════════
# PAGE 1 — Bug Analyzer
# ══════════════════════════════════════════════
if page == "🔍 Bug Analyzer":
    st.markdown("## 🔍 Analyze a Bug")

    code, error_msg, language = _code_input_widgets("analyzer")

    # Show detected language info when Auto-Detect is active and there's code
    detection_info = None
    if language == "Auto-Detect" and code.strip():
        resolved_lang, detection_info = _resolve_language(code, language)
        conf_pct = detection_info.get("confidence", 0) if detection_info else 0
        st.info(
            f"🔎 Detected language: **{resolved_lang}** "
            f"(confidence: {conf_pct:.0%})"
        )
    else:
        resolved_lang = language if language != "Auto-Detect" else "python"

    # Analyze button
    if st.button("🚀 Analyze Bug", type="primary", use_container_width=True):
        if not code.strip():
            st.warning("Please paste some code before analyzing.")
        else:
            with st.spinner("Analyzing your code…"):
                result = analyzer.analyze(
                    code=code,
                    error_message=error_msg,
                    language=resolved_lang,
                )
                st.session_state.analysis_result = result

    # Display results
    if st.session_state.analysis_result:
        st.divider()
        st.markdown("### 📊 Analysis Results")
        display_results(st.session_state.analysis_result)


# ══════════════════════════════════════════════
# PAGE 2 — Prompt Comparison
# ══════════════════════════════════════════════
elif page == "⚖️ Prompt Comparison":
    st.markdown("## ⚖️ Compare Prompt Versions")
    st.caption(
        "Run the same bug through all three prompt versions and compare quality."
    )

    code, error_msg, language = _code_input_widgets("compare")

    resolved_lang = language
    if language == "Auto-Detect" and code.strip():
        resolved_lang, _ = _resolve_language(code, language)

    if st.button("🔬 Compare All Prompt Versions", type="primary", use_container_width=True):
        if not code.strip():
            st.warning("Please paste some code before comparing.")
        else:
            results = {}
            progress = st.progress(0, text="Starting comparison…")
            versions = prompt_manager.get_all_versions()
            for idx, version in enumerate(versions):
                progress.progress(
                    (idx + 1) / len(versions),
                    text=f"Analyzing with {version}…",
                )
                res = analyzer.analyze(
                    code=code,
                    error_message=error_msg,
                    language=resolved_lang if resolved_lang != "Auto-Detect" else "python",
                    prompt_version=version,
                )
                results[version] = res
            progress.empty()
            st.session_state.comparison_results = results

    # Display comparison results
    if st.session_state.comparison_results:
        st.divider()
        comp = st.session_state.comparison_results
        version_keys = list(comp.keys())
        tab_labels = [v.upper() for v in version_keys] + ["📊 Summary"]
        tabs = st.tabs(tab_labels)

        for i, ver in enumerate(version_keys):
            with tabs[i]:
                st.markdown(f"### Results — {ver.upper()}")
                display_results(comp[ver])

        # Summary tab
        with tabs[-1]:
            st.markdown("### 📊 Comparison Summary")

            # Build comparison table
            table_data = {
                "Metric": [
                    "Error Type",
                    "Severity",
                    "Confidence",
                    "Analysis Time (s)",
                    "Has Corrected Code",
                    "Number of Steps",
                    "Number of Tips",
                ],
            }
            for ver in version_keys:
                formatted = format_for_display(comp[ver])
                eid = formatted.get("error_identification", {})
                conf = formatted.get("confidence", {})
                meta = formatted.get("_meta", {})
                fix = formatted.get("corrected_code", {})
                steps = formatted.get("debugging_steps", [])
                tips = formatted.get("prevention_tips", [])
                table_data[ver.upper()] = [
                    eid.get("error_type", "—"),
                    eid.get("severity", "—"),
                    conf.get("level", "—"),
                    f"{meta.get('analysis_time', 0):.2f}",
                    "✅" if fix.get("code") else "❌",
                    str(len(steps)),
                    str(len(tips)),
                ]

            st.table(table_data)

            # Key observations matrix
            st.markdown("#### 🔑 Key Observations")
            for ver in version_keys:
                formatted = format_for_display(comp[ver])
                conf = formatted.get("confidence", {})
                limitations = conf.get("limitations", [])
                st.markdown(f"**{ver.upper()}**")
                if limitations:
                    for lim in limitations:
                        st.markdown(f"  - ⚠️ {lim}")
                else:
                    st.markdown("  - ✅ No noted limitations")


# ══════════════════════════════════════════════
# PAGE 3 — Prompt Viewer
# ══════════════════════════════════════════════
elif page == "📝 Prompt Viewer":
    st.markdown("## 📝 Prompt Templates")
    st.caption("Explore the prompt engineering behind each analysis version.")

    versions = prompt_manager.get_all_versions()
    tab_labels = [v.upper() for v in versions] + ["FINAL"]
    tabs = st.tabs(tab_labels)

    for i, ver in enumerate(versions):
        with tabs[i]:
            info = prompt_manager.get_prompt_info(ver)
            st.markdown(f"### {info.get('name', ver.upper())}")

            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown(f"**Description:** {info.get('description', '—')}")
                st.markdown(f"**Output Format:** `{info.get('format', '—')}`")
            with mc2:
                improvements = info.get("improvements", [])
                if improvements:
                    st.markdown("**Improvements:**")
                    for imp in improvements:
                        st.markdown(f"- ✨ {imp}")

            limitations = info.get("limitations", [])
            if limitations:
                st.markdown("**Known Limitations:**")
                for lim in limitations:
                    st.markdown(f"- ⚠️ {lim}")

            st.markdown("---")
            st.markdown("**Full Prompt Template:**")
            template = prompt_manager.get_template(ver)
            st.code(template, language="text")

    # Final / active prompt tab
    with tabs[-1]:
        st.markdown("### 🏆 Final (Active) Prompt")
        final_info = prompt_manager.get_prompt_info("final")
        st.markdown(f"**Description:** {final_info.get('description', '—')}")
        st.markdown(f"**Output Format:** `{final_info.get('format', '—')}`")
        improvements = final_info.get("improvements", [])
        if improvements:
            st.markdown("**Improvements over previous versions:**")
            for imp in improvements:
                st.markdown(f"- ✨ {imp}")

        st.markdown("---")
        st.markdown("**Full Prompt Template:**")
        final_template = prompt_manager.get_template("final")
        st.code(final_template, language="text")


# ══════════════════════════════════════════════
# PAGE 4 — About
# ══════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown("## ℹ️ About Bug Fix Assistant")

    st.markdown(
        '<div class="about-card">'
        "<h4>What is this tool?</h4>"
        "<p>The <strong>Bug Explanation &amp; Fix Assistant</strong> is an intelligent "
        "code-debugging tool that analyzes buggy source code snippets and error messages, "
        "identifies root causes, provides corrected code, and explains every fix in "
        "beginner-friendly language.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✨ Features")
        features = [
            "🔍 Automatic language detection",
            "🐛 Deep root-cause analysis",
            "🔧 Corrected code generation",
            "📖 Plain-English explanations with analogies",
            "🪜 Step-by-step debugging walkthroughs",
            "🛡️ Prevention tips & best practices",
            "📊 Confidence & limitation transparency",
            "⚖️ Side-by-side prompt version comparison",
        ]
        for f in features:
            st.markdown(f"- {f}")

        st.markdown("### 🌐 Supported Languages")
        for lang in get_supported_languages():
            st.markdown(f"- {lang}")

    with col2:
        st.markdown("### 🏗️ Technology Stack")
        tech = {
            "Frontend": "Streamlit",
            "AI Backend": "Google Gemini API",
            "Language Detection": "Custom heuristic engine",
            "Prompt Engineering": "Multi-version iterative refinement",
            "Response Parsing": "Structured JSON extraction",
        }
        for k, v in tech.items():
            st.markdown(f"- **{k}:** {v}")

        st.markdown("### 🧠 Prompt Engineering")
        st.markdown(
            "The assistant uses **three progressively refined prompt versions** "
            "to maximise analysis quality:\n\n"
            "1. **V1 — Basic:** Simple instruction-based prompt.\n"
            "2. **V2 — Structured:** Adds explicit output schema and severity rubric.\n"
            "3. **V3 / Final — Advanced:** Includes chain-of-thought reasoning, "
            "analogies, confidence calibration, and prevention guidance."
        )

        st.markdown("### ⚙️ Configuration")
        st.markdown(
            "1. Create a `.env` file in the project root.\n"
            "2. Add your API key: `GEMINI_API_KEY=your_key_here`\n"
            "3. Restart the app — it will switch from Demo to AI mode automatically."
        )

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.divider()
st.caption(
    "Built with ❤️ using Streamlit & Google Gemini · "
    "Bug Explanation & Fix Assistant v1.0"
)
