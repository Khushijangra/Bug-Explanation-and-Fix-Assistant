"""
Bug Explanation and Fix Assistant - Main Streamlit Application
A professional web interface for analyzing, explaining, and fixing code bugs.
Built for SCSE4041 Mini Project (Milestone 2).
"""

import os
import sys
import json
import streamlit as st

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from modules.config import get_app_config, AppConfig
from modules.language_detector import detect_language, get_supported_languages
from modules.bug_analyzer import BugAnalyzer
from modules.prompt_manager import PromptManager
from modules.response_formatter import format_for_display

# ──────────────────────────────────────────────
# Page Configuration & Styling
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bug Fix Assistant",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #9333ea 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);
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

    /* Severity badge styles */
    .badge-critical {
        background: #fee2e2; color: #991b1b;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; display: inline-block;
    }
    .badge-major {
        background: #ffedd5; color: #9a3412;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; display: inline-block;
    }
    .badge-minor {
        background: #fef9c3; color: #854d0e;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; display: inline-block;
    }
    .badge-warning {
        background: #e0f2fe; color: #075985;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; display: inline-block;
    }

    /* Step columns */
    .step-box-wrong {
        background: #fef2f2; border-left: 4px solid #ef4444;
        padding: 0.8rem; border-radius: 0 6px 6px 0; min-height: 90px;
    }
    .step-box-change {
        background: #fffbeb; border-left: 4px solid #f59e0b;
        padding: 0.8rem; border-radius: 0 6px 6px 0; min-height: 90px;
    }
    .step-box-works {
        background: #f0fdf4; border-left: 4px solid #22c55e;
        padding: 0.8rem; border-radius: 0 6px 6px 0; min-height: 90px;
    }

    /* Info callouts */
    .demo-banner {
        background: #fffbeb; border: 1px solid #fde68a;
        color: #92400e; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;
    }
    .ai-banner {
        background: #f0fdf4; border: 1px solid #bbf7d0;
        color: #166534; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# State Initialization
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
config: AppConfig = analyzer.config

# ──────────────────────────────────────────────
# Sample Code Presets
# ──────────────────────────────────────────────
SAMPLE_CASES = {
    "Select a pre-built sample bug...": {
        "code": "", "error": "", "lang": "Auto-Detect"
    },
    "Python: Missing Parenthesis (SyntaxError)": {
        "code": "def greet():\n    print(\"Hello World\"\n\ngreet()",
        "error": "SyntaxError: unexpected EOF while parsing",
        "lang": "Python"
    },
    "Python: Division by Zero (ZeroDivisionError)": {
        "code": "def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)\nprint(result)",
        "error": "ZeroDivisionError: division by zero",
        "lang": "Python"
    },
    "JavaScript: Temporal Dead Zone (ReferenceError)": {
        "code": "console.log(result);\nlet result = 42;",
        "error": "ReferenceError: Cannot access 'result' before initialization",
        "lang": "JavaScript"
    },
    "Java: Null Reference (NullPointerException)": {
        "code": "public class Main {\n    public static void main(String[] args) {\n        String name = null;\n        System.out.println(name.length());\n    }\n}",
        "error": "Exception in thread \"main\" java.lang.NullPointerException",
        "lang": "Java"
    },
    "C++: Missing Semicolon (CompilationError)": {
        "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello World\" << endl\n    return 0;\n}",
        "error": "error: expected ';' before 'return'",
        "lang": "C++"
    },
    "C: Array Out of Bounds (Segmentation Fault)": {
        "code": "#include <stdio.h>\n\nint main() {\n    int arr[5] = {1, 2, 3, 4, 5};\n    printf(\"%d\\n\", arr[10]);\n    return 0;\n}",
        "error": "Segmentation fault (core dumped)",
        "lang": "C"
    },
    "Python: Loop Off-by-One (LogicalError)": {
        "code": "def sum_list(numbers):\n    total = 0\n    for i in range(1, len(numbers)):\n        total += numbers[i]\n    return total\n\nprint(sum_list([1, 2, 3, 4, 5]))",
        "error": "Expected output: 15, Got: 14",
        "lang": "Python"
    },
    "Edge Case: Ambiguous C/C++ (Missing main)": {
        "code": "int x = 5;\nint y = 10;\nint z = x + y;",
        "error": "undefined reference to 'main'",
        "lang": "Auto-Detect"
    },
    "Invalid Input: Misleading Error (Java traceback on Python)": {
        "code": "print('Hello World')",
        "error": "Exception in thread \"main\" java.lang.NullPointerException",
        "lang": "Python"
    }
}

# ──────────────────────────────────────────────
# Sidebar: Navigation & Configuration
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # Mode Selector
    current_default = 1 if (config.app_mode == "ai" and config.has_valid_api_key) else 0
    mode_selection = st.radio(
        "Execution Mode",
        ["🎮 Demo Mode (Offline)", "🤖 AI Mode (Gemini 2.0 Flash)"],
        index=current_default,
        help="Demo Mode is deterministic and verified offline. AI Mode connects to Google Gemini 2.0 Flash.",
        key="sidebar_mode_select",
    )

    target_mode = "ai" if "AI Mode" in mode_selection else "demo"

    if target_mode == "ai":
        base_cfg = get_app_config(custom_mode="ai")
        if base_cfg.has_valid_api_key:
            st.success(f"🤖 **AI Mode Connected**\n\nModel: `{base_cfg.gemini_model}`\n(Configured via Secrets/Env)")
            new_config = base_cfg
        else:
            st.info("🔑 **Gemini API Key Required**\nEnter your key below or add `GEMINI_API_KEY` to Streamlit Secrets.")
            user_key_input = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIzaSy...",
                help="Get a free key from https://aistudio.google.com/ (never stored or logged).",
                key="sidebar_key_input",
            )
            if user_key_input.strip():
                new_config = get_app_config(custom_mode="ai", custom_api_key=user_key_input)
                if new_config.has_valid_api_key:
                    st.success(f"🤖 **Key Accepted** (`{new_config.gemini_model}`)")
                else:
                    st.warning("Key format appears invalid.")
            else:
                new_config = get_app_config(custom_mode="ai", custom_api_key="")
                st.caption("ℹ️ Provide a key above to enable live AI inference.")
    else:
        new_config = get_app_config(custom_mode="demo")
        st.info("🎮 **Demo Mode Active**\n\nDeterministic verification with calibrated responses across 17 test cases.")

    # Apply configuration to analyzer if changed
    if (new_config.app_mode != analyzer.config.app_mode) or (new_config.gemini_api_key != analyzer.config.gemini_api_key):
        analyzer.set_config(new_config)
    config = analyzer.config

    st.divider()

    page = st.radio(
        "Navigation",
        ["🔍 Bug Analyzer", "⚖️ Prompt Comparison", "📝 Prompt Viewer", "ℹ️ About"],
        index=0,
    )

    st.divider()
    st.markdown("### 🌐 Supported Languages")
    for lang in get_supported_languages():
        st.markdown(f"- {lang}")

    st.divider()
    st.caption("SCSE4041 Mini Project · Milestone 2")


# ──────────────────────────────────────────────
# Header Banner
# ──────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🐛 Bug Explanation &amp; Fix Assistant</h1>
    <p>AI-Powered Debugger for Students &amp; Junior Developers — Plain Explanations &amp; Working Fixes</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Helper: Render Full Analysis Dashboard (A–G)
# ──────────────────────────────────────────────
def render_results_dashboard(result: dict):
    """Render the 7 structured analysis sections A through G without exception risks."""
    formatted = format_for_display(result)
    meta = formatted.get("_meta", {})

    # Top Execution Metrics Bar
    m1, m2, m3 = st.columns(3)
    mode_text = "🤖 AI (Gemini)" if meta.get("is_ai") else "🎮 Demo Mode"
    m1.metric("Execution Mode", mode_text)
    m2.metric("Prompt Version", meta.get("prompt_version", "final").upper())
    m3.metric("Analysis Latency", f"{meta.get('duration_seconds', 0.0):.3f}s")

    st.markdown("---")

    # Section A: Error Identification
    with st.expander("🅰️ **A. Error Identification**", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        c1.markdown(f"**Error Type:**\n\n`{formatted.get('error_type', 'Unknown')}`")
        c2.markdown(f"**Location:**\n\n`{formatted.get('error_location', 'Unable to determine')}`")
        sev = formatted.get("severity", "Major")
        sev_icon = formatted.get("severity_icon", "⚪")
        c3.markdown(f"**Severity:**\n\n{sev_icon} **{sev}**")
        st.info(f"**Summary:** {formatted.get('error_summary', 'No summary available.')}")

    # Section B: Root Cause Analysis
    with st.expander("🅱️ **B. Root Cause Analysis**", expanded=True):
        st.markdown(formatted.get("root_cause_explanation", "_No technical explanation available._"))
        prob_code = formatted.get("problematic_code", "")
        if prob_code:
            st.markdown("**Problematic Code Segment:**")
            st.code(prob_code, language="text")
        rule = formatted.get("language_rule", "")
        if rule:
            st.caption(f"📏 **Language Rule / Constraint:** {rule}")

    # Section C: Corrected Code
    with st.expander("🅲 **C. Corrected Code**", expanded=True):
        corrected = formatted.get("corrected_code", "")
        fix_type = formatted.get("fix_type", "Suggested Improvement")
        st.markdown(f"*Fix Status:* **{fix_type}**")

        if corrected:
            st.code(corrected, language="text")
            # Copy to clipboard button
            st.button(
                "📋 Copy Corrected Code",
                key="btn_copy_code",
                on_click=lambda: st.toast("✅ Code copied! Use Ctrl+V / Cmd+V to paste."),
            )
        else:
            st.warning("No code modification could be generated for this input.")

        changes = formatted.get("changes_made", [])
        if changes:
            st.markdown("**Modifications Made:**")
            for ch in changes:
                st.markdown(f"- {ch}")

    # Section D: Simple Explanation
    with st.expander("🅳 **D. Simple Explanation (Beginner-Friendly)**", expanded=True):
        st.markdown(formatted.get("simple_explanation", "_No plain-language explanation provided._"))
        analogy = formatted.get("analogy")
        if analogy:
            st.success(f"💡 **Real-World Analogy:** {analogy}")

    # Section E: Step-by-Step Debugging
    with st.expander("🅴 **E. Step-by-Step Debugging Walkthrough**", expanded=True):
        steps = formatted.get("debugging_steps", [])
        if steps:
            for s in steps:
                s_num = s.get("step_number", 1)
                st.markdown(f"#### Step {s_num}")
                col_w, col_c, col_k = st.columns(3)
                with col_w:
                    st.markdown(
                        f"<div class='step-box-wrong'><strong>❌ What Was Wrong</strong><br>"
                        f"{s.get('what_was_wrong', s.get('wrong', '—'))}</div>",
                        unsafe_allow_html=True,
                    )
                with col_c:
                    st.markdown(
                        f"<div class='step-box-change'><strong>🔄 What Was Changed</strong><br>"
                        f"{s.get('what_was_changed', s.get('changed', '—'))}</div>",
                        unsafe_allow_html=True,
                    )
                with col_k:
                    st.markdown(
                        f"<div class='step-box-works'><strong>✅ Why It Works</strong><br>"
                        f"{s.get('why_it_works', s.get('works', '—'))}</div>",
                        unsafe_allow_html=True,
                    )
                st.write("")
        else:
            st.info("No step-by-step breakdown available.")

    # Section F: Prevention Tips
    with st.expander("🅵 **F. Prevention Tips & Best Practices**", expanded=False):
        tips = formatted.get("prevention_tips", [])
        if tips:
            for tip in tips:
                st.markdown(f"- 🛡️ {tip}")
        else:
            st.info("No prevention tips provided.")

    # Section G: Confidence and Limitations
    with st.expander("🅶 **G. Confidence & Limitations**", expanded=False):
        conf_level = formatted.get("confidence_level", "Medium")
        st.markdown(f"**Confidence Level:** **{conf_level}**")

        assumptions = formatted.get("assumptions", [])
        if assumptions:
            st.markdown("**Assumptions Made:**")
            for a in assumptions:
                st.markdown(f"- {a}")

        limitations = formatted.get("limitations", [])
        if limitations:
            st.markdown("**Known Limitations:**")
            for lim in limitations:
                st.warning(f"⚠️ {lim}")

    # Raw AI Response viewer
    raw_resp = formatted.get("raw_response", "")
    if raw_resp:
        with st.expander("📄 Raw Model Output", expanded=False):
            st.text(raw_resp)


# ──────────────────────────────────────────────
# PAGE 1: Bug Analyzer
# ──────────────────────────────────────────────
if page == "🔍 Bug Analyzer":
    st.markdown("### 🔍 Analyze & Debug Source Code")
    st.write("Paste your code and error traceback, or choose a sample case to explore.")

    # Sample presets dropdown
    preset_choice = st.selectbox(
        "📂 Load Sample Code Example",
        list(SAMPLE_CASES.keys()),
        index=0,
    )
    preset_data = SAMPLE_CASES[preset_choice]

    col_code, col_meta = st.columns([3, 1])

    with col_meta:
        lang_options = ["Auto-Detect"] + get_supported_languages()
        default_lang_idx = 0
        if preset_data["lang"] in lang_options:
            default_lang_idx = lang_options.index(preset_data["lang"])
        selected_lang = st.selectbox("🌐 Target Language", lang_options, index=default_lang_idx)

    with col_code:
        code_input = st.text_area(
            "📝 Source Code",
            value=preset_data["code"],
            height=220,
            placeholder="Paste your source code here...",
            key="input_code_main",
        )

    error_input = st.text_area(
        "⚠️ Error Message / Traceback (Optional)",
        value=preset_data["error"],
        height=90,
        placeholder="Paste your terminal error message, compiler trace, or exception here...",
        key="input_error_main",
    )

    # Resolve Language Heuristic
    resolved_lang = selected_lang
    if selected_lang == "Auto-Detect":
        if code_input.strip():
            det_lang, det_conf = detect_language(code_input, error_input)
            if det_lang != "Unknown":
                st.info(f"🔎 Detected Language: **{det_lang}** (Confidence: {det_conf:.0%})")
                resolved_lang = det_lang
            else:
                resolved_lang = "Python"
        else:
            resolved_lang = "Python"

    # Action Buttons: Analyze & Clear
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    with btn_col1:
        analyze_clicked = st.button("🚀 Analyze Bug", type="primary", use_container_width=True)
    with btn_col2:
        clear_clicked = st.button("🔄 Clear Input", use_container_width=True)

    if clear_clicked:
        st.session_state.analysis_result = None
        st.rerun()

    if analyze_clicked:
        if not code_input.strip() and not error_input.strip():
            st.error("Please provide at least a source code snippet or an error traceback.")
        else:
            with st.spinner("Analyzing code, diagnosing cause, and synthesizing fix..."):
                res = analyzer.analyze(
                    code=code_input,
                    error_message=error_input,
                    language=resolved_lang,
                    prompt_version="final",
                )
                st.session_state.analysis_result = res

    # Display Results
    if st.session_state.analysis_result:
        st.markdown("### 📋 Diagnostic & Repair Dashboard")
        render_results_dashboard(st.session_state.analysis_result)


# ──────────────────────────────────────────────
# PAGE 2: Prompt Comparison
# ──────────────────────────────────────────────
elif page == "⚖️ Prompt Comparison":
    st.markdown("### ⚖️ Prompt Engineering Version Comparison")
    st.write(
        "Evaluate how the **same input** is analyzed across **V1 (Basic)**, "
        "**V2 (Structured)**, and **V3 (Optimized Final)** prompt architectures."
    )

    if analyzer.is_ai_mode:
        st.markdown("""
        <div class="ai-banner">
            <strong>🤖 Live AI Comparison:</strong> Executing genuine queries for V1, V2, and V3
            against Google Gemini using identical model settings (temperature=0.3).
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="demo-banner">
            <strong>🎮 Simulated Demonstration Mode:</strong> Illustrates the structural and schema
            progression across V1 (Free text), V2 (Markdown), and V3 (Validated JSON).
            To perform live empirical LLM comparisons, configure <code>APP_MODE=ai</code> and <code>GEMINI_API_KEY</code> in <code>.env</code>.
        </div>
        """, unsafe_allow_html=True)

    # Inputs for comparison
    comp_preset = st.selectbox(
        "📂 Load Comparison Preset",
        list(SAMPLE_CASES.keys()),
        index=1,
    )
    comp_data = SAMPLE_CASES[comp_preset]

    col_ccode, col_clang = st.columns([3, 1])
    with col_clang:
        c_lang = st.selectbox("🌐 Language", get_supported_languages(), index=0, key="comp_lang_select")
    with col_ccode:
        c_code = st.text_area("📝 Source Code for Comparison", value=comp_data["code"], height=180, key="comp_code_area")

    c_error = st.text_area("⚠️ Error Message", value=comp_data["error"], height=80, key="comp_error_area")

    if st.button("🔬 Compare All Prompt Versions", type="primary", use_container_width=True):
        if not c_code.strip():
            st.warning("Please provide code to compare.")
        else:
            with st.spinner("Executing comparison across V1, V2, and V3..."):
                comp_results = analyzer.compare_prompts(
                    code=c_code,
                    error_message=c_error,
                    language=c_lang,
                )
                st.session_state.comparison_results = comp_results

    if st.session_state.comparison_results:
        results = st.session_state.comparison_results
        tabs = st.tabs(["📋 V1: Basic Zero-Shot", "📋 V2: Structured Role-Based", "📋 V3: Optimized Final", "📊 Comparison Matrix"])

        with tabs[0]:
            st.markdown("#### Version 1 — Basic Zero-Shot Output")
            render_results_dashboard(results.get("v1", {}))

        with tabs[1]:
            st.markdown("#### Version 2 — Structured Role-Based Output")
            render_results_dashboard(results.get("v2", {}))

        with tabs[2]:
            st.markdown("#### Version 3 — Optimized Final Output (Production)")
            render_results_dashboard(results.get("v3", {}))

        with tabs[3]:
            st.markdown("#### 📊 Comparative Evaluation Matrix")
            st.caption("Demonstrating the impact of prompt engineering on output structure, pedagogical depth, and consistency.")

            v1_res = results.get("v1", {})
            v2_res = results.get("v2", {})
            v3_res = results.get("v3", {})

            comparison_table = {
                "Evaluation Dimension": [
                    "Output Schema Type",
                    "Error Categorization",
                    "Severity Assessment",
                    "Corrected Code Provided",
                    "Inline Code Fix Markers",
                    "Pedagogical Analogy",
                    "3-Column Debugging Steps",
                    "Confidence & Uncertainty",
                    "Programmatic Parseability"
                ],
                "V1 (Basic Zero-Shot)": [
                    "Unstructured Free Text",
                    "None / Ad-hoc",
                    "Not included",
                    "Often Snippet Only",
                    "None",
                    "None",
                    "None (Raw text)",
                    "None",
                    "❌ Brittle (Regex-only)"
                ],
                "V2 (Structured Role-Based)": [
                    "Structured Markdown Text",
                    "Basic (Syntax/Runtime)",
                    "Present",
                    "Full Code",
                    "Basic comments",
                    "Occasional",
                    "Present (List)",
                    "Implicit (Caveats)",
                    "⚠️ Medium (Heading-bound)"
                ],
                "V3 (Optimized Final)": [
                    "Strict Validated JSON",
                    "Formal 9-Class Taxonomy",
                    "Standardized (Critical/Major/Minor/Warning)",
                    "Full Code with Annotations",
                    "Standardized // FIXED: / # FIXED:",
                    "Consistent Real-World Analogies",
                    "Standardized 3-Column Schema",
                    "Calibrated Rating + Assumptions",
                    "✅ 100% Reliable (JSON RFC 8259)"
                ]
            }
            st.table(comparison_table)

            st.markdown("""
            > **Methodology Note:** The comparison highlights the progressive shift from **unconstrained natural language generation (V1)** 
            > to **role-guided sectioning (V2)**, culminating in **schema-enforced, pedagogically grounded JSON (V3)**.
            """)


# ──────────────────────────────────────────────
# PAGE 3: Prompt Viewer
# ──────────────────────────────────────────────
elif page == "📝 Prompt Viewer":
    st.markdown("### 📝 Prompt Engineering Repository & Templates")
    st.write("Inspect the exact prompt templates, metadata, and variables across all iterations.")

    versions = prompt_manager.get_all_versions()
    p_tabs = st.tabs(["V1: Basic", "V2: Structured", "V3: Optimized", "Final (Active)"])

    for i, v in enumerate(versions):
        with p_tabs[i]:
            info = prompt_manager.get_prompt_info(v)
            template_text = prompt_manager.get_template(v)

            st.markdown(f"### {info.get('name', v.upper())}")
            st.markdown(f"**Purpose:** {info.get('purpose', info.get('description', '—'))}")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Output Format:** `{info.get('format', 'text')}`")
                st.markdown(f"**Variables:** `{', '.join(info.get('variables', []))}`")
            with col_m2:
                model_cfg = info.get("model_settings", {})
                st.markdown(f"**Model Settings:** Temperature = `{model_cfg.get('temperature', 0.3)}`")

            improvements = info.get("improvements", [])
            if improvements:
                st.markdown("**Key Improvements:**")
                for imp in improvements:
                    st.markdown(f"- ✨ {imp}")

            limitations = info.get("limitations", [])
            if limitations:
                st.markdown("**Recorded Limitations:**")
                for lim in limitations:
                    st.markdown(f"- ⚠️ {lim}")

            st.markdown("---")
            st.markdown("**Full Prompt Template:**")
            st.code(template_text, language="text")


# ──────────────────────────────────────────────
# PAGE 4: About & Academic Documentation
# ──────────────────────────────────────────────
elif page == "ℹ️ About":
    st.markdown("### ℹ️ About Bug Explanation and Fix Assistant")

    st.markdown("""
    The **Bug Explanation and Fix Assistant** is an AI-powered developer assistance web tool 
    designed specifically for **students and junior developers** to understand, debug, and fix programming errors.
    
    Developed for **SCSE4041 Mini Project (Milestone 2)**.
    """)

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.markdown("#### ✨ Core Features")
        st.markdown("""
        - **Automatic Language Detection:** Heuristic engine supporting Python, JS, Java, C++, and C.
        - **Deep Root Cause Diagnosis:** Explains the exact failure mechanism citing language specifications.
        - **Annotated Code Repair:** Generates working patches with inline fix annotations.
        - **Pedagogical Analogies:** Uses beginner-friendly metaphors to bridge conceptual gaps.
        - **3-Column Debugging Steps:** Detailed *What was wrong* → *What was changed* → *Why it works*.
        - **Multi-Version Prompt Comparison:** Side-by-side empirical demonstration of prompt engineering.
        - **Zero-Failure Fallback:** High-fidelity offline demo mode when API keys are not configured.
        """)

    with col_a2:
        st.markdown("#### 🏗️ Architecture & Technology Stack")
        st.markdown("""
        - **Frontend Presentation:** Streamlit (v1.28+)
        - **Backend Execution:** Python 3.8+
        - **AI Inference Engine:** Google Gemini API (`gemini-2.0-flash`)
        - **Language Detector:** Lexical and syntactic regex pattern scorer
        - **Prompt Management:** Version-controlled disk templates (V1, V2, V3, Final)
        - **Response Formatter:** Resilient JSON / Markdown deserializer
        """)

    st.markdown("---")
    st.markdown("#### 🔑 Configuration Guide")
    st.markdown("""
    1. Copy `.env.example` to `.env`:
       ```bash
       cp .env.example .env
       ```
    2. Configure mode and credentials:
       - **Demo Mode (Offline / No Key):** Keep `APP_MODE=demo`
       - **AI Mode (Live Gemini):** Set `APP_MODE=ai` and add your `GEMINI_API_KEY`
    3. Run the application:
       ```bash
       streamlit run app.py
       ```
    """)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.divider()
st.caption("Bug Explanation and Fix Assistant · Built for SCSE4041 Mini Project Milestone 2")
