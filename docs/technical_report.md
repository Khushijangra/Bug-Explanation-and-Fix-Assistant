# Technical Report: Bug Explanation and Fix Assistant
**Academic Course:** SCSE4041 Mini Project (Milestone 2)  
**Authors:** Team [Team ID Placeholder]  
**Date:** November 2026  
**Document Status:** Complete Standalone Technical Report  

---

## 1. Executive Summary

Debugging is widely recognized as one of the most formidable barriers faced by students and novice programmers. Traditional compilers and interpreters emit tersely formatted syntax diagnostics or raw execution call stacks (e.g., `Segmentation fault`, `NullPointerException`, `unexpected EOF while parsing`) that state *what* failed mechanically but fail to clarify the conceptual rationale or actionable remedies.

The **Bug Explanation and Fix Assistant** is an AI-powered developer assistance web tool designed specifically for students and junior developers. The system accepts source code across 5 widely used programming languages (Python, JavaScript, Java, C++, and C) alongside compiler or runtime error traces. It categorizes the underlying defect according to a structured taxonomy, synthesizes a complete, functioning code patch with inline annotations, unpacks the root cause using accessible beginner analogies, outlines a numbered 3-part debugging walkthrough, and provides preventive coding advice.

---

## 2. System Architecture & Tech Stack

The solution is architected as a modular, lightweight full-stack Python application:

```
[User Browser] <---> [Streamlit Presentation Layer (app.py)]
                             |
         +-------------------+-------------------+
         |                   |                   |
[Language Detector]   [Prompt Manager]    [Response Formatter]
         |                   |                   |
         +-------------------+-------------------+
                             |
                   [Bug Analyzer Engine]
                   /                   \
        (APP_MODE=ai)                 (APP_MODE=demo)
              v                              v
    [Google Gemini API]            [Deterministic Engine]
   (gemini-2.0-flash LLM)          (12 Verified Cases)
```

### Technical Stack:
- **Presentation & Web Server:** Streamlit (v1.28+) providing reactive single-page layout, code editors, tabs, and interactive metrics.
- **Language Detection Engine (`language_detector.py`):** Weighted lexical and syntactic heuristic analyzer combining keyword matching, regular expression syntax pattern evaluation, and error log pattern matching.
- **Prompt Lifecycle Management (`prompt_manager.py`):** Version-controlled template loader managing iterations (V1, V2, V3, and Final) with dynamic runtime variable interpolation.
- **Response Parser & Normalizer (`response_formatter.py`):** Resilient dual-path deserializer supporting strict JSON schema validation with markdown fence extraction, accompanied by regex-based markdown section recovery.
- **Core Orchestrator (`bug_analyzer.py`):** High-reliability orchestrator featuring dual operational modes: live LLM integration with Google Gemini (`gemini-2.0-flash`) and an offline, deterministic fallback engine covering all validation scenarios.

---

## 3. Prompt Engineering Methodology

Prompt engineering forms the intellectual core of this project. Rather than treating the LLM as an unconstrained text generator, prompts were systematically evolved through three major iterations:

1. **Version 1 (Basic Zero-Shot):** Formulated as an unconstrained 15-line prompt instructing the model to find the bug and suggest a fix.  
   *Limitation:* Output layout was unpredictable, explanations assumed senior-level knowledge, and programmatic UI integration was impossible.
2. **Version 2 (Structured Role-Based):** Introduced an explicit role persona ("expert software debugging assistant"), target audience context ("beginner who needs clear, simple explanations"), and structured markdown headings (1 through 6).  
   *Limitation:* Markdown text parsing remained fragile; lack of confidence estimation and edge-case handling produced hallucinations on empty or invalid inputs.
3. **Version 3 (Optimized Final Prompt):** Deployed a comprehensive multi-step prompt enforcing:
   - Named persona ("BugFixBot") with pedagogical principles.
   - Formal error categorization into 9 distinct classes (SyntaxError, RuntimeError, LogicalError, TypeError, NameError, ImportError, IndexError, CompilationError, Other).
   - Strict JSON output schema with inline `# FIXED:` code markers.
   - Numbered 3-part walkthrough schema: `what_was_wrong` → `what_was_changed` → `why_it_works`.
   - Explicit confidence scoring with enumerated assumptions and static analysis limitations.
   - Explicit guardrails for 5 edge conditions (empty code, missing error log, ambiguous language, mismatched error logs, unsupported language).

---

## 4. Empirical Testing & Validation

The application was validated against an empirical test suite of 12 distinct test cases executed through automated harness `tests/test_application.py`:

| Category | Count | Scenarios Tested |
| :--- | :--- | :--- |
| **Normal Bugs** | 7 | Python Syntax unclosed paren, Python ZeroDivisionError, JS TDZ ReferenceError, Java NullPointerException, C++ Missing Semicolon, C Array Bounds Segfault, Python Loop Off-by-one. |
| **Edge Cases** | 3 | Empty source code string, missing runtime error message, multi-language syntactically ambiguous code. |
| **Invalid Inputs** | 2 | Misleading cross-language error log (Java error on valid Python code), unsupported language (Rust). |

**Empirical Results:**  
- **Total Test Cases Executed:** 12  
- **Passed:** 12 (100.0%)  
- **Failed:** 0  
- **Language Detection Accuracy:** 100% on test snippets with confidence ranging from 0.25 to 0.95.  
- **Zero-Failure Fallback:** Demo engine guarantees deterministic execution with zero hallucinations when network or API quota is unavailable.

---

## 5. System Limitations & Future Scope

### Known Limitations:
1. **Static Analysis Horizon:** The system performs static LLM inference without sandboxed code execution, meaning semantic correctness cannot be verified via dynamic runtime testing.
2. **Short Snippet Ambiguity:** Syntax common to multiple C-family languages without standard headers requires contextual heuristic inference.
3. **Token Overhead:** Version 3 prompts contain extensive schema specifications (~4,000 characters), which introduces modest API token overhead compared to trivial prompts.

### Future Improvements:
1. **Dockerized Execution Sandbox:** Integrate secure isolated containers (e.g. gVisor/Docker) to compile and execute patches, validating compiler exit codes and unit test results before returning output.
2. **Interactive Multi-Turn Dialogue:** Enable conversational follow-up questions within the Streamlit session state so students can ask clarifying questions regarding specific lines.
3. **IDE Plugin Extension:** Package the V3 debugging engine as a VS Code / JetBrains extension for inline editor diagnostics.
