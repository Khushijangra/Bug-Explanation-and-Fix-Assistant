"""
Bug Analyzer Module
Core AI analysis engine for the Bug Explanation and Fix Assistant.
Routes bug analysis requests to either the Gemini AI backend or a
deterministic demo mode, depending on configuration.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional

from modules.prompt_manager import PromptManager
from modules.response_formatter import parse_ai_response, format_for_display
from modules.language_detector import detect_language

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Deterministic demo responses adhering strictly to the V3 JSON schema
# ---------------------------------------------------------------------------

DEMO_RESPONSES: Dict[str, dict] = {
    "python_syntax": {
        "error_identification": {
            "error_type": "SyntaxError",
            "error_location": "Line 2 - print statement",
            "severity": "Critical",
            "summary": "Missing closing parenthesis in print function call"
        },
        "root_cause": {
            "explanation": "Python 3 requires print to be invoked as a function with matched parentheses. The opening parenthesis '(' on line 2 is never closed before the end of the line or file, triggering a SyntaxError.",
            "problematic_code": 'print("Hello World"',
            "language_rule": "In Python 3.x, print is a built-in function requiring closing parenthesis for its argument list."
        },
        "corrected_code": {
            "code": 'def greet():\n    print("Hello World")  # FIXED: Added missing closing parenthesis\n\ngreet()',
            "changes_made": ["Added missing closing parenthesis to print() function call"],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "Think of parentheses like matching shoes: you always need both the left '(' and right ')' one. Here you opened the shoe box with '(' but forgot to close it with ')'.",
            "analogy": "Like opening a quote or door and forgetting to close it behind you."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": 'The print statement had an unclosed parenthesis: print("Hello World"',
                "what_was_changed": 'Appended the matching closing parenthesis: print("Hello World")',
                "why_it_works": "The Python parser now clearly knows where the arguments to print() end."
            }
        ],
        "prevention_tips": [
            "Use an IDE or text editor with automatic bracket-matching highlights.",
            "Use a syntax checker or linter such as flake8 or ruff.",
            "Type both '(' and ')' immediately, then place your cursor between them to write arguments."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Python 3.x execution environment"],
            "limitations": ["Static syntax inspection only; code was not executed."]
        }
    },
    "python_zerodivision": {
        "error_identification": {
            "error_type": "ZeroDivisionError",
            "error_location": "Line 2 - 'return a / b'",
            "severity": "Critical",
            "summary": "Division by zero occurred during arithmetic operation"
        },
        "root_cause": {
            "explanation": "The denominator 'b' evaluated to 0 during 'a / b'. In mathematics and standard computing architectures, dividing a real number by zero is undefined and raises an unhandled ZeroDivisionError at runtime.",
            "problematic_code": "return a / b",
            "language_rule": "Python arithmetic operators raise ZeroDivisionError when the second argument to /, //, or % is zero."
        },
        "corrected_code": {
            "code": "def divide(a, b):\n    if b == 0:  # FIXED: Guard against zero denominator\n        raise ValueError('Denominator cannot be zero.')\n    return a / b\n\nresult = divide(10, 2)\nprint(result)",
            "changes_made": [
                "Added conditional validation guard ensuring denominator b is non-zero",
                "Replaced test call divide(10, 0) with valid denominator divide(10, 2)"
            ],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "You cannot split 10 cookies equally among 0 people. Computers cannot divide numbers by 0, so Python stops your program with an error.",
            "analogy": "Sharing pizza slices among zero friends is impossible to calculate."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "The function attempted division without checking if b == 0.",
                "what_was_changed": "Introduced an if condition checking if b == 0 before performing division.",
                "why_it_works": "Prevents the illegal division instruction from ever executing when b is zero."
            }
        ],
        "prevention_tips": [
            "Always validate user inputs or variables before passing them as denominators.",
            "Use try-except blocks or assertions if zero denominators are possible in dynamic workflows."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Inputs are numeric scalars"],
            "limitations": ["Assumes standard float or integer arithmetic."]
        }
    },
    "javascript_reference": {
        "error_identification": {
            "error_type": "ReferenceError",
            "error_location": "Line 1 - console.log(result)",
            "severity": "Critical",
            "summary": "Cannot access 'result' before initialization (Temporal Dead Zone)"
        },
        "root_cause": {
            "explanation": "Variables declared with let and const are hoisted to the top of their enclosing block scope but are not initialized. Accessing them before the declaration statement triggers a ReferenceError due to the Temporal Dead Zone (TDZ).",
            "problematic_code": "console.log(result);\nlet result = 42;",
            "language_rule": "ECMAScript block-scoped declarations (let and const) cannot be accessed prior to their declaration statement."
        },
        "corrected_code": {
            "code": "let result = 42;  // FIXED: Declared and initialized before usage\nconsole.log(result);",
            "changes_made": ["Moved variable declaration before its first access"],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "You asked JavaScript to display 'result' on the screen before you actually told it what 'result' is. You must define a variable before using it.",
            "analogy": "Trying to read a book before you purchase or open it."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "console.log was called on line 1 before 'let result' was declared on line 2.",
                "what_was_changed": "Reordered statements so 'let result = 42;' executes before 'console.log(result);'.",
                "why_it_works": "The variable is properly bound and initialized in memory prior to being read."
            }
        ],
        "prevention_tips": [
            "Always declare variables at the top of functions or scope blocks.",
            "Use ESLint with the 'no-use-before-define' rule enabled."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Running in modern ECMAScript environment"],
            "limitations": ["Static code review."]
        }
    },
    "java_nullpointer": {
        "error_identification": {
            "error_type": "NullPointerException",
            "error_location": "Line 4 - name.length()",
            "severity": "Critical",
            "summary": "Invocation of instance method length() on null reference"
        },
        "root_cause": {
            "explanation": "Variable 'name' is assigned to null. Attempting to invoke an instance method (.length()) on a reference pointing to null throws a java.lang.NullPointerException at runtime.",
            "problematic_code": "String name = null;\nSystem.out.println(name.length());",
            "language_rule": "In Java, dereferencing a reference variable pointing to null triggers NullPointerException."
        },
        "corrected_code": {
            "code": "public class Main {\n    public static void main(String[] args) {\n        String name = \"Default\";  // FIXED: Initialized with non-null value\n        if (name != null) {       // FIXED: Added defensive null check\n            System.out.println(name.length());\n        }\n    }\n}",
            "changes_made": [
                "Assigned an initial non-null value to string variable",
                "Added defensive null check guard before method invocation"
            ],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "The variable 'name' is currently completely empty (null). You asked Java to measure the length of something that does not exist.",
            "analogy": "Trying to count the pages of a book when the book box is empty."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Invoked .length() on name when name was null.",
                "what_was_changed": "Initialized name with a valid string and added null guard.",
                "why_it_works": "Guarantees that methods are only called on valid memory objects."
            }
        ],
        "prevention_tips": [
            "Use Optional<T> or annotations like @NonNull / @Nullable in Java.",
            "Always perform defensive null checks before dereferencing external or uninitialized references."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Java 8+ runtime"],
            "limitations": ["Static analysis."]
        }
    },
    "cpp_missing_semicolon": {
        "error_identification": {
            "error_type": "CompilationError",
            "error_location": "Line 5 - cout << \"Hello World\" << endl",
            "severity": "Critical",
            "summary": "Missing semicolon ';' before 'return' keyword"
        },
        "root_cause": {
            "explanation": "C++ statements must be terminated with a semicolon. The compiler encountered 'return' while still parsing the previous cout stream statement, triggering a syntax/compilation error.",
            "problematic_code": 'cout << "Hello World" << endl',
            "language_rule": "C++ grammar mandates every expression statement ends with a semicolon ';'."
        },
        "corrected_code": {
            "code": '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello World" << endl;  // FIXED: Added terminating semicolon\n    return 0;\n}',
            "changes_made": ["Added terminating semicolon ';' to cout statement"],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "In C++, semicolons are like periods at the end of sentences. You forgot to put a period at the end of your cout instruction.",
            "analogy": "Sentences in English require periods; code statements in C++ require semicolons."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Line 5 cout stream statement did not terminate with ';'.",
                "what_was_changed": "Appended ';' to the end of line 5.",
                "why_it_works": "Informs the C++ compiler's lexical analyzer that the statement has completed."
            }
        ],
        "prevention_tips": [
            "Remember that virtually all expression statements in C++ must end with ';'.",
            "Configure your editor to format code automatically on save (e.g. clang-format)."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Standard C++ compiler (g++, clang++)"],
            "limitations": ["Static syntax validation."]
        }
    },
    "c_array_bounds": {
        "error_identification": {
            "error_type": "RuntimeError",
            "error_location": "Line 5 - arr[10]",
            "severity": "Critical",
            "summary": "Array index out of bounds causing segmentation fault"
        },
        "root_cause": {
            "explanation": "The array 'arr' is declared with 5 elements (indices 0 through 4). Attempting to read index 10 accesses unallocated or forbidden memory, resulting in undefined behavior and a Segmentation Fault (SIGSEGV).",
            "problematic_code": 'printf("%d\\n", arr[10]);',
            "language_rule": "In C, arrays are zero-indexed and bounds are not checked at runtime; reading beyond array boundaries violates memory safety."
        },
        "corrected_code": {
            "code": '#include <stdio.h>\n\nint main() {\n    int arr[5] = {1, 2, 3, 4, 5};\n    int valid_index = 4;  // FIXED: Restrict index to valid range [0, 4]\n    printf("%d\\n", arr[valid_index]);\n    return 0;\n}',
            "changes_made": ["Replaced out-of-bounds index 10 with a valid index (4) within bounds [0..4]"],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "You created a shelf with only 5 slots (numbered 0 to 4), but then you tried to reach for item number 10. The computer crashes because that slot does not exist.",
            "analogy": "Looking for apartment #10 in a building that only has 5 apartments."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Accessing arr[10] when array size is 5.",
                "what_was_changed": "Changed index to 4 (the last valid element in the array).",
                "why_it_works": "The accessed memory is within the allocated stack boundaries of arr."
            }
        ],
        "prevention_tips": [
            "Use constants or sizeof(arr)/sizeof(arr[0]) to calculate array bounds.",
            "Compile with AddressSanitizer (-fsanitize=address) to catch memory boundary violations immediately."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["C99 or newer standard"],
            "limitations": ["C runtime memory safety is verified statically."]
        }
    },
    "python_off_by_one": {
        "error_identification": {
            "error_type": "LogicalError",
            "error_location": "Line 3 - 'for i in range(1, len(numbers)):'",
            "severity": "Major",
            "summary": "Off-by-one logical error in loop starting range index"
        },
        "root_cause": {
            "explanation": "Python lists are zero-indexed. The loop begins at index 1 instead of index 0, completely omitting the first element (numbers[0]) from the calculated sum.",
            "problematic_code": "for i in range(1, len(numbers)):",
            "language_rule": "Sequence indices in Python start at 0. Using range(1, len(list)) skips index 0."
        },
        "corrected_code": {
            "code": "def sum_list(numbers):\n    total = 0\n    for i in range(0, len(numbers)):  # FIXED: Start at index 0 (or use 'for n in numbers:')\n        total += numbers[i]\n    return total\n\nprint(sum_list([1, 2, 3, 4, 5]))",
            "changes_made": [
                "Changed range start from 1 to 0 so the first element is included in summation"
            ],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "Computers count starting at 0, not 1! Because your loop started at 1, you skipped the very first number in the list.",
            "analogy": "Starting to count pages in a booklet from page 2, missing page 1 entirely."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Loop initialized at index 1, skipping numbers[0].",
                "what_was_changed": "Updated range start to 0.",
                "why_it_works": "Ensures all elements from index 0 to len(numbers)-1 are accumulated."
            }
        ],
        "prevention_tips": [
            "Prefer idiomatic Python iteration: 'for num in numbers:' over manual indexing.",
            "Or use built-in functions like 'sum(numbers)' directly."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["List contains numeric values"],
            "limitations": ["Logic error inferred from discrepancy in expected output."]
        }
    },
    "empty_code": {
        "error_identification": {
            "error_type": "InvalidInput",
            "error_location": "N/A - Source code input is empty",
            "severity": "Warning",
            "summary": "No source code was provided for analysis"
        },
        "root_cause": {
            "explanation": "The code editor was left empty. An AI debugging assistant requires code to inspect syntax, abstract syntax trees, and logical flow.",
            "problematic_code": "",
            "language_rule": "Non-empty input required."
        },
        "corrected_code": {
            "code": "",
            "changes_made": [],
            "fix_type": "N/A"
        },
        "simple_explanation": {
            "explanation": "You didn't paste any code! Please paste your code snippet into the editor so we can analyze it.",
            "analogy": "Asking a doctor for a diagnosis without showing up to the appointment."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Empty code input field.",
                "what_was_changed": "Please paste your buggy code into the text area.",
                "why_it_works": "Provides the input needed to perform static analysis."
            }
        ],
        "prevention_tips": [
            "Ensure you copy and paste your complete code snippet before clicking Analyze."
        ],
        "confidence": {
            "level": "High",
            "assumptions": [],
            "limitations": ["No code to analyze."]
        }
    },
    "missing_error": {
        "error_identification": {
            "error_type": "TypeError",
            "error_location": "Line 5 - add(5, '3')",
            "severity": "Major",
            "summary": "Unsupported operand type(s) for +: 'int' and 'str'"
        },
        "root_cause": {
            "explanation": "Even though no error message was provided, static analysis reveals that calling add(5, '3') attempts to evaluate 5 + '3'. Python does not perform implicit type coercion between integers and strings.",
            "problematic_code": "result = add(5, '3')",
            "language_rule": "In Python, binary operator + does not support mixed int and str operands without explicit casting."
        },
        "corrected_code": {
            "code": "def add(a, b):\n    return a + b\n\nresult = add(5, 3)  # FIXED: Passed integer 3 instead of string '3'\nprint(result)",
            "changes_made": [
                "Replaced string literal '3' with integer literal 3 to ensure compatible operand types"
            ],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "Python does not know whether you want to add numbers (5 + 3 = 8) or glue words together ('5' + '3' = '53'). You cannot add a number and a word directly.",
            "analogy": "Trying to add 5 apples to the word 'three' without translating first."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Passed incompatible types (int and str) to the + operator.",
                "what_was_changed": "Ensured both arguments are integers.",
                "why_it_works": "Integer addition is a well-defined arithmetic operation."
            }
        ],
        "prevention_tips": [
            "Use Python type hints (def add(a: int, b: int) -> int:) to detect type mismatches early.",
            "Use static type checkers such as mypy."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Deduced through static code inspection without runtime traceback"],
            "limitations": ["No runtime error message was provided."]
        }
    },
    "ambiguous_language": {
        "error_identification": {
            "error_type": "CompilationError",
            "error_location": "Global scope - missing entry point",
            "severity": "Critical",
            "summary": "Missing main() function entry point in C/C++ program"
        },
        "root_cause": {
            "explanation": "The code contains statements outside of any function body, and lacks a 'main' function entry point required by C/C++ linkers.",
            "problematic_code": "int x = 5;\nint y = 10;\nint z = x + y;",
            "language_rule": "In C and C++, executable statements must reside inside functions, and an executable binary must define 'int main()'."
        },
        "corrected_code": {
            "code": "#include <stdio.h>\n\nint main() {  // FIXED: Wrapped statements inside main function\n    int x = 5;\n    int y = 10;\n    int z = x + y;\n    printf(\"Sum: %d\\n\", z);\n    return 0;\n}",
            "changes_made": [
                "Added required #include directive",
                "Wrapped loose assignment logic inside int main() function entry point"
            ],
            "fix_type": "Confirmed Fix"
        },
        "simple_explanation": {
            "explanation": "C and C++ programs do not know where to start running unless you provide a 'main' function. Loose code cannot run by itself.",
            "analogy": "A car without an ignition key or starting button cannot begin its journey."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Code executed outside a function and lacked main().",
                "what_was_changed": "Encapsulated logic inside int main().",
                "why_it_works": "Provides the mandatory starting point required by the linker."
            }
        ],
        "prevention_tips": [
            "Remember that C, C++, and Java require execution entry points.",
            "Always wrap executable logic in functions or main."
        ],
        "confidence": {
            "level": "Medium",
            "assumptions": ["Interpreted as C/C++ given syntax and linker error message"],
            "limitations": ["Syntax is syntactically ambiguous between C, C++, and Java without context."]
        }
    },
    "misleading_error": {
        "error_identification": {
            "error_type": "InputDiscrepancyWarning",
            "error_location": "Error Message vs Source Code Mismatch",
            "severity": "Warning",
            "summary": "Error message does not match the provided source code or programming language"
        },
        "root_cause": {
            "explanation": "The source code is perfectly valid Python ('print(\"Hello World\")'), whereas the error message ('NullPointerException in thread main') is a Java runtime exception. This indicates the error message belongs to a different project or language.",
            "problematic_code": "print('Hello World')",
            "language_rule": "Python does not produce java.lang.NullPointerException."
        },
        "corrected_code": {
            "code": "print('Hello World')  # Code is already valid Python!",
            "changes_made": [
                "No code fix required: Python code is syntactically and semantically valid"
            ],
            "fix_type": "Suggested Improvement"
        },
        "simple_explanation": {
            "explanation": "Your Python code is actually completely fine! The error message you pasted ('NullPointerException') comes from a Java program, not Python. Make sure you copied the correct error message from your terminal.",
            "analogy": "Bringing a bicycle repair manual to fix a flat tire on a submarine."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Pasted error message belongs to Java, but the code is Python.",
                "what_was_changed": "Verified Python code correctness independently.",
                "why_it_works": "Prevents modifying correct code based on an unrelated error log."
            }
        ],
        "prevention_tips": [
            "Double-check terminal outputs to ensure tracebacks match the active script.",
            "Clear your terminal before running tests so old error logs do not confuse you."
        ],
        "confidence": {
            "level": "High",
            "assumptions": ["Code is Python 3; error is Java VM traceback"],
            "limitations": ["Identified conflict between code and error input."]
        }
    },
    "unsupported_language": {
        "error_identification": {
            "error_type": "UnsupportedLanguage",
            "error_location": "Language Specification",
            "severity": "Warning",
            "summary": "The specified programming language (Rust) is currently not officially supported"
        },
        "root_cause": {
            "explanation": "This tool officially supports Python, JavaScript, Java, C++, and C. The input code appears to be Rust ('fn main() { println!... }'). While we can identify the general issue, language-specific linting features are optimized for the 5 supported languages.",
            "problematic_code": 'println!("Hello, world!");',
            "language_rule": "Supported languages: Python, JavaScript, Java, C++, C."
        },
        "corrected_code": {
            "code": 'fn main() {\n    println!("Hello, world!");  // Rust code preserved\n}',
            "changes_made": ["No changes made; language is outside primary support scope"],
            "fix_type": "Suggested Improvement"
        },
        "simple_explanation": {
            "explanation": "You provided Rust code. Currently this assistant is tailored for Python, JavaScript, Java, C++, and C. We recommend selecting one of the supported languages.",
            "analogy": "Speaking Italian to a translator fluent in French, Spanish, German, and English."
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Unsupported programming language provided.",
                "what_was_changed": "Select one of the 5 supported programming languages.",
                "why_it_works": "Ensures prompt templates and rules are fully tuned."
            }
        ],
        "prevention_tips": [
            "Use this tool for Python, JavaScript, Java, C++, and C projects."
        ],
        "confidence": {
            "level": "Medium",
            "assumptions": ["Rust syntax detected"],
            "limitations": ["Rust is outside official scope."]
        }
    },
    "generic": {
        "error_identification": {
            "error_type": "RuntimeError",
            "error_location": "Problematic code segment",
            "severity": "Major",
            "summary": "An issue was detected in the provided code snippet"
        },
        "root_cause": {
            "explanation": "Static analysis detected a potential bug or runtime problem in the logic. Connect a valid Google Gemini API key to activate real-time deep LLM semantic inspection.",
            "problematic_code": "",
            "language_rule": "General language best practices."
        },
        "corrected_code": {
            "code": "# Connect a Gemini API key for live real-time LLM corrections",
            "changes_made": ["Placeholder in demo mode - connect Gemini API key for full AI capability"],
            "fix_type": "Suggested Improvement"
        },
        "simple_explanation": {
            "explanation": "The assistant detected an issue in your code. In Demo Mode, canned patterns are used. For arbitrary live code, please set your GEMINI_API_KEY in .env.",
            "analogy": None
        },
        "debugging_steps": [
            {
                "step_number": 1,
                "what_was_wrong": "Generic error condition.",
                "what_was_changed": "Review logic and variable definitions.",
                "why_it_works": "Resolves common runtime defects."
            }
        ],
        "prevention_tips": [
            "Set APP_MODE=ai and add your GEMINI_API_KEY in .env for unlimited custom analyses.",
            "Always review line numbers cited in the error traceback."
        ],
        "confidence": {
            "level": "Low",
            "assumptions": ["Operating in Demo Mode"],
            "limitations": ["Live dynamic LLM analysis requires API key."]
        }
    }
}


# ---------------------------------------------------------------------------
# BugAnalyzer Class
# ---------------------------------------------------------------------------

class BugAnalyzer:
    """Core bug analyzer coordinating AI-powered and demo-mode debugging."""

    def __init__(self):
        self._api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
        self._model_name: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        self._mode: str = os.environ.get("APP_MODE", "demo").strip().lower()

        self.prompt_manager = PromptManager()
        self._model = None

        if self._api_key and self._api_key != "your_gemini_api_key_here" and self._mode == "ai":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._model = genai.GenerativeModel(self._model_name)
                logger.info("Gemini model '%s' initialized.", self._model_name)
            except Exception as e:
                logger.warning("Failed to initialize Gemini: %s. Falling back to demo mode.", e)
                self._model = None

    def is_ai_mode(self) -> bool:
        """Return True when live Gemini model is active."""
        return self._model is not None

    def get_mode_string(self) -> str:
        """Return readable mode indicator."""
        if self.is_ai_mode():
            return f"🤖 AI Mode (Model: {self._model_name})"
        return "🎮 Demo Mode (deterministic responses)"

    def analyze(
        self,
        code: str,
        error_message: str = "",
        language: str = "",
        prompt_version: str = "final",
    ) -> Dict[str, Any]:
        """Analyze code for bugs and return a formatted display dictionary."""
        start_time = time.time()

        # Handle empty code edge case
        if not code or not code.strip():
            raw = DEMO_RESPONSES["empty_code"].copy()
            formatted = format_for_display(raw)
            formatted["_meta"] = {
                "mode": "demo",
                "prompt_version": prompt_version,
                "duration_seconds": round(time.time() - start_time, 4),
            }
            return formatted

        # Route to AI or Demo
        if self.is_ai_mode():
            raw = self._analyze_with_ai(code, error_message, language, prompt_version)
        else:
            raw = self._analyze_demo(code, error_message, language)

        formatted = format_for_display(raw)
        formatted["_meta"] = {
            "mode": "ai" if self.is_ai_mode() else "demo",
            "prompt_version": prompt_version,
            "duration_seconds": round(time.time() - start_time, 4),
        }
        return formatted

    def _analyze_with_ai(
        self, code: str, error_message: str, language: str, prompt_version: str
    ) -> dict:
        """Query the Gemini model."""
        try:
            prompt = self.prompt_manager.get_prompt(
                version=prompt_version,
                code=code,
                error_message=error_message,
                language=language or "Auto-Detect",
            )
            response = self._model.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 4096},
            )
            return parse_ai_response(response.text)
        except Exception as e:
            logger.error("AI query failed: %s", e)
            return self._error_response(f"AI analysis failed: {e}")

    def _analyze_demo(self, code: str, error_message: str, language: str) -> dict:
        """Pattern matching for demo scenarios."""
        code_str = code or ""
        code_lower = code_str.lower()
        err_str = error_message or ""
        err_lower = err_str.lower()
        lang_lower = (language or "").lower()

        # 1. Empty code
        if not code_str.strip():
            return DEMO_RESPONSES["empty_code"].copy()

        # 2. Unsupported language
        if "rust" in lang_lower or "fn main" in code_lower:
            return DEMO_RESPONSES["unsupported_language"].copy()

        # 3. Misleading error (Java exception on Python code)
        if ("python" in lang_lower or "print(" in code_lower) and "nullpointer" in err_lower:
            return DEMO_RESPONSES["misleading_error"].copy()

        # 4. Ambiguous language / missing main
        if "int x = 5" in code_lower and ("main" in err_lower or "undefined reference" in err_lower):
            return DEMO_RESPONSES["ambiguous_language"].copy()

        # 5. Missing error message with type mismatch
        if not err_str.strip() and "add(5, '3')" in code_str:
            return DEMO_RESPONSES["missing_error"].copy()

        # 6. Python SyntaxError (print)
        if "print(" in code_lower and ("syntaxerror" in err_lower or code_lower.count("(") > code_lower.count(")")):
            return DEMO_RESPONSES["python_syntax"].copy()

        # 7. Python ZeroDivisionError
        if "zerodivision" in err_lower or ("/" in code_lower and ", 0)" in code_lower):
            return DEMO_RESPONSES["python_zerodivision"].copy()

        # 8. JavaScript ReferenceError / TDZ
        if "referenceerror" in err_lower or ("console.log(" in code_lower and "let " in code_lower):
            return DEMO_RESPONSES["javascript_reference"].copy()

        # 9. Java NullPointerException
        if "nullpointer" in err_lower or ("java" in lang_lower and "null" in code_lower and ".length()" in code_lower):
            return DEMO_RESPONSES["java_nullpointer"].copy()

        # 10. C++ Missing semicolon
        if "expected ';'" in err_lower or ("iostream" in code_lower and "cout" in code_lower and ";" not in code_lower.split("cout")[-1].split("\n")[0]):
            return DEMO_RESPONSES["cpp_missing_semicolon"].copy()

        # 11. C Array Bounds / Segfault
        if "segmentation" in err_lower or ("arr[10]" in code_lower and "arr[5]" in code_lower):
            return DEMO_RESPONSES["c_array_bounds"].copy()

        # 12. Python Logical off-by-one
        if "range(1, len(" in code_lower or "expected output: 15" in err_lower:
            return DEMO_RESPONSES["python_off_by_one"].copy()

        return DEMO_RESPONSES["generic"].copy()

    def _error_response(self, message: str) -> dict:
        return {
            "error_identification": {
                "error_type": "AnalysisError",
                "error_location": "N/A",
                "severity": "Warning",
                "summary": message,
            },
            "root_cause": {
                "explanation": message,
                "problematic_code": "",
                "language_rule": "",
            },
            "corrected_code": {
                "code": "",
                "changes_made": [],
                "fix_type": "N/A",
            },
            "simple_explanation": {
                "explanation": message,
                "analogy": None,
            },
            "debugging_steps": [],
            "prevention_tips": [],
            "confidence": {
                "level": "Low",
                "assumptions": [],
                "limitations": [message],
            },
        }

    def compare_prompts(
        self, code: str, error_message: str, language: str
    ) -> Dict[str, Any]:
        """Run input through V1, V2, and V3 prompts for empirical comparison."""
        results = {}
        for version in ["v1", "v2", "v3"]:
            start_time = time.time()
            try:
                res = self.analyze(
                    code=code,
                    error_message=error_message,
                    language=language,
                    prompt_version=version,
                )
                results[version] = res
            except Exception as e:
                results[version] = {
                    "error": str(e),
                    "_meta": {
                        "mode": "error",
                        "prompt_version": version,
                        "duration_seconds": round(time.time() - start_time, 4),
                    },
                }
        return results
