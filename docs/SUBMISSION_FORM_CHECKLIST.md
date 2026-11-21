# SCSE4041 Milestone 2 Submission Form Checklist

**Course:** SCSE4041 Mini Project (Milestone 2 — 12 Marks)  
**Team ID:** `PE-B01-21` | **Team Name:** `Deadlock` | **Batch Group:** `B01 - B12`  
**Project Title:** `Bug Explanation and Fix Assistant`  
**Team Leader:** `Khushi Jangra` (`S24CSEU0666`)  

---

| Q# | Field Label / Requirement | Verified Submission Value | Source of Verification | Ready to Submit? | Manual Action Remaining? |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **Q1** | Team ID (assigned after Milestone 1) | `PE-B01-21` | Official Milestone 1 Records | ✅ **READY** | None. Directly copy-paste. |
| **Q2** | Team Name as Given in Milestone 1 | `Deadlock` | Official Milestone 1 Records | ✅ **READY** | None. Directly copy-paste. |
| **Q3** | Project Title / Name | `Bug Explanation and Fix Assistant` | Codebase & Milestone 1 | ✅ **READY** | None. Directly copy-paste. |
| **Q4** | Team Leader Name | `Khushi Jangra` | Official Milestone 1 Records | ✅ **READY** | None. Directly copy-paste. |
| **Q5** | Team Leader Enrollment No. | `S24CSEU0666` | Official Milestone 1 Records | ✅ **READY** | None. Directly copy-paste. |
| **Q6** | Select your Group (Batch) | `B01-12` | Official Milestone 1 Records | ✅ **READY** | Select option `B01-12`. |
| **Q7** | Enrollment numbers of all team members (one per line; format: S24CSEU1234) | `S24CSEU0666`<br/>`S24CSEU0682`<br/>`S24CSEU0674`<br/>`S24CSEU0668`<br/>`S24CSEU1023` | Official Milestone 1 Roster | ✅ **READY** | Copy the 5 lines exactly. |
| **Q8** | Project Type (Deliverable) | `App with code` | Codebase architecture (`app.py`) | ✅ **READY** | Select option `App with code`. |
| **Q9** | Main AI tool and model used | `Gemini 2.0 Flash in Google AI Studio (gemini-2.0-flash)` | `modules/config.py`, `bug_analyzer.py` | ✅ **READY** | Directly copy-paste. |
| **Q10** | Number of prompts in final solution (1 ~ 50) | `1` | `prompts/final/prompt.txt` | ✅ **READY** | Enter `1` (The unified multi-step schema prompt). |
| **Q11** | Prototype link | `http://localhost:8501` | Active Streamlit server | ⚠️ **ACTION** | Enter `http://localhost:8501` or your public Streamlit Cloud deployment URL. |
| **Q12** | Git repository or Google Drive folder link | *[Your Team's GitHub / Drive URL]* | Team version control | ⚠️ **ACTION** | Paste your public GitHub or shared Drive link. |
| **Q13** | Share link to your reel (Drive / unlisted YouTube) | *[Your Video URL]* | Recorded video demo | ⚠️ **ACTION** | Paste video link with "Anyone with link can view". |
| **Q14** | Short Video and Reel length in seconds (90–150) | `105` | `docs/demo_reel_script.md` | ✅ **READY** | Enter `105`. |
| **Q15** | Supporting document type | `Technical Report` | `docs/technical_report.pdf` | ✅ **READY** | Select `Technical Report`. |
| **Q16** | Upload supporting document (PDF max 10MB, named: TeamName_DocumentType.pdf) | `Deadlock_TechnicalReport.pdf` (6.6 KB, 2 pages) | `docs/technical_report.pdf` | ✅ **READY** | Upload `Technical_Report.pdf` (or rename to `Deadlock_TechnicalReport.pdf`). |
| **Q17** | Number of test inputs in test table (minimum 10) | `17` | `test-data/test_cases.json`, `test_results.json` | ✅ **READY** | Enter `17` (8 Normal, 5 Edge, 4 Invalid). |
| **Q18** | Total prompt versions in iteration log (minimum 3) | `3` | `prompts/v1/`, `v2/`, `v3/` | ✅ **READY** | Enter `3` (V1 Zero-Shot, V2 Structured, V3 Optimized). |
| **Q19** | Prototype Status | `All modules working` | Automated test suite execution | ✅ **READY** | Select `All modules working`. |
| **Q20** | Names of working modules | 1. Code Input Module<br/>2. Error Input Module<br/>3. Programming Language Detection Module<br/>4. AI Debugging Module<br/>5. Root Cause Explanation Module<br/>6. Corrected Code Generation Module<br/>7. Step-by-Step Debugging Guidance Module<br/>8. Prompt Version Management Module<br/>9. Prompt Comparison Module<br/>10. Testing and Validation Module | Project Architecture (`modules/`) | ✅ **READY** | Copy the 10-module list. |
| **Q21** | Upload Milestone 2 PDF (maximum 10 MB) | `Deadlock_Milestone2_Report.pdf` (44.1 KB, 16 pages) | `docs/milestone_2_report_submission.pdf` | ✅ **READY** | Upload `Milestone_2_Submission_Report.pdf` (or rename to `Deadlock_Milestone2_Report.pdf`). |
| **Q22** | Main task of each team member (Enrollment - Name - Task) | `S24CSEU0666 - Khushi Jangra - Project Lead, System Architecture, Core AI Bug Analyzer Engine, Google Gemini 2.0 Flash API Integration, and Dual-Mode Runtime Logic`<br/>`S24CSEU0682 - Janwi Singh - Prompt Engineering Iterations (V1 Zero-Shot, V2 Structured, V3 Optimized Few-Shot), Error Taxonomy, and Prompt Metadata`<br/>`S24CSEU0674 - Jaismeen Kaur - Streamlit Frontend UI/UX, Multi-Page Layout (Analyzer, Comparison, Viewer), and 7-Section Results Dashboard`<br/>`S24CSEU0668 - Kangna Bansal - Heuristic Language Detector (Python/JS/Java/C++/C), RFC 8259 JSON Parser, and Python AST Syntax Validator`<br/>`S24CSEU1023 - Akharsh Tyagi - Automated Testing Suite (17 Normal/Edge/Invalid Test Cases), Empirical Prompt Comparison Logs, and Milestone 2 Documentation` | Section 7 Team Contribution Table | ✅ **READY** | Copy the 5 lines exactly. |
| **Q23** | Evaluator notes | 1. Dual-Mode Architecture: Demo Mode runs 100% offline with 17 verified test cases; AI Mode runs live Gemini 2.0 Flash (`gemini-2.0-flash`) via `GEMINI_API_KEY`.<br/>2. Automated Verification: Run `python tests/test_application.py` to verify 10 unit tests, 17 demo tests, and 5 semantic execution tests.<br/>3. Prompt Comparison: Evaluates V1, V2, and V3 side-by-side with 9-dimension comparative matrix. | Verified system architecture | ✅ **READY** | Copy the evaluator notes. |
| **Q24** | Confirmation | `I confirm` | Rubric requirement | ✅ **READY** | Select `I confirm`. |
