# 🐛 Bug Explanation and Fix Assistant

An AI-powered developer assistance tool designed for **students and junior developers** to understand, debug, and fix programming errors with ease.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Model](https://img.shields.io/badge/LLM-Google%20Gemini-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Academic%20Use-green.svg)]()

---

## 🎯 Overview

Programming errors can be overwhelming for beginners. Standard compiler and runtime errors often present cryptically (e.g. `Segmentation fault`, `unexpected EOF while parsing`, `NullPointerException`), without explaining *why* they happened or how to fix them conceptually.

**Bug Explanation and Fix Assistant** bridges this gap:
1. **Identifies the cause** and categorizes the error (Syntax, Runtime, Logical, Type, etc.).
2. **Generates complete, working corrected code** with inline fix annotations.
3. **Explains the bug in beginner-friendly words**, utilizing intuitive analogies.
4. **Offers numbered, step-by-step debugging walkthroughs** (What was wrong → What was changed → Why it works).
5. **Provides actionable prevention tips** to build better programming habits.
6. **Compares different prompt engineering iterations (V1, V2, V3)** side-by-side to demonstrate the impact of prompt engineering.

---

## 🌐 Supported Programming Languages

- 🐍 **Python**
- ⚡ **JavaScript**
- ☕ **Java**
- 🔧 **C++**
- 🔩 **C**

*Includes automatic language detection with manual override.*

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
# Set to 'ai' to use Google Gemini API or 'demo' for deterministic demo mode
APP_MODE=demo

# Required if APP_MODE=ai (Get free key from https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Model name
GEMINI_MODEL=gemini-2.0-flash
```

> **Note on Demo Mode:** If no API key is provided, the application runs seamlessly in **Demo Mode**, offering deterministic, validated sample runs without fabricating AI responses.

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
│   ├── v1/                     # Version 1 (Basic Prompt)
│   │   ├── prompt.txt
│   │   └── metadata.json
│   ├── v2/                     # Version 2 (Structured Prompt)
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
│   ├── language_detector.py    # Multi-language heuristic detection engine
│   ├── bug_analyzer.py         # AI analysis engine & demo fallback orchestrator
│   ├── prompt_manager.py       # Prompt version lifecycle manager
│   └── response_formatter.py   # Multi-format parser (JSON & text) & UI normalizer
│
├── test-data/                  # Test Cases and Empirical Outputs
│   ├── test_cases.json         # 12 diverse test inputs (Normal, Edge, Invalid)
│   └── test_results.json       # Real execution results against the test suite
│
├── tests/                      # Automated Verification
│   ├── __init__.py
│   └── test_application.py     # Unit and integration test runner
│
└── docs/                       # Comprehensive Academic Documentation
    ├── architecture.md         # System architecture & component design
    ├── prompt_workflow.md      # Detailed prompt engineering analysis & evolution
    ├── testing_report.md       # Empirical testing report & validation log
    ├── milestone_2_report.md   # Complete Milestone 2 Submission Document
    ├── technical_report.md     # 2-page Standalone Technical Report
    ├── demo_reel_script.md     # 90-150 second video demonstration script
    └── diagrams/               # Text and Mermaid architectural diagrams
```

---

## 🧠 Prompt Engineering Evolution

Prompt engineering is the academic core of this project:

| Feature | V1 (Basic) | V2 (Structured) | V3 (Optimized Final) |
| :--- | :--- | :--- | :--- |
| **Paradigm** | Zero-Shot Request | Role-Based Prompting | Few-Shot Schema-Enforced Reasoning |
| **Role Persona** | Generic Assistant | Expert Debugging Assistant | "BugFixBot" with Educational Principles |
| **Output Target** | Unstructured Free Text | Markdown Sections | Validated Strict JSON Schema |
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
- **7 Normal Bugs**: Across Python, JS, Java, C++, and C (SyntaxError, ZeroDivisionError, TDZ ReferenceError, NullPointerException, Missing Semicolons, Buffer Overflows, Off-by-one errors).
- **3 Edge Cases**: Empty source code input, missing error message, ambiguous multi-language code.
- **2 Invalid Cases**: Misleading error messages (Java error paired with Python code), unsupported languages (Rust).

All test results are logged into `test-data/test_results.json`.

---

## 👥 Academic Milestone Information

- **Course:** SCSE4041 Mini Project
- **Milestone:** Milestone 2 (12 Marks)
- **Project:** Bug Explanation and Fix Assistant
- **Team ID:** [Team ID Placeholder]
- **Documentation:** See `docs/milestone_2_report.md` for the complete 7-section submission report.
