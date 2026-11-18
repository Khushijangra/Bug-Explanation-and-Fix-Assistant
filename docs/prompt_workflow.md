# Prompt Engineering Workflow

## Overview

This document records the iterative prompt engineering process used to develop the Bug Explanation and Fix Assistant's AI prompts. Three distinct versions were created, each improving upon the previous one based on observed outputs and identified limitations.

## Prompt Iteration Log

### Version 1 — Basic Prompt

**Goal:** Create the simplest possible prompt that receives code and an error message and identifies the issue.

**Approach:** Minimal instruction set — just tell the AI what input it has and what output we want.

**Full Prompt Text:**
```
You are a programming assistant. Given the following code and error message,
identify the bug, suggest a fix, and explain the issue.

Code:
{code}

Error Message:
{error_message}

Programming Language: {language}

Please provide:
1. What the error is
2. How to fix it
3. A brief explanation
```

**Variables:**
| Variable | Meaning |
|----------|---------|
| `{code}` | User's source code |
| `{error_message}` | The error message received |
| `{language}` | Programming language |

**Observed Results:**
- ✅ Generally identifies the correct error type
- ✅ Provides basic fix suggestions
- ❌ Output format varies significantly between runs
- ❌ No error classification or severity assessment
- ❌ Explanations may use jargon inappropriate for beginners
- ❌ No step-by-step debugging guidance
- ❌ No confidence or uncertainty indication
- ❌ Inconsistent handling of edge cases

**Limitations Recorded:**
1. No structured output format → difficult to parse programmatically
2. No role-based instructions → inconsistent persona
3. No error classification → missing context for the user
4. No confidence assessment → user can't gauge reliability
5. No edge case handling → may crash or give nonsensical output on empty inputs

---

### Version 2 — Structured Prompt

**Goal:** Improve V1 by adding role instructions, structured sections, language context, and beginner-friendly requirements.

**What Changed from V1:**
1. Added expert role definition ("expert software debugging assistant")
2. Added beginner audience context
3. Structured output into 6 clear sections
4. Required severity assessment
5. Added prevention tips section
6. Required uncertainty acknowledgment
7. Added code blocks for input formatting

**Why These Changes Were Made:**
- Role definition ensures consistent persona across runs
- Structured sections make output predictable and parseable
- Severity assessment helps users prioritize which bugs to fix first
- Prevention tips add educational value beyond just fixing the immediate bug
- Beginner context prompts simpler language use

**Full Prompt Text:**
```
You are an expert software debugging assistant specializing in {language}
programming. Your role is to help students and junior developers understand
and fix bugs in their code.

## Context
- Programming Language: {language}
- The user is a beginner who needs clear, simple explanations.

## Input
### Source Code
```{language}
{code}
```

### Error Message
```
{error_message}
```

## Instructions
Analyze the provided code and error message, then provide a comprehensive
debugging report with the following sections:

### 1. Error Identification
- Identify the type of error (syntax, runtime, logical, etc.)
- Locate where in the code the error occurs (line number if possible)
- Assess the severity (Critical / Major / Minor / Warning)
- Provide a one-line summary of the error

### 2. Root Cause Analysis
- Explain exactly why this error occurs
- Identify the specific problematic code or logic
- Reference the relevant programming language rules or conventions

### 3. Corrected Code
- Provide the complete corrected code
- Preserve the original intended functionality
- Mark changes with comments explaining what was fixed

### 4. Simple Explanation
- Explain the problem as if talking to a beginner
- Use analogies if helpful
- Avoid unnecessary jargon

### 5. Step-by-Step Debugging Guide
For each fix applied:
- Step N: What was wrong → What was changed → Why it works now

### 6. Prevention Tips
- How to avoid this type of error in the future
- Relevant best practices

Please be thorough but concise. If you are uncertain about anything, say so clearly.
```

**Observed Results:**
- ✅ Consistent section structure across runs
- ✅ Better beginner-friendly explanations
- ✅ Error severity consistently reported
- ✅ Prevention tips provide educational value
- ✅ Root cause analysis is more detailed
- ⚠️ Output is text-based markdown, harder to parse programmatically
- ❌ No formal error classification taxonomy
- ❌ No JSON output for consistent parsing
- ❌ No confidence scoring system
- ❌ Limited edge case handling

**Improvement Over V1:**
- Output consistency: Significantly improved
- Explanation quality: Better for beginners
- Structural completeness: 6 sections vs. 3 bullet points
- Still lacks: Programmatic parseability, edge case handling

---

### Version 3 — Optimized Final Prompt

**Goal:** Create a production-ready prompt with JSON output, error taxonomy, confidence scoring, edge case handling, and comprehensive debugging guidance.

**What Changed from V2:**
1. Added named persona ("BugFixBot") for consistent identity
2. Added core principles (accuracy, beginner-friendly, complete, structured)
3. Created formal error classification taxonomy (9 categories)
4. Required strict JSON output matching a defined schema
5. Added confidence assessment with assumptions and limitations
6. Added explicit edge case handling instructions (5 scenarios)
7. Added fix type distinction (Confirmed Fix vs Suggested Improvement)
8. Added real-world analogy field for beginners
9. Added multi-bug handling with severity ordering
10. Added inline change markers (# FIXED: / // FIXED:)

**Why These Changes Were Made:**
- JSON output enables reliable programmatic parsing and display
- Error taxonomy provides consistent classification across all languages
- Confidence scoring helps users gauge the reliability of suggestions
- Edge case handling prevents crashes and nonsensical outputs
- Fix type distinction prevents users from treating suggestions as confirmed fixes
- Analogies make complex concepts accessible to beginners
- Multi-bug handling addresses real-world code that often has multiple issues

**Full Prompt Text:** See `prompts/v3/prompt.txt`

**Variables:**
| Variable | Meaning |
|----------|---------|
| `{code}` | User's source code |
| `{error_message}` | The error message received |
| `{language}` | Programming language (display name) |
| `{language_lower}` | Programming language (lowercase, for code blocks) |

**Output Format:** Structured JSON with 7 top-level sections

**Observed Results:**
- ✅ Consistent JSON output across runs
- ✅ Reliable programmatic parsing
- ✅ Comprehensive error classification
- ✅ Confidence scoring with assumptions
- ✅ Graceful edge case handling
- ✅ Excellent beginner explanations with analogies
- ✅ Multi-bug detection and ordering
- ✅ Clear fix type distinction
- ⚠️ Longer prompts use more tokens
- ⚠️ Occasional JSON formatting issues require fallback parsing

**Improvement Over V2:**
- Parseability: JSON vs free text — dramatically improved
- Consistency: Schema-enforced structure
- Edge cases: Explicit handling instructions
- Confidence: Formal scoring system
- Overall quality: Suitable for production use

---

## Prompt Comparison Summary

| Aspect | V1 (Basic) | V2 (Structured) | V3 (Optimized) |
|--------|-----------|-----------------|----------------|
| **Lines of Prompt** | ~15 | ~50 | ~120 |
| **Output Format** | Free text | Structured text | JSON |
| **Role Definition** | None | Expert assistant | Named persona + principles |
| **Error Classification** | None | Basic (syntax/runtime/logical) | Taxonomy (9 categories) |
| **Severity Assessment** | No | Yes | Yes |
| **Root Cause** | Minimal | Detailed | Detailed + language rules |
| **Corrected Code** | Maybe | Yes | Yes + change markers |
| **Step-by-Step** | No | Yes | Yes (structured JSON) |
| **Prevention Tips** | No | Yes | Yes |
| **Confidence Level** | No | Implicit | Explicit + assumptions |
| **Edge Cases** | None | Minimal | 5 explicit scenarios |
| **Beginner Friendliness** | Low | Medium | High (analogies) |
| **Programmatic Parsing** | Difficult | Possible | Reliable |
| **Consistency** | Low | Medium | High |

## Workflow Diagram

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  V1      │    │  V2      │    │  V3      │
│  Basic   │───▶│ Structured│───▶│ Optimized│
│  Prompt  │    │  Prompt  │    │  Prompt  │
└──────────┘    └──────────┘    └──────────┘
     │               │               │
     ▼               ▼               ▼
 Free text      Markdown text    JSON output
 3 items        6 sections       7 sections
 No role        Expert role      Named persona
 No edge cases  Basic edges      5 edge cases
                                     │
                                     ▼
                              ┌──────────┐
                              │  FINAL   │
                              │  (= V3)  │
                              │ Production│
                              └──────────┘
```

## Key Learnings

1. **Role definition matters**: Adding an expert role significantly improved output quality and consistency.
2. **Structured output > free text**: Each level of structure improved reliability.
3. **JSON is essential for applications**: Free text is unpredictable; JSON enables reliable UI rendering.
4. **Edge cases need explicit instructions**: The model handles edge cases much better when told exactly what to do.
5. **Confidence scoring builds trust**: Users trust the tool more when it honestly communicates uncertainty.
6. **Analogies help beginners**: Real-world comparisons make technical concepts click for newcomers.
7. **More tokens, better results**: The investment in a longer prompt pays off in output quality.
