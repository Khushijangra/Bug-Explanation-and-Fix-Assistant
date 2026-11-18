# Changelog

All notable changes to the Bug Explanation and Fix Assistant project.

## [2.0.0] - 2026-11-18 (Milestone 2 Final Delivery)

### Fixed
- **Critical UI Crash in `app.py`:** Resolved `AttributeError: 'str' object has no attribute 'get'` by updating `format_for_display` to provide an idempotent, dual-access dictionary supporting both nested dictionary sections (`error_identification`, `corrected_code`, `root_cause`, `simple_explanation`, `debugging_steps`) and flattened convenience keys (`error_type`, `severity`, `corrected_code`, etc.).
- **Prompt Viewer Crash:** Implemented missing methods in `PromptManager` (`get_prompt_info()`, `get_template()`) resolving `AttributeError` when viewing prompt templates.
- **Application Mode Detection:** Centralized configuration logic into `modules/config.py` with `APP_MODE` as the primary source of truth. Fixed sidebar displaying AI mode when `APP_MODE=demo` was set.
- **Silent Fallback Elimination:** Prevented AI Mode from silently falling back to Demo Mode while misrepresenting AI execution; clear configuration warnings and errors are now displayed.
- **Prompt Comparison:** Added distinct simulated progression responses for V1 (free text), V2 (Markdown), and V3 (JSON) in Demo Mode with explicit simulation tagging, and parallel multi-prompt execution in AI Mode.

### Added
- **Sample Code Presets Dropdown:** Added interactive sample bug presets in `app.py` for Python Syntax, ZeroDivision, JS TDZ, Java NullPointer, C++ Semicolon, C Array Bounds, Loop Off-by-one, and edge cases.
- **Clear Input Action:** Added "Clear Input" button resetting code and error inputs.
- **Central Configuration Module (`modules/config.py`):** Unified dataclass managing mode state, credentials, timeouts, and model parameters.
- **Expanded Test Suite (17 Test Cases):** Added 5 new test cases (JavaScript undefined variable, very long source code, typographic Unicode smart quotes, invalid input types, and parser fallback recovery).
- **Isolated AST Syntax Validation:** Added `validate_python_syntax` using Python `ast.parse` to verify that synthesized Python fixes are syntactically valid without executing arbitrary code on the host.
- **Live AI Verification Tier:** Added dedicated test suite tier checking AI mode availability and honestly reporting `NOT RUN` when API keys are unconfigured.
- **Complete Diagram Suite:** Added valid Mermaid diagrams for System Architecture, Prompt Workflow, Application Input-Output Flow, and Task Decomposition in `docs/diagrams/`.
- **Milestone 2 PDF & Technical Report PDF Generation:** Added automated PDF compilation scripts and generated standalone PDFs.
- **Final Delivery Package:** Created clean `final_delivery/` directory and `final_delivery.zip` archive.

### Security
- Verified `.env` exclusion from Git tracking.
- Ensured `.env.example` contains only safe placeholder values.
- Cleaned Git tracking of temporary files.
- Safe static AST code analysis without host code execution.
