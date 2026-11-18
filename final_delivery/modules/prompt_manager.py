"""
Prompt Manager Module
Manages prompt versions and provides prompt rendering for different analysis modes.
"""

import os
import json
from typing import Dict, List, Optional, Any


class PromptManager:
    """Manages different prompt versions for bug analysis."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the PromptManager.

        Args:
            prompts_dir: Path to the prompts directory. Defaults to ../prompts/
        """
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self.prompts_dir = prompts_dir
        self._prompts_cache: Dict[str, str] = {}
        self._metadata_cache: Dict[str, dict] = {}

    def _load_prompt(self, version: str) -> str:
        """Load a prompt template from file."""
        norm_v = version.strip().lower()
        if norm_v not in self._prompts_cache:
            prompt_path = os.path.join(self.prompts_dir, norm_v, "prompt.txt")
            if not os.path.exists(prompt_path):
                # Fallback to final if unknown
                prompt_path = os.path.join(self.prompts_dir, "final", "prompt.txt")
                if not os.path.exists(prompt_path):
                    raise FileNotFoundError(f"Prompt file not found for version: {version}")
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._prompts_cache[norm_v] = f.read()
        return self._prompts_cache[norm_v]

    def _load_metadata(self, version: str) -> dict:
        """Load prompt metadata from file."""
        norm_v = version.strip().lower()
        if norm_v not in self._metadata_cache:
            meta_path = os.path.join(self.prompts_dir, norm_v, "metadata.json")
            if not os.path.exists(meta_path):
                meta_path = os.path.join(self.prompts_dir, "final", "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self._metadata_cache[norm_v] = json.load(f)
            else:
                self._metadata_cache[norm_v] = {
                    "version": norm_v,
                    "name": norm_v.upper(),
                    "description": f"Prompt version {norm_v}",
                    "output_format": "text",
                    "limitations": [],
                }
        return self._metadata_cache[norm_v]

    def get_prompt(self, version: str, code: str, error_message: str, language: str) -> str:
        """
        Render a prompt template with the given variables.

        Args:
            version: Prompt version (v1, v2, v3, final)
            code: Source code
            error_message: Error message
            language: Programming language

        Returns:
            Rendered prompt string
        """
        template = self._load_prompt(version)
        return template.format(
            code=code,
            error_message=error_message,
            language=language or "Auto-Detect",
            language_lower=language.lower() if language else "text",
        )

    def get_metadata(self, version: str) -> dict:
        """Get metadata for a prompt version."""
        return self._load_metadata(version)

    def get_prompt_info(self, version: str) -> dict:
        """
        Get normalized prompt metadata info for UI display.
        Ensures consistent keys: name, description, format, improvements, limitations, purpose.
        """
        raw = self._load_metadata(version)
        improvements = raw.get("expected_improvements", [])
        if isinstance(improvements, str):
            improvements = [improvements]
        elif not improvements:
            improvements = raw.get("improvements_over_v1", raw.get("improvements_over_v2", []))

        return {
            "name": raw.get("name", version.upper()),
            "version": raw.get("version", version),
            "description": raw.get("description", raw.get("purpose", "Prompt template")),
            "purpose": raw.get("purpose", ""),
            "format": raw.get("output_format", "text"),
            "improvements": improvements,
            "limitations": raw.get("limitations", raw.get("remaining_issues", [])),
            "model_settings": raw.get("model_settings", {"temperature": 0.3}),
            "variables": raw.get("variables", []),
        }

    def get_prompt_text(self, version: str) -> str:
        """Get raw prompt template text."""
        return self._load_prompt(version)

    def get_template(self, version: str) -> str:
        """Alias for get_prompt_text to ensure API compatibility."""
        return self._load_prompt(version)

    def get_all_versions(self) -> List[str]:
        """Return list of available prompt versions in standard order."""
        return ["v1", "v2", "v3", "final"]

    def get_version_info(self, version: str) -> dict:
        """Get combined version info including template and metadata."""
        return {
            "version": version,
            "template": self._load_prompt(version),
            "metadata": self._load_metadata(version),
            "info": self.get_prompt_info(version),
        }
