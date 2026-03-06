"""
Register built-in LLM providers. Import this module to ensure Gemini (and any
future providers) are registered before calling get_provider().
"""

from __future__ import annotations

from .gemini_provider import GeminiProvider
from .registry import register_provider

register_provider("gemini", GeminiProvider)
