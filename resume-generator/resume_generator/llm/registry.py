"""
Registry for LLM providers. Allows swapping the model by name.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import LLMConfig, LLMProvider

_providers: Dict[str, Type[LLMProvider]] = {}


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """Register an LLM provider class under a name."""
    _providers[name.lower()] = provider_class


def get_provider(config: LLMConfig) -> LLMProvider:
    """
    Instantiate the appropriate provider from config.

    Raises:
        ValueError: If provider name is not registered.
    """
    key = config.provider.lower()
    if key not in _providers:
        available = ", ".join(_providers.keys()) or "(none)"
        raise ValueError(
            f"Unknown LLM provider: {config.provider}. Available: {available}"
        )
    return _providers[key](config)
