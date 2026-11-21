"""
Language Detection Module
Detects programming language from source code using keyword analysis and pattern matching.
"""

import re
from typing import Tuple

# Language-specific indicators with weights
LANGUAGE_PATTERNS = {
    "Python": {
        "keywords": ["def ", "import ", "from ", "class ", "elif ", "except:",
                      "finally:", "lambda ", "yield ", "with ", "as ",
                      "print(", "self.", "__init__", "None", "True", "False"],
        "patterns": [r"^\s*def\s+\w+\s*\(", r"^\s*class\s+\w+", r"^\s*import\s+",
                     r"^\s*from\s+\w+\s+import", r"#.*$", r"'''|\"\"\"",
                     r"^\s*@\w+", r"\bif\s+__name__\s*=="],
        "error_patterns": ["Traceback", "SyntaxError", "IndentationError", "NameError",
                          "TypeError", "ValueError", "AttributeError", "ImportError",
                          "KeyError", "IndexError", "FileNotFoundError", "ZeroDivisionError"]
    },
    "JavaScript": {
        "keywords": ["const ", "let ", "var ", "function ", "=>", "console.log",
                      "document.", "window.", "require(", "module.exports",
                      "async ", "await ", "Promise", "undefined",
                      "export ", "import "],
        "patterns": [r"^\s*const\s+\w+", r"^\s*let\s+\w+", r"^\s*var\s+\w+",
                     r"^\s*function\s+\w+", r"=>\s*\{",
                     r"===|!==", r"^\s*class\s+\w+\s+extends"],
        "error_patterns": ["ReferenceError", "SyntaxError", "TypeError", "RangeError",
                          "Uncaught", "is not defined", "is not a function",
                          "Cannot read propert"]
    },
    "Java": {
        "keywords": ["public ", "private ", "protected ", "static ", "void ",
                      "class ", "interface ", "extends ", "implements ",
                      "System.out.print", "new ", "throw ", "throws ",
                      "try ", "catch ", "finally ", "package ", "import java.",
                      "String ", "int ", "boolean ", "double "],
        "patterns": [r"^\s*public\s+class\s+\w+", r"^\s*public\s+static\s+void\s+main",
                     r"^\s*import\s+java\.", r"^\s*package\s+\w+",
                     r"System\.out\.print"],
        "error_patterns": ["Exception in thread", "java.lang.", "NullPointerException",
                          "ArrayIndexOutOfBoundsException", "ClassNotFoundException",
                          "cannot find symbol", "incompatible types"]
    },
    "C++": {
        "keywords": ["#include", "iostream", "using namespace std", "cout",
                      "cin", "endl", "std::", "vector<", "string ",
                      "template", "nullptr", "public:", "private:",
                      "protected:", "virtual ", "override", "auto "],
        "patterns": [r"^\s*#include\s*<", r"^\s*using\s+namespace",
                     r"std::", r"cout\s*<<", r"cin\s*>>",
                     r"^\s*template\s*<", r"->\s*\w+"],
        "error_patterns": ["error:", "undefined reference", "no matching function",
                          "expected", "segmentation fault", "SIGSEGV",
                          "cannot convert", "was not declared"]
    },
    "C": {
        "keywords": ["#include", "stdio.h", "stdlib.h", "string.h", "printf(",
                      "scanf(", "malloc(", "free(", "sizeof(", "NULL",
                      "typedef ", "struct ", "enum ", "union "],
        "patterns": [r"^\s*#include\s*<stdio\.h>", r"^\s*#include\s*<stdlib\.h>",
                     r"printf\s*\(", r"scanf\s*\(",  r"malloc\s*\(",
                     r"^\s*int\s+main\s*\("],
        "error_patterns": ["error:", "undefined reference", "implicit declaration",
                          "segmentation fault", "expected", "incompatible pointer"]
    }
}

SUPPORTED_LANGUAGES = list(LANGUAGE_PATTERNS.keys())


def detect_language(code: str, error_message: str = "") -> Tuple[str, float]:
    """
    Detect the programming language of the given code.

    Args:
        code: Source code string
        error_message: Optional error message for additional context

    Returns:
        Tuple of (language_name, confidence_score)
        confidence_score is between 0.0 and 1.0
    """
    if not code or not code.strip():
        return ("Unknown", 0.0)

    # Strip string literals so English words inside strings (e.g. "Hello from Rust")
    # do not trigger false positive keyword matches for other languages.
    code_clean = re.sub(r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|\".*?\"|\'.*?\')', ' "" ', code)

    raw_scores = {}

    for language, indicators in LANGUAGE_PATTERNS.items():
        score = 0.0

        # Check keywords against sanitized code (outside string literals)
        for keyword in indicators["keywords"]:
            if keyword in code_clean:
                score += 1.0

        # Check regex patterns against original code (for full syntax structures)
        for pattern in indicators["patterns"]:
            try:
                if re.search(pattern, code, re.MULTILINE):
                    score += 1.5
            except re.error:
                pass

        # Check error message patterns
        if error_message:
            for err_pattern in indicators["error_patterns"]:
                if err_pattern.lower() in error_message.lower():
                    score += 2.0

        raw_scores[language] = score

    if not raw_scores:
        return ("Unknown", 0.0)

    # Disambiguation: C vs C++
    if raw_scores.get("C", 0) > 0 and raw_scores.get("C++", 0) > 0:
        cpp_indicators = ["cout", "cin", "std::", "iostream", "vector<",
                         "class ", "template", "namespace", "nullptr", "auto "]
        has_cpp = any(ind in code for ind in cpp_indicators)
        if has_cpp:
            raw_scores["C"] *= 0.5
        else:
            raw_scores["C++"] *= 0.7

    best_language = max(raw_scores, key=raw_scores.get)
    best_raw = raw_scores[best_language]

    if best_raw < 0.5:
        return ("Unknown", 0.0)

    # Calculate confidence based on raw score saturation
    confidence = min(round(best_raw / 4.0, 2), 0.95)
    confidence = max(confidence, 0.25)  # Minimum confidence for a matched indicator

    return (best_language, round(confidence, 2))


def get_supported_languages() -> list:
    """Return list of supported programming languages."""
    return SUPPORTED_LANGUAGES.copy()


def validate_language(language: str) -> bool:
    """Check if a language is supported."""
    return language in SUPPORTED_LANGUAGES
