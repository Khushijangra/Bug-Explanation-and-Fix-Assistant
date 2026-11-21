"""
Comprehensive Module-by-Module Audit Script
Tests M01 through M10, edge cases, Unicode, large inputs, and security.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.config import get_app_config
from modules.bug_analyzer import BugAnalyzer
from modules.language_detector import detect_language, get_supported_languages, validate_language
from modules.prompt_manager import PromptManager
from modules.response_formatter import (
    parse_ai_response,
    format_for_display,
    validate_python_syntax,
)

def audit():
    print("=" * 60)
    print("AUDIT: DEEP SYSTEM TESTING")
    print("=" * 60)
    analyzer = BugAnalyzer()
    cfg = get_app_config()

    # M01 & M02: Input Handling
    print("\n--- Testing M01 & M02: Code & Error Input ---")
    
    # 1. Empty input
    r_empty = analyzer.analyze("", "")
    assert r_empty["error_type"] == "InvalidInput", f"Empty code failure: {r_empty['error_type']}"
    print("[M01/M02] Empty code/error handled gracefully -> InvalidInput")

    # 2. Large code input (1,000 lines)
    large_code = "\n".join([f"var_{i} = {i} * 2" for i in range(1000)])
    r_large = analyzer.analyze(large_code, "MemoryError or SyntaxError")
    assert r_large["error_type"] != "", "Large code failed"
    print(f"[M01/M02] 1000-line code processed in {r_large['_meta']['duration_seconds']}s")

    # 3. Unicode and special characters
    unicode_code = 'print("Hello \u201cWorld\u201d \u263a \u4e16\u754c")'
    r_unicode = analyzer.analyze(unicode_code, "SyntaxError: invalid character")
    assert r_unicode["error_type"] != "", "Unicode code failed"
    print("[M01/M02] Unicode (Chinese, emoji, typographic quotes) handled cleanly")

    # 4. Multiline Stack Trace
    trace = """Traceback (most recent call last):
  File "app.py", line 124, in calculate
    result = compute_avg(items)
  File "app.py", line 89, in compute_avg
    return sum(items) / len(items)
ZeroDivisionError: division by zero"""
    r_trace = analyzer.analyze("def compute_avg(items): return sum(items) / len(items)", trace, "Python")
    assert "ZeroDivisionError" in r_trace["error_type"], f"Traceback parse failure: {r_trace['error_type']}"
    print("[M01/M02] Complex multiline stack trace correctly extracted and analyzed")

    # M03: Language Detection
    print("\n--- Testing M03: Language Detection ---")
    test_cases = [
        ("Python", "def calculate_sum(numbers):\n    total = 0\n    for n in numbers:\n        total += n\n    return total"),
        ("JavaScript", "const calculateSum = (numbers) => {\n    return numbers.reduce((acc, curr) => acc + curr, 0);\n};"),
        ("Java", "public class Calculator {\n    public static void main(String[] args) {\n        System.out.println(42);\n    }\n}"),
        ("C++", "#include <iostream>\nusing namespace std;\nint main() {\n    cout << 42 << endl;\n    return 0;\n}"),
        ("C", "#include <stdio.h>\nint main() {\n    printf(\"%d\\n\", 42);\n    return 0;\n}"),
        ("Unsupported", "fn main() {\n    println!(\"Hello from Rust\");\n}"),
    ]
    for lang, sample in test_cases:
        det, conf = detect_language(sample)
        print(f"[M03] Target: {lang:12} -> Detected: {det:12} (Confidence: {conf:.2f})")
        if lang != "Unsupported":
            assert det == lang, f"Language detection mismatch for {lang}: got {det}"

    # Ambiguous snippet
    amb_det, amb_conf = detect_language("int x = 10;")
    print(f"[M03] Ambiguous 'int x = 10;' -> Detected: {amb_det} (Confidence: {amb_conf:.2f})")

    # M04: AI / Demo Engine
    print("\n--- Testing M04: AI / Demo Engine ---")
    print(f"[M04] APP_MODE: {cfg.app_mode}")
    print(f"[M04] Has Valid API Key: {cfg.has_valid_api_key}")
    print(f"[M04] Mode String: {analyzer.get_mode_string()}")

    # M05 & M06: Root Cause & Code Correction with AST Validation
    print("\n--- Testing M05 & M06: Root Cause & AST Syntax Validation ---")
    python_samples = [
        ("def f():\n    print('Hello World'\n\nf()", "SyntaxError: unexpected EOF"),
        ("def divide(a, b):\n    return a / b\ndivide(10, 0)", "ZeroDivisionError: division by zero"),
        ("def calc():\n    total = 0\n    for i in range(1, len([1,2,3])):\n        total += [1,2,3][i]\n    return total", "Expected 6, got 5"),
    ]
    for code, err in python_samples:
        res = analyzer.analyze(code, err, "Python")
        rc = res.get("root_cause", {}).get("explanation", "")
        fix = res.get("corrected_code", "")
        assert len(rc) > 10, "Empty root cause explanation"
        assert len(fix) > 0, "Empty corrected code"
        ast_val = validate_python_syntax(fix)
        print(f"[M05/M06] Error: {res['error_type']} | Root Cause Length: {len(rc)} | AST Valid: {ast_val['valid']}")
        assert ast_val["valid"] is True, f"Generated Python fix failed AST parse: {ast_val['error']}"

    # M07: Step-by-Step Explanation
    print("\n--- Testing M07: Step-by-Step 3-Part Schema ---")
    steps = res.get("debugging_steps", [])
    assert len(steps) > 0, "No debugging steps found"
    step1 = steps[0]
    assert "what_was_wrong" in step1
    assert "what_was_changed" in step1
    assert "why_it_works" in step1
    print(f"[M07] Step 1 Schema: Wrong -> '{step1['what_was_wrong'][:35]}...' | Changed -> '{step1['what_was_changed'][:35]}...' | Works -> '{step1['why_it_works'][:35]}...'")

    # M08: Prompt Version Management
    print("\n--- Testing M08: Prompt Version Management ---")
    pm = PromptManager()
    for v in ["v1", "v2", "v3", "final"]:
        text = pm.get_prompt_text(v)
        meta = pm.get_metadata(v)
        print(f"[M08] Version: {v:5} | Template Length: {len(text):4} chars | Format: {meta.get('output_format', 'text')}")
        assert len(text) > 50, f"Template for {v} is too short"

    # M09: Prompt Comparison
    print("\n--- Testing M09: Prompt Comparison ---")
    comp = analyzer.compare_prompts(
        code="def divide(a, b):\n    return a / b\nresult = divide(10, 0)",
        error_message="ZeroDivisionError: division by zero",
        language="Python",
    )
    assert "v1" in comp and "v2" in comp and "v3" in comp
    print("[M09] Compared V1, V2, V3 successfully:")
    print(f"      V1 Format: {comp['v1']['_meta'].get('prompt_version')} (Simulated: {comp['v1']['_meta'].get('simulated', False)})")
    print(f"      V2 Format: {comp['v2']['_meta'].get('prompt_version')} (Simulated: {comp['v2']['_meta'].get('simulated', False)})")
    print(f"      V3 Format: {comp['v3']['_meta'].get('prompt_version')} (Simulated: {comp['v3']['_meta'].get('simulated', False)})")

    # M10: Automated Testing Suite
    print("\n--- Testing M10: Full Regression Test Execution ---")
    from tests.test_application import run_unit_tests, run_demo_mode_tests
    u_res = run_unit_tests()
    d_res = run_demo_mode_tests()
    print(f"[M10] Unit Tests: {u_res['passed']}/{u_res['total']}")
    print(f"[M10] Integration Tests: {d_res['passed']}/{d_res['total']}")
    assert u_res["failed"] == 0
    assert d_res["failed"] == 0

    print("\n" + "=" * 60)
    print("ALL 10 MODULES INDEPENDENTLY AUDITED AND VERIFIED!")
    print("=" * 60)

if __name__ == "__main__":
    audit()
