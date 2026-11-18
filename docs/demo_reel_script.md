# Video Demonstration Script: Bug Explanation and Fix Assistant

**Project:** Bug Explanation and Fix Assistant (SCSE4041 - Milestone 2)  
**Target Video Duration:** 105 seconds (Within 90–150 seconds range)  
**Format:** Screen recording with voiceover narration  
**Recorded Quality:** 1080p 60fps  

---

## Storyboard & Narration Breakdown

```
+-----------------------------------------------------------------------------------------+
| Timecode  | Segment                  | Screen Display                | Audio Narration  |
+-----------------------------------------------------------------------------------------+
| 00:00-00:12 | 1. Problem Introduction | Terminal with cryptic errors  | Voiceover Intro  |
| 00:12-00:45 | 2. Prompt Experiment    | Prompt Comparison View        | Prompt Analysis  |
| 00:45-01:30 | 3. Live App Demo        | Streamlit Interactive UI      | Live Workflow    |
| 01:30-01:45 | 4. Summary & Future Work| Summary Slide & Architecture  | Conclusion       |
+-----------------------------------------------------------------------------------------+
```

---

### Segment 1: Problem Introduction (00:00 – 00:12 | ~12 seconds)

- **Visual on Screen:**  
  A dark terminal split-screen displaying cryptic compiler errors: a C++ `error: expected ';' before 'return'`, a Python `SyntaxError: unexpected EOF while parsing`, and a Java `java.lang.NullPointerException`.
- **Narration (Spoken clearly):**  
  *"For students and junior developers, cryptic compiler errors and runtime stack traces are intimidating roadblocks. Traditional compilers tell you THAT code crashed, but rarely explain WHY in plain English or HOW to fix it. Today, we introduce the Bug Explanation and Fix Assistant."*

---

### Segment 2: The Prompt Engineering Experiment (00:12 – 00:45 | ~33 seconds)

- **Visual on Screen:**  
  Navigate to the **📊 Prompt Comparison** tab in the Streamlit application. Enter TC001 (`print("Hello World"` with missing parenthesis). Click **Compare All Prompt Versions**.
- **Camera Focus:**  
  Pan across the tabs: V1 (Basic), V2 (Structured), V3 (Optimized), and the Summary Comparison Table.
- **Narration (Spoken clearly):**  
  *"Prompt engineering is the core academic foundation of our project.  
  In **Version 1**, a basic zero-shot prompt produces unformatted text with inconsistent terminology.  
  In **Version 2**, adding role context and markdown headers improved organization, but text parsing remained fragile for automated user interfaces.  
  In **Version 3**, our optimized prompt enforces a strict 9-class error taxonomy, beginner-friendly analogies, and a validated JSON schema with explicit confidence scoring. Looking at our summary table, Version 3 guarantees 100% parseability and structured pedagogical guidance."*

---

### Segment 3: Working Application Demonstration (00:45 – 01:30 | ~45 seconds)

- **Visual on Screen:**  
  Switch to the **🔍 Bug Analyzer** page.
  1. **Demo 1 (Auto-Detection & Fix):** Paste a Python snippet with an unclosed parenthesis. Notice the Auto-Detect badge instantly display `Python (Confidence: 88%)`.
  2. Click **Analyze Bug**. The loading spinner activates and resolves in a fraction of a second.
  3. Expand **A. Error Identification**: Point out the red `Critical` badge, location `Line 2`, and clear summary.
  4. Expand **C. Corrected Code**: Click the **📋 Copy Corrected Code** button; point out the inline `# FIXED:` annotation.
  5. Expand **D. Simple Explanation**: Highlight the intuitive shoe box / door analogy.
  6. Expand **E. Step-by-Step Debugging**: Show the 3 columns: *What was wrong* → *What was changed* → *Why it works*.
  7. **Demo 2 (Edge Case Handling):** Clear the input box and click Analyze with empty code. Show the system gracefully detecting `InvalidInput` without crashing.
- **Narration (Spoken clearly):**  
  *"Now let's see the application in action.  
  We paste a Python function with an unclosed parenthesis. The system automatically detects Python with high confidence.  
  Clicking 'Analyze Bug' produces our structured dashboard:  
  First, Error Identification classifies this as a Critical Syntax Error.  
  Next, the Corrected Code section supplies complete, working code with inline fix annotations and a one-click copy button.  
  Under Simple Explanation, students read an intuitive real-world analogy rather than confusing jargon.  
  The step-by-step debugging walkthrough breaks down the change mechanically into three clear pillars: what was wrong, what changed, and why it works.  
  Furthermore, our automated suite of 12 test cases covers edge cases—like empty inputs, ambiguous code, and cross-language misleading errors—with a 100% pass rate."*

---

### Segment 4: Progress, Architecture & Future Work (01:30 – 01:45 | ~15 seconds)

- **Visual on Screen:**  
  Display the system architecture slide showing Streamlit frontend, modular Python backend, and dual-mode Google Gemini / deterministic fallback engine. Show the GitHub repository with clean structure and verified test logs.
- **Narration (Spoken clearly):**  
  *"All 10 application modules are fully functional and verifiable locally or in the cloud. For future milestones, we plan to integrate a Dockerized sandboxed code execution environment to compile and execute patches live. Thank you for watching!"*

---

## Recording Checklist
- [x] Application running locally (`streamlit run app.py`)
- [x] Resolution set to 1920x1080
- [x] Browser zoom at 100% or 110% for crisp readability
- [x] Sample inputs pre-saved for smooth copy-pasting
- [x] Audio microphone tested for noise cancellation
