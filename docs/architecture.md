# System Architecture

## Overview

The Bug Explanation and Fix Assistant is a web-based AI-powered debugging tool built with a modular architecture. It uses Google Gemini as the AI backbone and Streamlit for the frontend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT FRONTEND                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │Code Input│  │Error     │  │Language   │  │Results    │  │
│  │Module    │  │Input     │  │Selector   │  │Dashboard  │  │
│  │          │  │Module    │  │           │  │           │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └─────▲─────┘  │
│       │              │              │              │         │
│       └──────────────┴──────┬───────┘              │         │
│                             ▼                      │         │
│  ┌──────────────────────────────────────────────┐  │         │
│  │              BUG ANALYZER MODULE             │  │         │
│  │  ┌────────────────┐  ┌────────────────────┐  │  │         │
│  │  │Language        │  │Prompt Manager      │  │  │         │
│  │  │Detector        │  │(V1, V2, V3, Final) │  │  │         │
│  │  └────────────────┘  └────────┬───────────┘  │  │         │
│  │                               ▼              │  │         │
│  │  ┌────────────────────────────────────────┐  │  │         │
│  │  │         AI / Demo Engine               │  │  │         │
│  │  │  ┌──────────┐    ┌──────────────┐      │  │  │         │
│  │  │  │Gemini API│    │Demo Responses│      │  │  │         │
│  │  │  │(AI Mode) │    │(Demo Mode)   │      │  │  │         │
│  │  │  └──────────┘    └──────────────┘      │  │  │         │
│  │  └────────────────────┬───────────────────┘  │  │         │
│  │                       ▼                      │  │         │
│  │  ┌────────────────────────────────────────┐  │  │         │
│  │  │       Response Formatter               │──┼──┘         │
│  │  │  JSON Parser → Normalizer → Display    │  │            │
│  │  └────────────────────────────────────────┘  │            │
│  └──────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘

                    EXTERNAL SERVICES
         ┌──────────────────────────────┐
         │  Google Gemini API           │
         │  (gemini-2.0-flash)          │
         │  - Text generation           │
         │  - JSON structured output    │
         └──────────────────────────────┘
```

## Component Details

### 1. Streamlit Frontend (`app.py`)

The main application entry point providing:
- **Code Input Module**: Text area for source code with syntax highlighting placeholder
- **Error Input Module**: Text area for error messages
- **Language Selector**: Dropdown with auto-detection support
- **Results Dashboard**: Expandable sections for all analysis components
- **Prompt Comparison Page**: Side-by-side comparison of prompt versions
- **Prompt Viewer Page**: View full prompt templates and metadata
- **About Page**: Tool description and configuration guide

### 2. Language Detector (`modules/language_detector.py`)

Keyword and pattern-based language detection engine:
- Maintains pattern databases for Python, JavaScript, Java, C++, and C
- Uses weighted scoring with keyword matching, regex patterns, and error message analysis
- Includes C vs C++ disambiguation logic
- Returns language name and confidence score (0.0 to 0.95)

### 3. Bug Analyzer (`modules/bug_analyzer.py`)

Core analysis engine with dual-mode operation:
- **AI Mode**: Sends prompts to Google Gemini API with configurable parameters
- **Demo Mode**: Returns deterministic sample responses when API key is unavailable
- Handles empty input, edge cases, and API errors gracefully
- Provides prompt comparison functionality across all versions

### 4. Prompt Manager (`modules/prompt_manager.py`)

Manages prompt template lifecycle:
- Loads prompt templates from versioned directories
- Renders templates with code, error message, and language variables
- Provides metadata access for prompt version information
- Caches loaded prompts for performance

### 5. Response Formatter (`modules/response_formatter.py`)

Multi-format response parser:
- **JSON Parser**: Extracts and validates JSON from AI responses (V3/final)
- **Text Parser**: Extracts structured sections from free-form text (V1/V2)
- **Normalizer**: Converts all formats to a standard display dictionary
- **Display Formatter**: Adds UI-ready elements (icons, colors, labels)

## Data Flow

```
User Input → Language Detection → Prompt Selection → Prompt Rendering
     → AI/Demo Analysis → Response Parsing → Display Formatting → UI
```

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API authentication | (required for AI mode) |
| `APP_MODE` | Operating mode: "ai" or "demo" | "demo" |
| `GEMINI_MODEL` | Gemini model identifier | "gemini-2.0-flash" |

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Streamlit | ≥1.28.0 |
| Backend | Python | ≥3.8 |
| AI Engine | Google Gemini | gemini-2.0-flash |
| Config | python-dotenv | ≥1.0.0 |
| AI SDK | google-generativeai | ≥0.8.0 |
