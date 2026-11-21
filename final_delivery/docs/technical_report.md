# Technical Report: Bug Explanation and Fix Assistant
**Course:** SCSE4041 Mini Project (Milestone 2) | **Team ID:** T-SCSE-C5-04 | **Date:** November 2026
**Team Roster:** S24CSEU0666 (Lead), S24CSEU0682, S24CSEU0674, S24CSEU0668, S24CSEU1023

---

### A. Project Overview
- **Problem Addressed:** Novice programmers struggle with cryptic compiler diagnostics and stack traces (e.g., `Segmentation fault`, `NullPointerException`, `unexpected EOF`) that report execution failures without explaining conceptual root causes or providing actionable fixes.
- **Target Users:** Undergraduate computer science students and junior software developers.
- **Purpose:** An AI-powered assistant that ingests multi-language source code and error messages, categorizes bugs via a 9-class taxonomy, provides verified code repairs, explains root causes with beginner analogies, offers step-by-step debugging walkthroughs, and compares prompt versions.

### B. System Architecture
The solution uses a decoupled 5-tier architecture:
1. **Presentation Layer (`app.py`):** Reactive Streamlit UI with 4 views (Analyzer, Prompt Comparison, Prompt Viewer, About) and 8 one-click presets.
2. **Configuration Engine (`modules/config.py`):** Central controller strictly enforcing `APP_MODE` (`demo` vs `ai`) and credential validation.
3. **Language Detection Engine (`modules/language_detector.py`):** Weighted lexical/syntactic analyzer with string-literal sanitization covering Python, JS, Java, C++, and C.
4. **Prompt Management Engine (`modules/prompt_manager.py`):** Versioned template loader for V1, V2, V3, and Final prompts.
5. **Response Parser & Validator (`modules/response_formatter.py`):** Deserializer with RFC 8259 JSON validation, Markdown fallback, and isolated Python AST syntax checks (`ast.parse`).
6. **Dual-Mode Orchestrator (`modules/bug_analyzer.py`):** Routes to Google Gemini 2.0 Flash in AI Mode or a 17-case deterministic offline engine in Demo Mode.

### C. Tools and Technologies
- **Frontend & Web Framework:** Streamlit (v1.58+) reactive web application.
- **Runtime Environment:** Python 3.8+ (tested on Python 3.13).
- **AI Model & Platform:** Google Gemini 2.0 Flash (`gemini-2.0-flash`) via Google AI Studio API (`temperature=0.3`, `max_output_tokens=4096`).
- **Core Libraries:** `google-generativeai`, `python-dotenv`, `reportlab`, `pypdf`, native `ast` module for syntax parsing.

### D. Prompt Engineering Progression
- **V1 (Basic Zero-Shot, 291 chars):** Simple prompt asking for bug identity and fix. *Limitation:* Unstructured text output, no formal taxonomy, brittle parsing.
- **V2 (Structured Role-Based, 1,566 chars):** Added expert debugging persona, beginner audience context, and markdown section headers. *Limitation:* Markdown parsing vulnerabilities, no strict confidence calibration.
- **V3 / Final (Optimized Few-Shot Schema, 4,119 chars):** Enforces strict RFC 8259 JSON output, 9-class error taxonomy, inline `# FIXED:` code markers, 3-column debugging steps (*what was wrong* -> *what was changed* -> *why it works*), real-world analogies, and explicit confidence/limitations scoring.

### E. Testing Methodology
- **Unit Testing:** 10 isolated tests verifying configuration, language detection across 5 languages, prompt loading, response parsing, and AST validation.
- **Demo-Mode Integration Testing:** 17 end-to-end scenarios (8 Normal, 5 Edge, 4 Invalid) exercising the full analysis pipeline.
- **Safe Semantic & Syntax Verification:** Python code patches validated via `ast.parse` and executed in isolated scopes to ensure bug resolution without secondary defects.
- **Live AI Verification:** Dedicated test tier that probes Gemini API connectivity when credentials are configured or honestly logs `NOT RUN` in Demo Mode.

### F. Actual Results
- **Unit Test Suite:** 10 / 10 Passed (100.0%).
- **Integration Test Suite:** 17 / 17 Passed (100.0%) across Normal (TC001–TC008), Edge (TC009–TC013), and Invalid (TC014–TC017) scenarios.
- **Operational Mode Distinction:** Demo Mode runs 100% offline with zero external network dependency; Live AI Mode requires `APP_MODE=ai` with `GEMINI_API_KEY`.
- **Code Quality:** 100% of generated Python fixes passed AST syntax parsing.

### G. System Limitations
1. **Static Analysis Horizon:** Evaluates code statically; cannot dynamically verify multi-threaded race conditions or hardware memory faults without sandboxed compilation.
2. **Language Ambiguity:** Short 1-line statements (e.g., `int x = 10;`) lacking headers share syntax across C, C++, and Java, requiring user manual selection.
3. **Multi-File Context:** Single-file input scope does not resolve cross-module package hierarchies in enterprise repositories.
4. **Live AI Quota:** Cloud inference depends on Gemini API key availability and rate quotas.

### H. Future Improvements
1. **Dockerized Execution Sandbox:** Containerized runtime (Docker/gVisor) to compile, link, and run student patches with exit code verification.
2. **Conversational Multi-Turn State:** Allow interactive follow-up questions regarding specific line numbers.
3. **IDE Plugin Distribution:** Package the core diagnostic engine as a lightweight VS Code extension.
