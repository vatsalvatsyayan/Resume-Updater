"""
Google Gemini LLM provider.

Uses the free tier (Gemini 2.0 Flash or 2.5 Flash). Set GOOGLE_API_KEY or
GEMINI_API_KEY in the environment.
"""

from __future__ import annotations

import os
from typing import Optional

from .base import LLMConfig, LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini API (gemini-2.0-flash recommended for free tier)."""

    def __init__(self, config: LLMConfig) -> None:
        self._config = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError as e:
                raise ImportError(
                    "google-generativeai is required for Gemini. "
                    "Install with: pip install google-generativeai"
                ) from e
            api_key = (
                self._config.api_key
                or os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
            )
            if not api_key:
                raise ValueError(
                    "Gemini API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY."
                )
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(
                model_name=self._config.model,
                generation_config={
                    "max_output_tokens": self._config.max_output_tokens,
                    "temperature": self._config.temperature,
                },
            )
        return self._client

    @property
    def name(self) -> str:
        return f"gemini:{self._config.model}"

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        model = self._get_client()
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        gen_config = {}
        if max_tokens is not None:
            gen_config["max_output_tokens"] = max_tokens
        if temperature is not None:
            gen_config["temperature"] = temperature

        if gen_config:
            response = model.generate_content(
                full_prompt,
                generation_config=gen_config,
            )
        else:
            response = model.generate_content(full_prompt)

        if not response.text:
            raise RuntimeError(
                "Gemini returned empty response. "
                "Check safety settings or try a different prompt."
            )
        return response.text.strip()
