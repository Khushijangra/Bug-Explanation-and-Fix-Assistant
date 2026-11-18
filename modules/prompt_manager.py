"""
Prompt Manager Module
Manages prompt versions and provides prompt rendering for different analysis modes.
"""

import os
import json
from typing import Dict, Optional


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
        if version not in self._prompts_cache:
            prompt_path = os.path.join(self.prompts_dir, version, "prompt.txt")
            if not os.path.exists(prompt_path):
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._prompts_cache[version] = f.read()
        return self._prompts_cache[version]

    def _load_metadata(self, version: str) -> dict:
        """Load prompt metadata from file."""
        if version not in self._metadata_cache:
            meta_path = os.path.join(self.prompts_dir, version, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self._metadata_cache[version] = json.load(f)
            else:
                self._metadata_cache[version] = {}
        return self._metadata_cache[version]

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
            language=language,
            language_lower=language.lower() if language else "text"
        )

    def get_metadata(self, version: str) -> dict:
        """Get metadata for a prompt version."""
        return self._load_metadata(version)

    def get_all_versions(self) -> list:
        """Return list of available prompt versions."""
        versions = []
        for d in ["v1", "v2", "v3", "final"]:
            prompt_path = os.path.join(self.prompts_dir, d, "prompt.txt")
            if os.path.exists(prompt_path):
                versions.append(d)
        return versions

    def get_prompt_text(self, version: str) -> str:
        """Get raw prompt template text."""
        return self._load_prompt(version)

    def get_version_info(self, version: str) -> dict:
        """Get combined version info including template and metadata."""
        return {
            "version": version,
            "template": self._load_prompt(version),
            "metadata": self._load_metadata(version)
        }
