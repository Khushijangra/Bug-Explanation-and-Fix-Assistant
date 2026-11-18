"""
Packaging script for Milestone 2 Final Delivery
Assembles clean deliverables into final_delivery/ and generates final_delivery.zip
"""

import os
import shutil
import zipfile

BASE_DIR = r"c:\Users\Asus\OneDrive\Desktop\prompt\Bug-Explanation-and-Fix-Assistant"
DELIVERY_DIR = os.path.join(BASE_DIR, "final_delivery")
ZIP_PATH = os.path.join(BASE_DIR, "final_delivery.zip")

# Clean existing final_delivery directory if present
if os.path.exists(DELIVERY_DIR):
    shutil.rmtree(DELIVERY_DIR)
os.makedirs(DELIVERY_DIR, exist_ok=True)

# Define directories and files to copy
dirs_to_copy = [
    "modules",
    "prompts",
    "test-data",
    "tests",
    "docs",
]

files_to_copy = [
    "app.py",
    "requirements.txt",
    "README.md",
    "CHANGELOG.md",
    ".env.example",
    ".gitignore",
]

# Excluded names
EXCLUDED_PATTERNS = {
    ".env",
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "final_delivery",
    "final_delivery.zip",
    ".DS_Store",
    "Thumbs.db",
}

print("1. Assembling clean files into final_delivery/...")

for f in files_to_copy:
    src = os.path.join(BASE_DIR, f)
    dst = os.path.join(DELIVERY_DIR, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  Copied file: {f}")

for d in dirs_to_copy:
    src_dir = os.path.join(BASE_DIR, d)
    dst_dir = os.path.join(DELIVERY_DIR, d)
    if os.path.exists(src_dir):
        shutil.copytree(
            src_dir,
            dst_dir,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git*")
        )
        print(f"  Copied directory: {d}/")

# Copy PDFs to root of final_delivery as well for easy faculty access
m2_pdf_src = os.path.join(BASE_DIR, "docs", "milestone_2_report.pdf")
m2_pdf_dst = os.path.join(DELIVERY_DIR, "Milestone_2_Submission_Report.pdf")
if os.path.exists(m2_pdf_src):
    shutil.copy2(m2_pdf_src, m2_pdf_dst)

tech_pdf_src = os.path.join(BASE_DIR, "docs", "technical_report.pdf")
tech_pdf_dst = os.path.join(DELIVERY_DIR, "Technical_Report.pdf")
if os.path.exists(tech_pdf_src):
    shutil.copy2(tech_pdf_src, tech_pdf_dst)

print("\n2. Creating clean ZIP archive final_delivery.zip...")

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(DELIVERY_DIR):
        # Filter out any accidental unwanted directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_PATTERNS]
        for file in files:
            if file in EXCLUDED_PATTERNS or file.endswith(".pyc") or file.endswith(".tmp"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, DELIVERY_DIR)
            zipf.write(full_path, arcname=rel_path)

print(f"  Generated ZIP: {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")
print("Final delivery package completed successfully!")
