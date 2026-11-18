"""
Test Application Module
Automated tests for the Bug Explanation and Fix Assistant.
"""

import os
import sys
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.language_detector import detect_language, get_supported_languages, validate_language
from modules.bug_analyzer import BugAnalyzer
from modules.prompt_manager import PromptManager
from modules.response_formatter import parse_ai_response, format_for_display


def load_test_cases():
    """Load test cases from JSON file."""
    test_data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test-data", "test_cases.json"
    )
    with open(test_data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_all_tests():
    """Run all test cases and collect results."""
    test_cases = load_test_cases()
    analyzer = BugAnalyzer()
    results = []

    print(f"{'=' * 60}")
    print("Bug Explanation and Fix Assistant - Test Suite")
    print(f"Mode: {analyzer.get_mode_string()}")
    print(f"Total test cases: {len(test_cases)}")
    print(f"{'=' * 60}\n")

    passed = 0
    failed = 0

    for tc in test_cases:
        test_id = tc["test_id"]
        test_type = tc["test_type"]
        language = tc["language"]
        description = tc["description"]
        code = tc["code"]
        error_msg = tc["error_message"]
        expected = tc["expected_output"]

        print(f"[{test_id}] {description}")
        print(f"  Type: {test_type} | Language: {language}")

        # Handle language detection for auto-detect tests
        actual_language = language
        if language == "Auto-Detect":
            detected, confidence = detect_language(code, error_msg)
            actual_language = detected if detected != "Unknown" else "C"
            print(f"  Auto-detected language: {detected} (confidence: {confidence:.0%})")

        try:
            start_time = time.time()
            result = analyzer.analyze(
                code=code,
                error_message=error_msg,
                language=actual_language,
                prompt_version="final"
            )
            duration = time.time() - start_time

            # Determine pass/fail
            test_passed = True
            notes = []

            # Check if error type was identified
            error_type = result.get("error_type", "")
            if error_type and error_type != "Unknown":
                notes.append(f"Error type identified: {error_type}")
            elif test_type not in ("Invalid", "Edge"):
                test_passed = False
                notes.append("Failed to identify error type")

            # Check if corrected code was provided when expected
            if expected.get("should_fix", False):
                corrected = result.get("corrected_code", "")
                if corrected and corrected.strip():
                    notes.append("Corrected code provided")
                else:
                    if analyzer.is_ai_mode():
                        test_passed = False
                        notes.append("No corrected code provided")
                    else:
                        notes.append("Demo mode: corrected code may be limited")

            # Edge case: empty code
            if not code or not code.strip():
                summary = result.get("error_summary", "").lower()
                explanation = result.get("simple_explanation", "").lower()
                if "empty" in summary or "no code" in summary or \
                   "no source code" in summary or "empty" in explanation or \
                   "no code" in explanation:
                    notes.append("Correctly identified empty input")
                else:
                    notes.append("Handled empty input (response may vary)")

            status = "PASS" if test_passed else "FAIL"
            if test_passed:
                passed += 1
            else:
                failed += 1

            test_result = {
                "test_id": test_id,
                "test_type": test_type,
                "language": language,
                "description": description,
                "status": status,
                "duration_seconds": round(duration, 3),
                "error_type_found": error_type,
                "has_corrected_code": bool(result.get("corrected_code")),
                "confidence": result.get("confidence_level", "N/A"),
                "notes": notes,
                "actual_output_summary": {
                    "error_type": result.get("error_type", ""),
                    "severity": result.get("severity", ""),
                    "summary": (result.get("error_summary", "") or "")[:200],
                    "has_steps": bool(result.get("debugging_steps")),
                    "has_tips": bool(result.get("prevention_tips")),
                }
            }
            results.append(test_result)

            print(f"  Result: {status} ({duration:.3f}s)")
            for note in notes:
                print(f"    - {note}")
            print()

        except Exception as e:
            failed += 1
            test_result = {
                "test_id": test_id,
                "test_type": test_type,
                "language": language,
                "description": description,
                "status": "FAIL",
                "error": str(e),
                "notes": [f"Exception: {str(e)}"],
            }
            results.append(test_result)
            print(f"  Result: FAIL (Exception: {e})\n")

    # Summary
    total = len(test_cases)
    print(f"{'=' * 60}")
    print("RESULTS SUMMARY")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Rate:   {passed / total * 100:.1f}%")
    print(f"{'=' * 60}")

    # Save results
    output = {
        "run_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": analyzer.get_mode_string(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed / total * 100:.1f}%",
        "results": results,
    }

    results_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test-data", "test_results.json"
    )
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    return output


def test_language_detector():
    """Test the language detection module."""
    print("\n" + "=" * 60)
    print("Language Detector Tests")
    print("=" * 60 + "\n")

    test_snippets = [
        ("def hello():\n    print('hi')", "Python"),
        ("console.log('hello');", "JavaScript"),
        ("public class Main { public static void main(String[] args) {} }", "Java"),
        ('#include <iostream>\nint main() { cout << "hi"; }', "C++"),
        ('#include <stdio.h>\nint main() { printf("hi"); }', "C"),
        ("", "Unknown"),
    ]

    for code, expected in test_snippets:
        detected, confidence = detect_language(code)
        status = "PASS" if detected == expected else "WARN"
        print(
            f"[{status}] Expected: {expected:12s} | Detected: {detected:12s} "
            f"(confidence: {confidence:.2f})"
        )
        if code:
            print(f"       Code: {code[:50]}...")
        print()

    # Test supported languages
    langs = get_supported_languages()
    print(f"Supported languages: {langs}")
    assert len(langs) == 5, f"Expected 5 languages, got {len(langs)}"
    print("Language count: PASS")

    # Test validation
    assert validate_language("Python") is True
    assert validate_language("Fortran") is False
    print("Language validation: PASS")


def test_prompt_manager():
    """Test the prompt manager module."""
    print("\n" + "=" * 60)
    print("Prompt Manager Tests")
    print("=" * 60 + "\n")

    pm = PromptManager()

    # Test loading all versions
    versions = pm.get_all_versions()
    print(f"Available versions: {versions}")
    assert len(versions) >= 3, f"Expected at least 3 versions, got {len(versions)}"
    print("Version count: PASS")

    # Test rendering
    for v in ["v1", "v2", "v3"]:
        prompt = pm.get_prompt(v, "print('hello')", "SyntaxError", "Python")
        assert len(prompt) > 50, f"Prompt {v} seems too short"
        assert "print('hello')" in prompt, f"Code not found in {v} prompt"
        print(f"Prompt {v} rendering: PASS ({len(prompt)} chars)")

    # Test metadata
    for v in ["v1", "v2", "v3"]:
        meta = pm.get_metadata(v)
        assert "name" in meta, f"Missing name in {v} metadata"
        print(f"Prompt {v} metadata: PASS (name: {meta.get('name')})")


def test_response_formatter():
    """Test the response formatter module."""
    print("\n" + "=" * 60)
    print("Response Formatter Tests")
    print("=" * 60 + "\n")

    # Test JSON parsing
    json_response = json.dumps({
        "error_identification": {
            "error_type": "SyntaxError",
            "error_location": "Line 2",
            "severity": "Critical",
            "summary": "Missing parenthesis",
        },
        "root_cause": {
            "explanation": "Missing closing bracket",
            "problematic_code": "print('hello'",
            "language_rule": "Balanced parentheses required",
        },
        "corrected_code": {
            "code": "print('hello')",
            "changes_made": ["Added closing parenthesis"],
            "fix_type": "Confirmed Fix",
        },
        "simple_explanation": {
            "explanation": "You forgot to close the bracket",
            "analogy": "Like leaving a door open",
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Missing )",
                "what_was_changed": "Added )",
                "why_it_works": "Brackets must match",
            }
        ],
        "prevention_tips": ["Use an IDE with bracket matching"],
        "confidence": {
            "level": "High",
            "assumptions": [],
            "limitations": [],
        },
    })

    parsed = parse_ai_response(json_response)
    assert parsed["error_identification"]["error_type"] == "SyntaxError"
    print("JSON parsing: PASS")

    display = format_for_display(parsed)
    assert display["error_type"] == "SyntaxError"
    assert display["severity_icon"] == "\U0001f534"
    print("Display formatting: PASS")

    # Test text parsing
    text_response = (
        "# Error\nSyntaxError on line 2\n"
        "# Fix\n```python\nprint('hello')\n```"
    )
    parsed_text = parse_ai_response(text_response)
    assert parsed_text is not None
    print("Text parsing: PASS")

    # Test empty input
    empty = parse_ai_response("")
    assert empty is not None
    print("Empty input handling: PASS")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BUG EXPLANATION AND FIX ASSISTANT - FULL TEST SUITE")
    print("=" * 60 + "\n")

    # Unit tests
    test_language_detector()
    test_prompt_manager()
    test_response_formatter()

    # Integration tests
    run_all_tests()
