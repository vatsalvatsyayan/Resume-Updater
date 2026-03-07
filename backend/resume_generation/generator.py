from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from core.config import settings

from .pdf import build_pdf
from .schemas.input_schema import ResumeGeneratorInput
from .schemas.output_schema import TailoredResume
from .tailor import tailor_resume
from .llm import LLMConfig


def _get_llm_config() -> LLMConfig:
    api_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
    return LLMConfig(
        provider=settings.RESUME_LLM_PROVIDER,
        model=settings.RESUME_LLM_MODEL,
        api_key=api_key,
        max_output_tokens=8192,
        temperature=0.3,
    )


def generate_resume(
    data: Union[ResumeGeneratorInput, dict],
    *,
    output_pdf_path: Optional[Union[str, Path]] = None,
) -> tuple[TailoredResume, Union[bytes, Path]]:
    if isinstance(data, dict):
        data = ResumeGeneratorInput.model_validate(data)
    llm_config = _get_llm_config()
    tailored = tailor_resume(data, llm_config)
    if output_pdf_path is not None:
        path = build_pdf(tailored, output=output_pdf_path)
        return tailored, path
    pdf_bytes = build_pdf(tailored, output=None)
    return tailored, pdf_bytes
