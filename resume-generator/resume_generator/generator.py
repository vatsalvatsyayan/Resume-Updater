"""
Main entry point: generate a tailored resume and optionally a PDF.

Use this from the backend or from the test script.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .config import ResumeGeneratorConfig
from .schemas import ResumeGeneratorInput, TailoredResume
from .services import TailorService
from .pdf import PDFBuilder


def generate_resume(
    data: Union[ResumeGeneratorInput, dict],
    *,
    config: Optional[ResumeGeneratorConfig] = None,
    output_pdf_path: Optional[Union[str, Path]] = None,
) -> tuple[TailoredResume, Union[bytes, Path]]:
    """
    Tailor the resume for the job and build a PDF.

    Args:
        data: ResumeGeneratorInput or a dict matching that schema (e.g. from API JSON).
        config: Optional config; uses env-based defaults if not provided.
        output_pdf_path: If set, write PDF to this path and return it; otherwise return PDF bytes.

    Returns:
        (tailored_resume, pdf_path_or_bytes)
        - tailored_resume: TailoredResume instance.
        - pdf_path_or_bytes: If output_pdf_path was set, returns the Path; else returns PDF bytes.

    Raises:
        ValueError: Invalid input or LLM response.
    """
    if config is None:
        config = ResumeGeneratorConfig()
    if isinstance(data, dict):
        data = ResumeGeneratorInput.model_validate(data)

    tailor = TailorService(llm_config=config.llm_config())
    tailored = tailor.tailor(data)

    pdf_builder = PDFBuilder()
    if output_pdf_path is not None:
        path = pdf_builder.build(tailored, output=output_pdf_path)
        return tailored, path
    pdf_bytes = pdf_builder.build(tailored, output=None)
    return tailored, pdf_bytes
