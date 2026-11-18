# System Architecture: Bug Explanation and Fix Assistant

## 1. System Overview

The **Bug Explanation and Fix Assistant** is an AI-powered developer assistance web tool designed specifically for students and junior developers. It accepts buggy source code across 5 programming languages (Python, JavaScript, Java, C++, C) and associated compiler or runtime errors, diagnoses root causes, generates complete corrected code with inline annotations, unpacks concepts using beginner-friendly analogies, and guides users with 3-part step-by-step debugging walkthroughs.

## 2. High-Level Architectural Diagram

```
+───────────────────────────────────────────────────────────────────────────────────+
│                            STREAMLIT FRONTEND (app.py)                            │
│  +─────────────────────────+ +─────────────────────────+ +──────────────────────+  │
│  │   Code & Error Input    │ │   Language Selector     │ │  Results Dashboard   │  │
│  │   (Presets & Custom)    │ │   & Auto-Detect Badge   │ │     (Sections A-G)   │  │
│  +------------+------------+ +------------+------------+ +----------▲-----------+  │
+---------------|---------------------------|-------------------------|-------------+
                │                           │                         │
                v                           v                         │
+---------------------------------------------------------------------+-------------+
|                         APPLICATION MODULES SUBSYSTEM                             |
|  +─────────────────────────────────+      +─────────────────────────────────────+ │
|  |   modules/config.py             |      |     modules/response_formatter.py   | │
|  |   Central Config & Mode State   |      |     JSON Deserializer & UI Mapper   | │
|  +─────────────────+───────────────+      +──────────────────▲──────────────────+ │
|                    │                                         │                    │
|                    v                                         │                    │
|  +─────────────────────────────────+      +──────────────────+──────────────────+ │
|  |   modules/language_detector.py  |      |       modules/bug_analyzer.py       | │
|  |   Heuristic Regex & Keyword     |      |   AI Orchestrator & Dual Backend    | │
|  +─────────────────+───────────────+      +──────────────────▲──────────────────+ │
|                    │                                         │                    │
|                    v                                         │                    │
|  +─────────────────────────────────+                         │                    │
|  |   modules/prompt_manager.py     |─────────────────────────┘                    │
|  |   Templates (V1, V2, V3, Final) │                                              │
|  +─────────────────────────────────+                                              │
+-----------------------------------------------------------------------------------+
                                             │
               +─────────────────────────────+─────────────────────────────+
               │                                                           │
               v                                                           v
+─────────────────────────────────────────────+   +───────────────────────────────────+
|         Google Gemini API Backend           |   |    Deterministic Verification     |
|          (gemini-2.0-flash Model)           |   |          Demo Engine              |
|        Live Inference via API Key           |   |   (17 Verified Reference Cases)   |
+─────────────────────────────────────────────+   +───────────────────────────────────+
```

## 3. Subsystem Breakdown

### 3.1 Presentation Layer (`app.py`)
- **Technology:** Streamlit (v1.28+)
- **Responsive Layout:** Laptop and desktop-optimized layout featuring custom CSS badges for severity (`Critical`, `Major`, `Minor`, `Warning`), 3-color step boxes (Wrong / Changed / Works), and mode banners.
- **Interactive Controls:**
  - Code Editor with sample presets dropdown (Python, JS, Java, C++, C, Edge cases).
  - Error Input text area.
  - Language dropdown with heuristic Auto-Detection badge displaying real-time confidence percentage.
  - "Clear Input" and "Analyze Bug" action triggers.
  - Multi-version Prompt Comparison View (side-by-side tabs and comparative matrix).
  - Prompt Viewer and Academic About pages.

### 3.2 Configuration Subsystem (`modules/config.py`)
- **Central Source of Truth:** Manages `APP_MODE` (`ai` vs `demo`), `GEMINI_API_KEY`, `GEMINI_MODEL`, and timeouts.
- **Mode Decoupling:** `APP_MODE=demo` guarantees deterministic offline execution regardless of whether an API key exists in the environment. `APP_MODE=ai` requires a valid key, displaying clear warnings if credentials are missing rather than silently falling back.

### 3.3 Language Detection Engine (`modules/language_detector.py`)
- **Heuristic Pattern Scoring:** Weighted evaluator scanning keywords (1.0 pt), syntax regexes (1.5 pts), and error traceback patterns (2.0 pts).
- **C vs C++ Disambiguation:** Checks for C++ specific tokens (`cout`, `std::`, `iostream`, `nullptr`, `auto`) to prevent misclassification.
- **Confidence Calibration:** Computes score saturation and outputs calibrated confidence between 0.25 and 0.95.

### 3.4 Prompt Lifecycle Subsystem (`modules/prompt_manager.py`)
- **Version Isolation:** Dedicated filesystem directories for `prompts/v1/`, `prompts/v2/`, `prompts/v3/`, and `prompts/final/`.
- **Metadata Management:** Loads and normalizes version metadata, objectives, parameters, and limitations.

### 3.5 Core Orchestrator (`modules/bug_analyzer.py`)
- **Dual-Engine Routing:** Directs requests to either live Gemini inference or the deterministic demo engine based on configuration.
- **Resilience:** Implements timeouts, quota limit interception, and friendly user error handling.
- **Multi-Prompt Comparator:** Runs parallel model calls in AI mode, and provides structurally distinct pedagogical progression in Demo mode.

### 3.6 Response Formatting & Deserialization (`modules/response_formatter.py`)
- **Multi-Format Deserialization:** Primary JSON decoder with markdown code-fence extraction; secondary fallback regex heading extractor for unstructured model outputs.
- **Dual-Access API:** Returns both nested section dictionaries and flat convenience keys to ensure calling code never encounters missing-attribute errors.
- **Syntax Validator:** Isolated Python AST syntax checker (`ast.parse`) for evaluating the validity of synthesized code without executing arbitrary host code.

## 4. Data Flow

```
1. Input Payload (Code, Error Message, Target Language)
       │
       ▼
2. modules/config.py (Validates active mode and settings)
       │
       ▼
3. modules/language_detector.py (Detects/Validates Language + Confidence)
       │
       ▼
4. modules/prompt_manager.py (Binds variables to prompt template)
       │
       ▼
5. modules/bug_analyzer.py (Executes Gemini query or calibrated demo pattern)
       │
       ▼
6. modules/response_formatter.py (Parses JSON/Markdown + Validates Python AST)
       │
       ▼
7. app.py (Renders 7 Dashboard Sections A–G)
```
