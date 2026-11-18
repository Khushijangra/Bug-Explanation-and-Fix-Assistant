"""
Response Formatter Module
Parses and formats AI responses for display in the application.
"""

import json
import re
from typing import Dict, Any, Optional


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the AI model's response text into a structured dictionary.

    Attempts to parse as JSON first (for V3/final prompts), then falls back
    to text parsing for V1/V2 prompt responses.

    Args:
        response_text: Raw response text from the AI model

    Returns:
        Dictionary with standardized keys for display
    """
    # Try JSON parsing first
    parsed = _try_parse_json(response_text)
    if parsed:
        return _validate_and_normalize(parsed)

    # Fall back to text parsing
    return _parse_text_response(response_text)


def _try_parse_json(text: str) -> Optional[dict]:
    """Attempt to extract and parse JSON from the response."""
    # Try direct JSON parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find JSON block in markdown code fences
    json_patterns = [
        r"```json\s*\n(.*?)\n\s*```",
        r"```\s*\n(\{.*?\})\n\s*```",
        r"(\{[\s\S]*\})"
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except (json.JSONDecodeError, TypeError):
                continue

    return None


def _validate_and_normalize(data: dict) -> dict:
    """Validate and normalize parsed JSON response to standard format."""
    result = {
        "error_identification": {
            "error_type": "Unknown",
            "error_location": "Unable to determine",
            "severity": "Unknown",
            "summary": "No summary available"
        },
        "root_cause": {
            "explanation": "No explanation available",
            "problematic_code": "",
            "language_rule": ""
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "Suggested Improvement"
        },
        "simple_explanation": {
            "explanation": "No explanation available",
            "analogy": None
        },
        "debugging_steps": [],
        "prevention_tips": [],
        "confidence": {
            "level": "Low",
            "assumptions": [],
            "limitations": ["Response could not be fully validated"]
        },
        "raw_response": None
    }

    # Merge in provided data
    for key in result:
        if key in data:
            if isinstance(result[key], dict) and isinstance(data[key], dict):
                result[key].update(data[key])
            else:
                result[key] = data[key]

    return result


def _parse_text_response(text: str) -> dict:
    """Parse unstructured text response into standard format."""
    result = {
        "error_identification": {
            "error_type": "See analysis below",
            "error_location": "See analysis below",
            "severity": "See analysis below",
            "summary": ""
        },
        "root_cause": {
            "explanation": "",
            "problematic_code": "",
            "language_rule": ""
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "Suggested Improvement"
        },
        "simple_explanation": {
            "explanation": "",
            "analogy": None
        },
        "debugging_steps": [],
        "prevention_tips": [],
        "confidence": {
            "level": "Medium",
            "assumptions": ["Response was parsed from unstructured text"],
            "limitations": ["Structured fields may not be accurately extracted"]
        },
        "raw_response": text
    }

    # Extract code blocks
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", text, re.DOTALL)
    if code_blocks:
        # Use the last/largest code block as the corrected code
        result["corrected_code"]["code"] = max(code_blocks, key=len)

    # Try to extract sections by common headings
    sections = re.split(r"\n#+\s+", text)

    for section in sections:
        section_lower = section.lower().strip()
        if any(kw in section_lower for kw in ["error", "identification", "type", "issue"]):
            if not result["error_identification"]["summary"]:
                lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
                if lines:
                    result["error_identification"]["summary"] = lines[0][:200]
        elif any(kw in section_lower for kw in ["root cause", "why", "reason", "cause"]):
            lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
            if lines:
                result["root_cause"]["explanation"] = "\n".join(lines)
        elif any(kw in section_lower for kw in ["explanation", "simple", "beginner", "plain"]):
            lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
            if lines:
                result["simple_explanation"]["explanation"] = "\n".join(lines)
        elif any(kw in section_lower for kw in ["step", "debug", "walkthrough", "guide"]):
            lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
            for i, line in enumerate(lines):
                result["debugging_steps"].append({
                    "step_number": i + 1,
                    "what_was_wrong": line,
                    "what_was_changed": "",
                    "why_it_works": ""
                })
        elif any(kw in section_lower for kw in ["prevention", "tip", "avoid", "best practice"]):
            lines = [l.strip() for l in section.split("\n")
                     if l.strip() and not l.startswith("#") and len(l.strip()) > 5]
            result["prevention_tips"] = lines

    # If no structured extraction worked, put the whole response in simple_explanation
    if not result["simple_explanation"]["explanation"] and not result["root_cause"]["explanation"]:
        result["simple_explanation"]["explanation"] = text
        result["error_identification"]["summary"] = text[:200] if len(text) > 200 else text

    return result


def format_for_display(parsed_response: dict) -> dict:
    """
    Prepare parsed response for Streamlit display.

    Returns dict with display-ready strings and flags.
    """
    if not isinstance(parsed_response, dict):
        parsed_response = {}

    display = {}

    # Error identification
    ei = parsed_response.get("error_identification", {})
    if isinstance(ei, dict):
        display["error_type"] = ei.get("error_type", "Unknown")
        display["error_location"] = ei.get("error_location", "Unable to determine")
        display["severity"] = ei.get("severity", "Unknown")
        display["error_summary"] = ei.get("summary", "No summary available")
    else:
        display["error_type"] = "Analysis Result"
        display["error_location"] = "Unable to determine"
        display["severity"] = "Major"
        display["error_summary"] = str(ei)

    # Severity color
    severity_colors = {
        "Critical": "\U0001f534",
        "Major": "\U0001f7e0",
        "Minor": "\U0001f7e1",
        "Warning": "\U0001f535"
    }
    display["severity_icon"] = severity_colors.get(display["severity"], "\u26aa")

    # Root cause
    rc = parsed_response.get("root_cause", {})
    if isinstance(rc, dict):
        display["root_cause_explanation"] = rc.get("explanation", "")
        display["problematic_code"] = rc.get("problematic_code", "")
        display["language_rule"] = rc.get("language_rule", "")
    else:
        display["root_cause_explanation"] = str(rc)
        display["problematic_code"] = ""
        display["language_rule"] = ""

    # Corrected code
    cc = parsed_response.get("corrected_code", {})
    if isinstance(cc, dict):
        display["corrected_code"] = cc.get("code", "")
        display["changes_made"] = cc.get("changes_made", [])
        display["fix_type"] = cc.get("fix_type", "Suggested Improvement")
    else:
        display["corrected_code"] = str(cc) if cc else ""
        display["changes_made"] = []
        display["fix_type"] = "Confirmed Fix" if cc else "N/A"

    # Simple explanation
    se = parsed_response.get("simple_explanation", {})
    if isinstance(se, dict):
        display["simple_explanation"] = se.get("explanation", "")
        display["analogy"] = se.get("analogy")
    else:
        display["simple_explanation"] = str(se)
        display["analogy"] = None

    # Debugging steps
    steps = parsed_response.get("debugging_steps", [])
    if isinstance(steps, list):
        normalized_steps = []
        for i, s in enumerate(steps):
            if isinstance(s, dict):
                normalized_steps.append(s)
            elif isinstance(s, str):
                normalized_steps.append({
                    "step_number": i + 1,
                    "what_was_wrong": s,
                    "what_was_changed": "",
                    "why_it_works": ""
                })
        display["debugging_steps"] = normalized_steps
    else:
        display["debugging_steps"] = []

    # Prevention tips
    tips = parsed_response.get("prevention_tips", [])
    display["prevention_tips"] = tips if isinstance(tips, list) else ([str(tips)] if tips else [])

    # Confidence
    conf = parsed_response.get("confidence", {})
    if isinstance(conf, dict):
        display["confidence_level"] = conf.get("level", "Medium")
        display["assumptions"] = conf.get("assumptions", [])
        display["limitations"] = conf.get("limitations", [])
    elif isinstance(conf, (int, float)):
        level = "High" if conf >= 0.8 else ("Medium" if conf >= 0.5 else "Low")
        display["confidence_level"] = level
        display["assumptions"] = []
        display["limitations"] = []
    else:
        display["confidence_level"] = str(conf) if conf else "Medium"
        display["assumptions"] = []
        display["limitations"] = []

    # Raw response (for V1/V2)
    display["raw_response"] = parsed_response.get("raw_response")

    return display
