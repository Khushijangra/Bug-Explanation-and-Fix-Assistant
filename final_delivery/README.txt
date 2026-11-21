========================================================================
SCSE4041 MINI PROJECT — MILESTONE 2 FINAL DELIVERY PACKAGE
Project Title: Bug Explanation and Fix Assistant
Course: SCSE4041 Mini Project (12 Marks)
Team ID: PE-B01-21
Team Name: Deadlock
Batch Group: B01 - B12
========================================================================

TEAM MEMBERS:
- S24CSEU0666 - Khushi Jangra (Team Leader & Core AI Engine Architect)
- S24CSEU0682 - Janwi Singh (Prompt Engineering Specialist)
- S24CSEU0674 - Jaismeen Kaur (Streamlit Frontend UI/UX Developer)
- S24CSEU0668 - Kangna Bansal (Language & Syntax Parsing Specialist)
- S24CSEU1023 - Akharsh Tyagi (QA, Test Harness & Documentation Specialist)

DELIVERABLE CONTENTS:
1. Milestone_2_Submission_Report.pdf : Official 7-Section Academic Report
2. Technical_Report.pdf             : Concise 2-Page Technical Report (Sections A-H)
3. app.py                           : Streamlit Web Application (4 Views, 7 Output Sections)
4. modules/                         : Core Application Architecture (config, analyzer, detector, etc.)
5. prompts/                         : Versioned Prompt Engineering Artifacts (V1, V2, V3, Final)
6. test-data/                       : 17 Test Cases & Programmatically Logged Execution Results
7. tests/                           : Automated 4-Tier Test Harness (Unit, Integration, Semantic, Live AI)
8. screenshots/                     : 4 Genuine High-Resolution Live Application Run Screenshots
9. docs/                            : Architecture, Workflow Diagrams & Markdown Sources

QUICK START INSTRUCTIONS:
-------------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Run the Web Application:
   streamlit run app.py
   Open your browser at: http://localhost:8501

3. Run the Automated 4-Tier Test Suite:
   python tests/test_application.py
   (Executes 10 Unit Tests, 17 Integration Tests, 5 Semantic Tests, and AI status)

APPLICATION MODES & CLOUD DEPLOYMENT:
-------------------------------------
- STREAMLIT COMMUNITY CLOUD:
  Configured for instant one-click deployment at https://share.streamlit.io/
  Repository: https://github.com/Khushijangra/Bug-Explanation-and-Fix-Assistant
  Entry point: app.py (Branch: master)

- DEMO MODE (Default, Offline):
  Works completely out-of-the-box with zero API key dependencies across 17 calibrated scenarios.
  Guarantees zero-hallucination deterministic demonstration for academic grading.

- AI MODE (Online Google Gemini 2.0 Flash):
  Set APP_MODE=ai and configure GEMINI_API_KEY in Streamlit Secrets, sidebar, or .env.
========================================================================