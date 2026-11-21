"""
Configuration Module
Central source of truth for application configuration, environment settings,
and mode detection (AI Mode vs. Demo Mode).
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration container."""
    app_mode: str              # 'ai' or 'demo'
    gemini_api_key: Optional[str]
    gemini_model: str
    request_timeout: int       # seconds
    max_output_tokens: int
    temperature: float

    @property
    def is_ai_mode(self) -> bool:
        """True only if APP_MODE is explicitly 'ai' and a valid API key is present."""
        return self.app_mode == "ai" and self.has_valid_api_key

    @property
    def has_valid_api_key(self) -> bool:
        """True if GEMINI_API_KEY is configured with a non-placeholder value."""
        if not self.gemini_api_key:
            return False
        key = self.gemini_api_key.strip()
        invalid_placeholders = {
            "",
            "your_gemini_api_key_here",
            "your_key_here",
            "none",
            "null",
        }
        return key.lower() not in invalid_placeholders and len(key) > 8

    @property
    def mode_display_string(self) -> str:
        """Human-readable display string for current mode."""
        if self.app_mode == "ai":
            if self.has_valid_api_key:
                return f"🤖 AI Mode ({self.gemini_model})"
            return "⚠️ AI Mode (Missing API Key - Configuration Required)"
        return "🎮 Demo Mode (Deterministic Verification)"


def get_app_config(
    custom_mode: Optional[str] = None,
    custom_api_key: Optional[str] = None,
) -> AppConfig:
    """
    Read configuration from Streamlit Cloud Secrets, environment variables, or explicit overrides.

    Priority for API Key:
    1. custom_api_key (if explicitly provided via UI)
    2. Streamlit Cloud Secrets (st.secrets["GEMINI_API_KEY"])
    3. Environment variables (os.environ["GEMINI_API_KEY"] or .env)

    Priority for Mode:
    1. custom_mode (if explicitly provided via UI)
    2. Streamlit Cloud Secrets (st.secrets["APP_MODE"])
    3. Environment variables (os.environ["APP_MODE"] or .env)
    4. Default: 'demo'

    Rules:
    - If APP_MODE='demo', demo mode is used (offline deterministic).
    - If APP_MODE='ai', genuine AI execution is attempted when key is present.
    - If no key is configured, the application never crashes and reports clear status.
    """
    secret_key = None
    secret_mode = None

    # Safely query Streamlit Cloud Secrets without crashing in non-Streamlit environments
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            try:
                secret_key = st.secrets.get("GEMINI_API_KEY", None)
            except Exception:
                secret_key = None
            try:
                secret_mode = st.secrets.get("APP_MODE", None)
            except Exception:
                secret_mode = None
    except Exception:
        pass

    # Resolve mode
    if custom_mode:
        raw_mode = custom_mode
    elif secret_mode:
        raw_mode = str(secret_mode)
    else:
        raw_mode = os.environ.get("APP_MODE", "demo")

    raw_mode = str(raw_mode).strip().lower()
    app_mode = "ai" if raw_mode == "ai" else "demo"

    # Resolve API Key
    if custom_api_key is not None and custom_api_key.strip():
        api_key = custom_api_key.strip()
    elif secret_key:
        api_key = str(secret_key).strip() or None
    else:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip() or None

    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()
    timeout = int(os.environ.get("GEMINI_TIMEOUT_SECONDS", "30"))

    return AppConfig(
        app_mode=app_mode,
        gemini_api_key=api_key,
        gemini_model=model_name,
        request_timeout=timeout,
        max_output_tokens=4096,
        temperature=0.3,
    )
