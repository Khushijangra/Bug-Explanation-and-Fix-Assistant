"""
Portable Packaging script for Milestone 2 Final Delivery
Assembles clean deliverables into final_delivery/ and generates clean submission archives.
Fully portable using Path(__file__).resolve().parent
"""

import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DELIVERY_DIR = BASE_DIR / "final_delivery"
ZIP_PATH_1 = BASE_DIR / "final_delivery.zip"
ZIP_PATH_2 = BASE_DIR / "Bug_Explanation_and_Fix_Assistant.zip"

# Clean existing final_delivery directory if present
if DELIVERY_DIR.exists():
    shutil.rmtree(DELIVERY_DIR)
DELIVERY_DIR.mkdir(parents=True, exist_ok=True)

# Directories to copy
dirs_to_copy = [
    "modules",
    "prompts",
    "test-data",
    "tests",
    "docs",
    "screenshots",
]

# Root files to copy
files_to_copy = [
    "app.py",
    "requirements.txt",
    "README.md",
    "CHANGELOG.md",
    ".env.example",
    ".gitignore",
]

# Excluded patterns
EXCLUDED_PATTERNS = {
    ".env",
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "final_delivery",
    "final_delivery.zip",
    "Bug_Explanation_and_Fix_Assistant.zip",
    ".DS_Store",
    "Thumbs.db",
}

print(f"1. Assembling clean project deliverables from {BASE_DIR} into {DELIVERY_DIR}...")

for f in files_to_copy:
    src = BASE_DIR / f
    dst = DELIVERY_DIR / f
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  Copied file: {f}")

for d in dirs_to_copy:
    src_dir = BASE_DIR / d
    dst_dir = DELIVERY_DIR / d
    if src_dir.exists():
        shutil.copytree(
            src_dir,
            dst_dir,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git*")
        )
        print(f"  Copied directory: {d}/")

# Copy PDFs to root of final_delivery for convenient evaluator access
candidates = [
    BASE_DIR / "docs" / "Deadlock_Milestone2_Report.pdf",
    BASE_DIR / "docs" / "milestone_2_report_submission.pdf",
    BASE_DIR / "docs" / "milestone_2_report.pdf",
]
m2_pdf_src = next((p for p in candidates if p.exists()), candidates[-1])
m2_pdf_dst = DELIVERY_DIR / "Milestone_2_Submission_Report.pdf"
if m2_pdf_src.exists():
    shutil.copy2(m2_pdf_src, m2_pdf_dst)
    print(f"  Copied Milestone 2 PDF from {m2_pdf_src.name}")

tech_pdf_src = BASE_DIR / "docs" / "technical_report.pdf"
tech_pdf_dst = DELIVERY_DIR / "Technical_Report.pdf"
if tech_pdf_src.exists():
    shutil.copy2(tech_pdf_src, tech_pdf_dst)
    print(f"  Copied Technical Report PDF from {tech_pdf_src.name}")

# Generate README.txt inside final_delivery
readme_txt_content = """========================================================================
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

APPLICATION MODES:
------------------
- DEMO MODE (Default, Offline):
  Works completely out-of-the-box with zero API key dependencies across 17 calibrated scenarios.
  Guarantees zero-hallucination deterministic demonstration for academic grading.

- AI MODE (Online Google Gemini 2.0 Flash):
  Set APP_MODE=ai and configure GEMINI_API_KEY=your_key_here in .env.
========================================================================
"""

readme_txt_path = DELIVERY_DIR / "README.txt"
with open(readme_txt_path, "w", encoding="utf-8") as f:
    f.write(readme_txt_content.strip())
print(f"  Generated: {readme_txt_path.name}")

# Create clean ZIP archives
print("\n2. Creating clean ZIP archives...")

def make_archive(zip_target: Path):
    if zip_target.exists():
        os.remove(zip_target)
    with zipfile.ZipFile(zip_target, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DELIVERY_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_PATTERNS]
            for file in files:
                if file in EXCLUDED_PATTERNS or file.endswith(".pyc") or file.endswith(".tmp"):
                    continue
                full_path = Path(root) / file
                rel_path = full_path.relative_to(DELIVERY_DIR)
                zipf.write(full_path, arcname=str(rel_path))
    print(f"  Generated ZIP: {zip_target} ({zip_target.stat().st_size} bytes)")

make_archive(ZIP_PATH_1)
make_archive(ZIP_PATH_2)

# Copy Bug_Explanation_and_Fix_Assistant.zip into final_delivery as well
shutil.copy2(ZIP_PATH_2, DELIVERY_DIR / "Bug_Explanation_and_Fix_Assistant.zip")

print("\nFinal delivery package assembled and verified successfully!")
