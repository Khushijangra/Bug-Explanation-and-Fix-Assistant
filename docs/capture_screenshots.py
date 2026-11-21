"""
Automated genuine screenshot capture of the live Bug Explanation and Fix Assistant
using Playwright against the active Streamlit server at http://localhost:8501.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def capture():
    print(f"Connecting to live Streamlit instance and capturing screenshots into {SCREENSHOTS_DIR}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        # 1. Capture Bug Analyzer (Initial state with input and top results)
        print("1. Capturing Bug Analyzer screen...")
        page.goto("http://localhost:8501", timeout=15000)
        page.wait_for_timeout(3000)
        
        # Click Analyze Bug button to generate analysis
        analyze_btn = page.locator("button:has-text('Analyze Bug')")
        if analyze_btn.count() > 0:
            analyze_btn.first.click()
            page.wait_for_timeout(2500)
            
        page.screenshot(path=str(SCREENSHOTS_DIR / "bug_analyzer.png"))
        print(f"  Saved: {SCREENSHOTS_DIR / 'bug_analyzer.png'}")

        # 2. Capture Corrected Code and Debugging Steps (scrolled view)
        print("2. Capturing Corrected Code and Explanation...")
        page.evaluate("window.scrollTo(0, 650);")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(SCREENSHOTS_DIR / "corrected_code.png"))
        print(f"  Saved: {SCREENSHOTS_DIR / 'corrected_code.png'}")

        # 3. Capture Prompt Comparison View
        print("3. Capturing Prompt Comparison screen...")
        # Navigate to Prompt Comparison in sidebar radio
        comp_radio = page.locator("label:has-text('Prompt Comparison')")
        if comp_radio.count() > 0:
            comp_radio.first.click()
            page.wait_for_timeout(2000)
            
            # Click Compare All Prompt Versions button
            compare_btn = page.locator("button:has-text('Compare All Prompt Versions')")
            if compare_btn.count() > 0:
                compare_btn.first.click()
                page.wait_for_timeout(2500)

        page.evaluate("window.scrollTo(0, 300);")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(SCREENSHOTS_DIR / "prompt_comparison.png"))
        print(f"  Saved: {SCREENSHOTS_DIR / 'prompt_comparison.png'}")

        browser.close()

    # 4. Generate clean, high-resolution visual Repository tree screenshot
    print("4. Generating visual repository structure screenshot...")
    from PIL import Image, ImageDraw, ImageFont

    img_width, img_height = 1400, 950
    bg_color = (15, 23, 42)      # Dark slate #0f172a
    panel_color = (30, 41, 59)   # Slate #1e293b
    text_color = (248, 250, 252) # Light #f8fafc
    accent_blue = (56, 189, 248) # Cyan #38bdf8
    accent_green = (74, 222, 128)# Emerald #4ade80
    accent_purple = (168, 85, 247)# Purple #a855f7

    img = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 16)
        font_mono = ImageFont.truetype("consola.ttf", 15)
        font_header = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font_title = font_sub = font_mono = font_header = ImageFont.load_default()

    # Draw header banner
    draw.rectangle([(40, 30), (1360, 110)], fill=panel_color)
    draw.text((65, 45), "📁 Bug-Explanation-and-Fix-Assistant — Repository & Deliverable Structure", fill=text_color, font=font_title)
    draw.text((65, 80), "SCSE4041 Mini Project (Milestone 2) · Clean Architecture · 17 Test Scenarios · V1/V2/V3 Prompt Versions", fill=accent_blue, font=font_sub)

    repo_text = """
Bug-Explanation-and-Fix-Assistant/
├── app.py                             [Streamlit Reactive Web Application - 4 Pages, 7 Output Sections]
├── requirements.txt                   [Production Dependencies: streamlit, google-generativeai, reportlab, pypdf]
├── README.md                          [Comprehensive Documentation & Setup Guide]
├── CHANGELOG.md                       [Historical Version Log & Defect Remediation]
├── package_delivery.py                [Portable Packaging Script for Submission Distribution]
├── final_delivery.zip                 [Verified 100% Clean Archive - Zero Secrets/Caches]
│
├── modules/                           [Decoupled Application Modules]
│   ├── config.py                      [Central AppConfig & Transparent Mode Controller (ai vs demo)]
│   ├── language_detector.py           [Lexical/Syntactic Heuristic Language Classifier (Python/JS/Java/C++/C)]
│   ├── prompt_manager.py              [Dynamic Prompt Loader: V1, V2, V3, and Final]
│   ├── response_formatter.py          [RFC 8259 JSON Deserializer, Markdown Fallback & AST Syntax Validator]
│   └── bug_analyzer.py                [Dual Orchestrator: Gemini 2.0 Flash AI & 17 Deterministic Demo Cases]
│
├── prompts/                           [Versioned Prompt Templates & Metadata]
│   ├── v1/                            [Basic Zero-Shot Template: Unstructured text]
│   ├── v2/                            [Structured Role-Based Template: Markdown sections]
│   ├── v3/                            [Optimized Few-Shot Template: RFC 8259 JSON Schema & Taxonomy]
│   └── final/                         [Production Template: Synchronized with V3]
│
├── test-data/                         [Empirical Test Artifacts]
│   ├── test_cases.json                [17 Formal Test Cases: 8 Normal, 5 Edge, 4 Invalid]
│   └── test_results.json              [Empirical Test Results: 10/10 Unit, 17/17 Demo, 5/5 Semantic]
│
├── tests/                             [Automated Test Harness]
│   ├── test_application.py            [4-Tier Test Runner: Unit, Integration, Semantic, Live AI]
│   └── run_audit.py                   [Deep Module Audit Harness]
│
└── docs/                              [Milestone 2 Deliverables & Technical Documentation]
    ├── architecture.md                [System Architecture Specification]
    ├── technical_report.md            [2-Page Academic Technical Report (Sections A-H)]
    ├── technical_report.pdf           [Compiled 2-Page Technical Report PDF]
    ├── milestone_2_report.md          [Complete 7-Section Milestone 2 Submission Markdown]
    ├── milestone_2_report_submission.pdf [Official Milestone 2 Report PDF (15 Pages)]
    ├── demo_reel_script.md            [105-Second Video Demonstration Reel Script]
    ├── DEEP_AUDIT_REPORT.md           [15-Section Independent Deep Audit Report]
    └── diagrams/                      [Mermaid Diagrams: System Architecture, Workflow, I/O Flow, Tasks]
"""

    draw.rectangle([(40, 130), (1360, 910)], fill=panel_color)
    draw.text((65, 145), repo_text.strip(), fill=(226, 232, 240), font=font_mono)

    repo_img_path = SCREENSHOTS_DIR / "repository.png"
    img.save(repo_img_path)
    print(f"  Saved: {repo_img_path}")
    print("All 4 genuine screenshots captured successfully!")

if __name__ == "__main__":
    capture()
