# 🐛 Bug Explanation and Fix Assistant

An AI-powered developer assistance tool designed for **students and junior developers** to understand, debug, and fix programming errors with ease.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LLM](https://img.shields.io/badge/LLM-Google%20Gemini%202.0-orange.svg)](https://ai.google.dev/)
[![Status](https://img.shields.io/badge/Milestone%202-Verified%20100%25-brightgreen.svg)]()

---

## 🎯 Overview

Programming errors can be overwhelming for beginners. Standard compiler and runtime errors often present cryptically (e.g. `Segmentation fault`, `unexpected EOF while parsing`, `NullPointerException`), without explaining *why* they happened or how to fix them conceptually.

**Bug Explanation and Fix Assistant** bridges this gap:
1. **Identifies the cause** and categorizes the defect according to a formal 9-class error taxonomy.
2. **Generates complete, working corrected code** with inline `# FIXED:` or `// FIXED:` annotations.
3. **Explains the bug in beginner-friendly words**, utilizing intuitive real-world analogies.
4. **Offers numbered, step-by-step debugging walkthroughs** (*What was wrong* → *What was changed* → *Why it works*).
5. **Provides actionable prevention tips** to build better programming habits.
6. **Compares different prompt engineering iterations (V1, V2, V3)** side-by-side to demonstrate the impact of prompt engineering.
7. **Includes high-fidelity demo mode** allowing full interactive evaluation and offline verification with zero API key dependencies.

---

## 🌐 Supported Programming Languages

- 🐍 **Python**
- ⚡ **JavaScript**
- ☕ **Java**
- 🔧 **C++**
- 🔩 **C**

*Includes automatic heuristic language detection with real-time confidence metrics and manual override.*

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd Bug-Explanation-and-Fix-Assistant
```

### 2. Setup Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your mode:
```env
# Set to 'demo' for offline deterministic verification or 'ai' for live Google Gemini
APP_MODE=demo

# Required ONLY if APP_MODE=ai (Get free key from https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Model name (default: gemini-2.0-flash)
GEMINI_MODEL=gemini-2.0-flash
```

> **Note on Demo Mode:** When `APP_MODE=demo`, the application runs completely offline using a verified deterministic engine across 17 calibrated scenarios. It never fails due to missing keys or network boundaries.

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Repository Structure

```
Bug-Explanation-and-Fix-Assistant/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation and quick start
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version history and evolution
│
├── prompts/                    # Versioned Prompt Engineering Artifacts
│   ├── v1/                     # Version 1 (Basic Zero-Shot Prompt)
│   │   ├── prompt.txt
│   │   └── metadata.json
│   ├── v2/                     # Version 2 (Structured Role-Based Prompt)
│   │   ├── prompt.txt
│   │   └── metadata.json
│   ├── v3/                     # Version 3 (Optimized Final Prompt)
│   │   ├── prompt.txt
│   │   └── metadata.json
│   └── final/                  # Final production prompt (= V3)
│       ├── prompt.txt
│       └── metadata.json
│
├── modules/                    # Application Core Modules
│   ├── __init__.py
│   ├── config.py               # Central configuration & mode source of truth
│   ├── language_detector.py    # Multi-language heuristic detection engine
│   ├── bug_analyzer.py         # AI analysis engine & demo fallback orchestrator
│   ├── prompt_manager.py       # Prompt version lifecycle manager
│   └── response_formatter.py   # Multi-format parser (JSON & text) & AST validator
│
├── test-data/                  # Test Cases and Empirical Outputs
│   ├── test_cases.json         # 17 diverse test inputs (Normal, Edge, Invalid)
│   └── test_results.json       # Real execution results against the test suite
│
├── tests/                      # Automated Verification
│   ├── __init__.py
│   └── test_application.py     # Unit and integration test runner (17 cases)
│
└── docs/                       # Comprehensive Academic Documentation
    ├── architecture.md         # System architecture & component design
    ├── prompt_workflow.md      # Detailed prompt engineering analysis & evolution
    ├── testing_report.md       # Empirical testing report & validation log
    ├── milestone_2_report.md   # Complete Milestone 2 Submission Document (7 Sections)
    ├── technical_report.md     # 2-page Standalone Technical Report
    ├── demo_reel_script.md     # 90-150 second video demonstration script
    └── diagrams/               # Valid Mermaid architectural and workflow diagrams
```

---

## 🧠 Prompt Engineering Evolution

Prompt engineering is the academic core of this project:

| Feature | V1 (Basic Zero-Shot) | V2 (Structured Role-Based) | V3 (Optimized Final) |
| :--- | :--- | :--- | :--- |
| **Paradigm** | Zero-Shot Request | Role-Based Prompting | Few-Shot Schema-Enforced Reasoning |
| **Role Persona** | Generic Assistant | Expert Debugging Assistant | "BugFixBot" with Educational Principles |
| **Output Target** | Unstructured Free Text | Markdown Headings | Validated Strict JSON Schema |
| **Error Taxonomy**| None | High-level (Syntax/Runtime) | 9 Distinct Categories |
| **Pedagogy** | Minimal fix advice | Beginner explanations | Conceptual breakdown + Real-world analogy |
| **Debugging Steps**| None | High-level bullet points | 3-Part Walkthrough (Wrong / Changed / Works) |
| **Uncertainty** | None | Generic caveat | Confidence Score + Assumptions + Limitations |
| **Edge Cases** | Fails / Hallucinates | Partial degradation | Explicit handling rules for 5 edge conditions |

---

## 🧪 Testing & Empirical Validation

Run the automated test suite:
```bash
python tests/test_application.py
```

The suite validates:
- **10 Unit Tests:** AppConfig loading, language detection heuristics, prompt template lifecycle, dual-access response formatting, and isolated Python AST syntax checks.
- **17 Integration Tests:** Covering 8 normal bugs, 5 edge conditions (empty inputs, missing errors, language ambiguity, long scripts, Unicode smart quotes), and 4 invalid inputs (cross-language mismatches, unsupported languages, invalid types, fallback recovery).
- **Quality Checks:** All synthesized Python code fixes pass isolated AST parsing (`ast.parse`) without executing arbitrary host code.

All test results are logged into `test-data/test_results.json`.

---

## 👥 Academic Milestone Information

- **Course:** SCSE4041 Mini Project
- **Milestone:** Milestone 2 (12 Marks)
- **Project Title:** Bug Explanation and Fix Assistant
- **Team ID:** PE-B01-21
- **Team Name:** Deadlock
- **Team Leader:** Khushi Jangra (S24CSEU0666)
- **Batch Group:** B01 - B12
- **Documentation:** See `docs/milestone_2_report.md` for the complete 7-section submission report.

### Team Roster & Responsibilities
| Enrollment Number | Member Name | Role & Responsibility |
| :--- | :--- | :--- |
| **S24CSEU0666** | Khushi Jangra (Lead) | Project Lead, System Architecture, Core AI Bug Analyzer Engine, Google Gemini 2.0 Flash API Integration, and Dual-Mode Runtime Logic |
| **S24CSEU0682** | Janwi Singh | Prompt Engineering Iterations (V1 Zero-Shot, V2 Structured, V3 Optimized Few-Shot), Error Taxonomy, and Prompt Metadata |
| **S24CSEU0674** | Jaismeen Kaur | Streamlit Frontend UI/UX, Multi-Page Layout (Analyzer, Comparison, Viewer), and 7-Section Results Dashboard |
| **S24CSEU0668** | Kangna Bansal | Heuristic Language Detector (Python/JS/Java/C++/C), RFC 8259 JSON Parser, and Python AST Syntax Validator |
| **S24CSEU1023** | Akharsh Tyagi | Automated Testing Suite (17 Normal/Edge/Invalid Test Cases), Empirical Prompt Comparison Logs, and Milestone 2 Documentation |
