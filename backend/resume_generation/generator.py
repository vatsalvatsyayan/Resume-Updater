from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from core.config import settings

from .pdf_template import build_pdf_template as build_pdf
from .schemas.input_schema import ResumeGeneratorInput
from .schemas.output_schema import (
    TailoredResume,
    TailoredEducation,
    TailoredWorkExperience,
    TailoredProject,
    TailoredCertification,
    TailoredVolunteer,
    TailoredLeadership,
)
from .tailor import tailor_resume
from .llm import LLMConfig


def input_to_tailored_no_llm(data: Union[ResumeGeneratorInput, dict]) -> TailoredResume:
    """Convert input schema to TailoredResume without calling the LLM (for PDF-only testing)."""
    if isinstance(data, dict):
        data = ResumeGeneratorInput.model_validate(data)
    pi = data.personalInfo
    education = [
        TailoredEducation(
            universityName=e.universityName,
            courseName=e.courseName,
            courseType=e.courseType,
            major=e.major,
            gpa=e.gpa,
            location=e.location,
            startDate=e.startDate,
            endDate=e.endDate,
            isPresent=e.isPresent,
            highlight=None,
        )
        for e in data.education
    ]
    work = [
        TailoredWorkExperience(
            companyName=w.companyName,
            position=w.position,
            location=w.location,
            startDate=w.startDate,
            endDate=w.endDate,
            isPresent=w.isPresent,
            bullets=[w.description] if w.description else ([w.summary] if w.summary else []),
        )
        for w in data.workExperience
    ]
    projects = [
        TailoredProject(
            projectName=p.projectName,
            link=p.link or None,
            techStack=p.techStack or [],
            bullets=[p.description] if p.description else ([p.summary] if p.summary else []),
        )
        for p in data.projects
    ]
    sk = data.skills
    skills = (
        (sk.programmingLanguages or [])
        + (sk.frameworks or [])
        + (sk.databases or [])
        + (sk.toolsAndTechnologies or [])
        + (sk.cloud or [])
        + (sk.ai or [])
        + (sk.other or [])
    )
    certs = [
        TailoredCertification(name=c.name, issuingOrganization=c.issuingOrganization or "")
        for c in data.certifications
    ]
    volunteer = [
        TailoredVolunteer(
            organizationName=v.organizationName,
            role=v.role,
            bullets=[v.description] if v.description else [],
        )
        for v in data.volunteer
    ]
    leadership = [
        TailoredLeadership(
            title=l.title,
            organization=l.organization,
            bullets=[l.description] if l.description else [],
        )
        for l in data.leadership
    ]
    summary = None
    if data.workExperience and data.workExperience[0].summary:
        summary = data.workExperience[0].summary
    return TailoredResume(
        name=pi.name or "",
        email=pi.email or "",
        portfolioWebsite=pi.portfolioWebsite,
        githubUrl=pi.githubUrl,
        linkedinUrl=pi.linkedinUrl,
        professionalSummary=summary,
        education=education,
        workExperience=work,
        projects=projects,
        skills=skills,
        certifications=certs,
        volunteer=volunteer,
        leadership=leadership,
        extraSections=[],
    )


def _get_llm_config() -> LLMConfig:
    api_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError(
            "Gemini API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY in backend/.env"
        )
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
    """Generate tailored resume and PDF using the default template."""
    if isinstance(data, dict):
        data = ResumeGeneratorInput.model_validate(data)
    llm_config = _get_llm_config()
    tailored = tailor_resume(data, llm_config)
    result = build_pdf(tailored, output=output_pdf_path)
    if output_pdf_path is not None:
        return tailored, result
    return tailored, result
