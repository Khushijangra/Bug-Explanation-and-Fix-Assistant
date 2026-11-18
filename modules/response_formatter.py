"""
Response Formatter Module
Parses and formats AI and Demo responses for standardized display,
supporting strict JSON, markdown sections, and free text.
"""

import ast
import json
import re
from typing import Dict, Any, Optional, List


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the AI model's response text into a structured dictionary.

    Attempts JSON parsing first (for V3/final prompt), then falls back
    to markdown section extraction (for V2), and finally free-text fallback (for V1).

    Args:
        response_text: Raw response string from the AI model

    Returns:
        Structured dictionary matching the schema
    """
    if not response_text or not isinstance(response_text, str):
        return _empty_response("No response received from model.")

    # 1. Attempt JSON parsing
    parsed_json = _try_parse_json(response_text)
    if parsed_json and isinstance(parsed_json, dict):
        return _validate_and_normalize(parsed_json, raw=response_text)

    # 2. Attempt Markdown / Text section extraction (V2 / V1 fallback)
    return _parse_text_response(response_text)


def _try_parse_json(text: str) -> Optional[dict]:
    """Attempt to extract and parse JSON from the response text."""
    # Direct JSON parse
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, TypeError):
        pass

    # Extract ```json ... ``` blocks
    json_patterns = [
        r"```json\s*\n([\s\S]*?)\n\s*```",
        r"```\s*\n(\{\s*\"error_identification\"[\s\S]*?\})\n\s*```",
        r"(\{\s*\"error_identification\"[\s\S]*\})",
    ]

    for pattern in json_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            try:
                return json.loads(candidate)
            except (json.JSONDecodeError, TypeError):
                continue

    return None


def _validate_and_normalize(data: dict, raw: Optional[str] = None) -> dict:
    """Validate and normalize parsed JSON response into canonical schema."""
    result = {
        "error_identification": {
            "error_type": "Unknown",
            "error_location": "Unable to determine",
            "severity": "Major",
            "summary": "No summary provided",
        },
        "root_cause": {
            "explanation": "No explanation available",
            "problematic_code": "",
            "language_rule": "",
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "Suggested Improvement",
        },
        "simple_explanation": {
            "explanation": "No explanation available",
            "analogy": None,
        },
        "debugging_steps": [],
        "prevention_tips": [],
        "confidence": {
            "level": "Medium",
            "assumptions": [],
            "limitations": [],
        },
        "raw_response": raw or json.dumps(data, indent=2),
    }

    # Merge error_identification
    ei = data.get("error_identification", {})
    if isinstance(ei, dict):
        result["error_identification"]["error_type"] = ei.get("error_type", "Unknown")
        result["error_identification"]["error_location"] = ei.get("error_location", ei.get("location", "Unable to determine"))
        result["error_identification"]["severity"] = ei.get("severity", "Major")
        result["error_identification"]["summary"] = ei.get("summary", "No summary provided")
    elif isinstance(ei, str):
        result["error_identification"]["summary"] = ei

    # Merge root_cause
    rc = data.get("root_cause", {})
    if isinstance(rc, dict):
        result["root_cause"]["explanation"] = rc.get("explanation", "")
        result["root_cause"]["problematic_code"] = rc.get("problematic_code", "")
        result["root_cause"]["language_rule"] = rc.get("language_rule", "")
    elif isinstance(rc, str):
        result["root_cause"]["explanation"] = rc

    # Merge corrected_code
    cc = data.get("corrected_code", {})
    if isinstance(cc, dict):
        result["corrected_code"]["code"] = cc.get("code", "")
        result["corrected_code"]["changes_made"] = cc.get("changes_made", cc.get("changes", []))
        result["corrected_code"]["fix_type"] = cc.get("fix_type", "Confirmed Fix" if cc.get("code") else "N/A")
    elif isinstance(cc, str):
        result["corrected_code"]["code"] = cc
        result["corrected_code"]["fix_type"] = "Confirmed Fix" if cc else "N/A"

    # Merge simple_explanation
    se = data.get("simple_explanation", {})
    if isinstance(se, dict):
        result["simple_explanation"]["explanation"] = se.get("explanation", se.get("text", ""))
        result["simple_explanation"]["analogy"] = se.get("analogy", None)
    elif isinstance(se, str):
        result["simple_explanation"]["explanation"] = se

    # Merge debugging_steps
    steps = data.get("debugging_steps", [])
    if isinstance(steps, list):
        norm_steps = []
        for i, s in enumerate(steps, 1):
            if isinstance(s, dict):
                norm_steps.append({
                    "step_number": s.get("step_number", i),
                    "what_was_wrong": s.get("what_was_wrong", s.get("wrong", "")),
                    "what_was_changed": s.get("what_was_changed", s.get("changed", "")),
                    "why_it_works": s.get("why_it_works", s.get("works", "")),
                    "wrong": s.get("what_was_wrong", s.get("wrong", "")),
                    "changed": s.get("what_was_changed", s.get("changed", "")),
                    "works": s.get("why_it_works", s.get("works", "")),
                })
            elif isinstance(s, str):
                norm_steps.append({
                    "step_number": i,
                    "what_was_wrong": s,
                    "what_was_changed": "",
                    "why_it_works": "",
                    "wrong": s,
                    "changed": "",
                    "works": "",
                })
        result["debugging_steps"] = norm_steps

    # Merge prevention_tips
    tips = data.get("prevention_tips", [])
    result["prevention_tips"] = tips if isinstance(tips, list) else ([str(tips)] if tips else [])

    # Merge confidence
    conf = data.get("confidence", {})
    if isinstance(conf, dict):
        result["confidence"]["level"] = conf.get("level", "High")
        result["confidence"]["assumptions"] = conf.get("assumptions", [])
        result["confidence"]["limitations"] = conf.get("limitations", [])
    elif isinstance(conf, (int, float)):
        result["confidence"]["level"] = "High" if conf >= 0.8 else ("Medium" if conf >= 0.5 else "Low")

    return result


def _parse_text_response(text: str) -> dict:
    """Parse unstructured Markdown (V2) or free-text (V1) response."""
    result = {
        "error_identification": {
            "error_type": "Identified in Analysis",
            "error_location": "See explanation below",
            "severity": "Major",
            "summary": "",
        },
        "root_cause": {
            "explanation": "",
            "problematic_code": "",
            "language_rule": "",
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "Suggested Improvement",
        },
        "simple_explanation": {
            "explanation": "",
            "analogy": None,
        },
        "debugging_steps": [],
        "prevention_tips": [],
        "confidence": {
            "level": "Medium",
            "assumptions": ["Parsed from markdown/free text response"],
            "limitations": ["Structured sections extracted heuristically without strict JSON schema"],
        },
        "raw_response": text,
    }

    # Extract code blocks
    code_blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)\n```", text)
    if code_blocks:
        result["corrected_code"]["code"] = max(code_blocks, key=len).strip()
        result["corrected_code"]["fix_type"] = "Confirmed Fix"

    # Split into headings if available
    sections = re.split(r"\n#+\s+", text)
    for sec in sections:
        sec_clean = sec.strip()
        sec_lower = sec_clean.lower()
        if any(h in sec_lower for h in ["error identification", "1. error", "what the error is"]):
            lines = [l.strip() for l in sec_clean.split("\n") if l.strip() and not l.startswith("#")]
            if lines:
                result["error_identification"]["summary"] = lines[0][:250]
        elif any(h in sec_lower for h in ["root cause", "2. root", "why the error"]):
            lines = [l.strip() for l in sec_clean.split("\n") if l.strip() and not l.startswith("#")]
            result["root_cause"]["explanation"] = "\n".join(lines)
        elif any(h in sec_lower for h in ["simple explanation", "4. simple", "brief explanation", "how to fix"]):
            lines = [l.strip() for l in sec_clean.split("\n") if l.strip() and not l.startswith("#")]
            result["simple_explanation"]["explanation"] = "\n".join(lines)
        elif any(h in sec_lower for h in ["step-by-step", "5. step", "debugging guide"]):
            lines = [l.strip() for l in sec_clean.split("\n") if l.strip() and not l.startswith("#")]
            for idx, line in enumerate(lines, 1):
                result["debugging_steps"].append({
                    "step_number": idx,
                    "what_was_wrong": line,
                    "what_was_changed": "",
                    "why_it_works": "",
                    "wrong": line,
                    "changed": "",
                    "works": "",
                })
        elif any(h in sec_lower for h in ["prevention", "6. prevention", "best practice"]):
            lines = [l.strip() for l in sec_clean.split("\n") if l.strip() and not l.startswith("#")]
            result["prevention_tips"] = lines

    # Fallback if no sections parsed
    if not result["simple_explanation"]["explanation"] and not result["root_cause"]["explanation"]:
        result["simple_explanation"]["explanation"] = text.strip()
        result["error_identification"]["summary"] = text.strip()[:200]

    return result


def _empty_response(reason: str) -> dict:
    """Return default structure for empty or invalid responses."""
    return {
        "error_identification": {
            "error_type": "InvalidInput",
            "error_location": "N/A",
            "severity": "Warning",
            "summary": reason,
        },
        "root_cause": {
            "explanation": reason,
            "problematic_code": "",
            "language_rule": "",
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "N/A",
        },
        "simple_explanation": {
            "explanation": reason,
            "analogy": None,
        },
        "debugging_steps": [],
        "prevention_tips": [],
        "confidence": {
            "level": "Low",
            "assumptions": [],
            "limitations": [reason],
        },
        "raw_response": reason,
    }


def format_for_display(parsed: dict) -> dict:
    """
    Format parsed analysis result into an idempotent, dual-accessible dictionary.
    Supports BOTH nested section dicts (error_identification, corrected_code, etc.)
    AND flat top-level keys (error_type, severity, etc.) to guarantee that no
    UI rendering code crashes with AttributeError or MissingKey exceptions.
    """
    if not isinstance(parsed, dict):
        parsed = _empty_response(str(parsed))

    # If already formatted, maintain fields cleanly
    ei = parsed.get("error_identification", {})
    if not isinstance(ei, dict):
        ei = {"summary": str(ei)}
    error_type = ei.get("error_type", parsed.get("error_type", "Unknown"))
    error_location = ei.get("error_location", ei.get("location", parsed.get("error_location", "Unable to determine")))
    severity = ei.get("severity", parsed.get("severity", "Major")).capitalize()
    error_summary = ei.get("summary", parsed.get("error_summary", "No summary available"))

    # Severity icon
    severity_icons = {
        "Critical": "🔴",
        "Major": "🟠",
        "High": "🟠",
        "Medium": "🟡",
        "Minor": "🟡",
        "Low": "🟢",
        "Warning": "🔵",
    }
    severity_icon = severity_icons.get(severity, "⚪")

    # Root cause
    rc = parsed.get("root_cause", {})
    if not isinstance(rc, dict):
        rc = {"explanation": str(rc)}
    root_cause_explanation = rc.get("explanation", parsed.get("root_cause_explanation", ""))
    problematic_code = rc.get("problematic_code", parsed.get("problematic_code", ""))
    language_rule = rc.get("language_rule", parsed.get("language_rule", ""))

    # Corrected code
    cc = parsed.get("corrected_code", {})
    if isinstance(cc, dict):
        corrected_code = cc.get("code", "")
        changes_made = cc.get("changes_made", cc.get("changes", []))
        fix_type = cc.get("fix_type", "Confirmed Fix" if corrected_code else "N/A")
    else:
        corrected_code = str(cc) if cc else parsed.get("corrected_code", "")
        changes_made = parsed.get("changes_made", [])
        fix_type = parsed.get("fix_type", "Confirmed Fix" if corrected_code else "N/A")

    # Simple explanation
    se = parsed.get("simple_explanation", {})
    if isinstance(se, dict):
        simple_explanation = se.get("explanation", se.get("text", parsed.get("simple_explanation", "")))
        analogy = se.get("analogy", parsed.get("analogy", None))
    else:
        simple_explanation = str(se) if se else parsed.get("simple_explanation", "")
        analogy = parsed.get("analogy", None)

    # Debugging steps
    steps = parsed.get("debugging_steps", [])
    normalized_steps = []
    if isinstance(steps, list):
        for i, s in enumerate(steps, 1):
            if isinstance(s, dict):
                w = s.get("what_was_wrong", s.get("wrong", ""))
                c = s.get("what_was_changed", s.get("changed", ""))
                k = s.get("why_it_works", s.get("works", ""))
                normalized_steps.append({
                    "step_number": s.get("step_number", i),
                    "what_was_wrong": w,
                    "what_was_changed": c,
                    "why_it_works": k,
                    "wrong": w,
                    "changed": c,
                    "works": k,
                })
            elif isinstance(s, str):
                normalized_steps.append({
                    "step_number": i,
                    "what_was_wrong": s,
                    "what_was_changed": "",
                    "why_it_works": "",
                    "wrong": s,
                    "changed": "",
                    "works": "",
                })

    # Prevention tips
    tips = parsed.get("prevention_tips", [])
    normalized_tips = tips if isinstance(tips, list) else ([str(tips)] if tips else [])

    # Confidence
    conf = parsed.get("confidence", {})
    if isinstance(conf, dict):
        confidence_level = conf.get("level", parsed.get("confidence_level", "Medium")).capitalize()
        assumptions = conf.get("assumptions", parsed.get("assumptions", []))
        limitations = conf.get("limitations", parsed.get("limitations", []))
    else:
        confidence_level = str(conf) if conf else parsed.get("confidence_level", "Medium")
        assumptions = parsed.get("assumptions", [])
        limitations = parsed.get("limitations", [])

    meta = parsed.get("_meta", {})

    return {
        # Flat convenience keys
        "error_type": error_type,
        "error_location": error_location,
        "severity": severity,
        "severity_icon": severity_icon,
        "error_summary": error_summary,
        "root_cause_explanation": root_cause_explanation,
        "problematic_code": problematic_code,
        "language_rule": language_rule,
        "corrected_code": corrected_code,
        "changes_made": changes_made,
        "fix_type": fix_type,
        "simple_explanation": simple_explanation,
        "analogy": analogy,
        "debugging_steps": normalized_steps,
        "prevention_tips": normalized_tips,
        "confidence_level": confidence_level,
        "assumptions": assumptions,
        "limitations": limitations,
        "raw_response": parsed.get("raw_response", ""),
        "_meta": meta,

        # Nested dictionary sections (for structured callers)
        "error_identification": {
            "error_type": error_type,
            "error_location": error_location,
            "location": error_location,
            "severity": severity,
            "summary": error_summary,
        },
        "root_cause": {
            "explanation": root_cause_explanation,
            "problematic_code": problematic_code,
            "language_rule": language_rule,
        },
        "corrected_code_dict": {
            "code": corrected_code,
            "changes": changes_made,
            "changes_made": changes_made,
            "fix_type": fix_type,
        },
        "simple_explanation_dict": {
            "explanation": simple_explanation,
            "text": simple_explanation,
            "analogy": analogy,
        },
        "confidence": {
            "level": confidence_level,
            "assumptions": assumptions,
            "limitations": limitations,
        },
    }


def validate_python_syntax(code: str) -> Dict[str, Any]:
    """
    Safely validate whether a Python code snippet is syntactically valid using ast.parse.
    Does NOT execute the code.
    """
    if not code or not code.strip():
        return {"valid": False, "error": "Empty code snippet"}
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": f"SyntaxError on line {e.lineno}: {e.msg}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}
