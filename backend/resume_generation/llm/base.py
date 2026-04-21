from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: Optional[str] = None
    max_output_tokens: int = 8192
    temperature: float = 0.3


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
