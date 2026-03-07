from __future__ import annotations

from .gemini_provider import GeminiProvider
from .registry import register_provider

register_provider("gemini", GeminiProvider)
