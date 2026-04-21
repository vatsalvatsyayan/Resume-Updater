from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Optional

from pydantic import ValidationError

from core.config import settings

from .llm import LLMConfig, get_provider
from .schemas.input_schema import ResumeGeneratorInput
from .schemas.output_schema import (
    TailoredCertification,
    TailoredEducation,
    TailoredLeadership,
    TailoredResume,
    TailoredProject,
    TailoredSection,
    TailoredVolunteer,
    TailoredWorkExperience,
)


_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _parse_resume_date(raw: str | None) -> date | None:
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    normalized = text.replace(",", " ").strip().lower()
    if normalized in {"present", "current", "now", "ongoing"}:
        return date.max

    # ISO-like first (YYYY-MM-DD / YYYY-MM).
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return datetime.strptime(text, "%Y-%m-%d").date()
        if re.fullmatch(r"\d{4}-\d{2}", text):
            return datetime.strptime(text, "%Y-%m").date().replace(day=1)
    except ValueError:
        pass

    # MM/YY or MM/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{2}|\d{4})", text)
    if m:
        month = int(m.group(1))
        year_raw = m.group(2)
        year = int(year_raw)
        if len(year_raw) == 2:
            year += 2000
        if 1 <= month <= 12:
            try:
                return date(year, month, 1)
            except ValueError:
                return None

    # Month YYYY (abbr/full), e.g. "Mar 2019", "March 2019"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{4})", normalized)
    if m:
        month = _MONTHS.get(m.group(1).lower())
        year = int(m.group(2))
        if month:
            try:
                return date(year, month, 1)
            except ValueError:
                return None

    # Year-only fallback.
    if re.fullmatch(r"\d{4}", text):
        try:
            return date(int(text), 1, 1)
        except ValueError:
            return None
    return None


def _work_sort_key(item: TailoredWorkExperience) -> tuple[date, date]:
    # Present roles should appear first. Otherwise sort by end date, then start date.
    start = _parse_resume_date(item.startDate) or date.min
    if item.isPresent:
        end = date.max
    else:
        end = _parse_resume_date(item.endDate) or start
    return (end, start)


def _sort_work_reverse_chrono(items: list[TailoredWorkExperience]) -> list[TailoredWorkExperience]:
    return sorted(items, key=_work_sort_key, reverse=True)


def _profile_to_context(data: ResumeGeneratorInput) -> str:
    return json.dumps(
        {
            "personalInfo": data.personalInfo.model_dump(),
            "education": [e.model_dump() for e in data.education],
            "workExperience": [w.model_dump() for w in data.workExperience],
            "projects": [p.model_dump() for p in data.projects],
            "skills": data.skills.model_dump(),
            "certifications": [c.model_dump() for c in data.certifications],
            "volunteer": [v.model_dump() for v in data.volunteer],
            "leadership": [l.model_dump() for l in data.leadership],
        },
        indent=2,
    )


def _extract_json_from_response(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def _parse_tailored_json_from_llm(raw: str) -> dict:
    """Parse the tailored-resume JSON object from Gemini output.

    Handles fenced ```json``` blocks, prose before/after the object, and occasional
    truncation edge cases by taking the substring from the first ``{`` to the last ``}``.
    """
    text = raw.strip()
    candidate = _extract_json_from_response(text)
    try:
        obj = json.loads(candidate)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        chunk = text[start : end + 1]
        try:
            obj = json.loads(chunk)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return valid JSON: {e}") from e

    raise ValueError("LLM did not return valid JSON: could not find a JSON object")


def _build_system_prompt() -> str:
    return """You are an expert resume writer and ATS (Applicant Tracking System) specialist.
Your task is to tailor a candidate's resume for a specific job.

Rules:
1. Select only the most relevant education, work experience, projects, certifications, volunteer, and leadership entries for this job. Omit or reorder to emphasize fit.
2. Rewrite bullet points and descriptions to use keywords from the job description and to highlight impact (metrics, outcomes). Keep each bullet to 1-2 lines.
3. Use strong Harvard style action verbs to begin each bullet point, which fit the context of the bullet, and if any metrics present in original profile make sure to incorporate those..
4. Flatten and order the skills list to put the most relevant skills for the job first. Combine categories into one list.
5. Add a short professionalSummary (2-4 sentences) that positions the candidate for this specific role.
6. Preserve factual accuracy: do not invent companies, dates, or titles. Only rephrase and reorder.
7. Return a single JSON object that exactly matches the required output schema. No markdown, no explanation outside the JSON.

ATS formatting (required):
- Copy phone and location from personalInfo into top-level phone and location when the profile provides them. Do not invent a phone number or location.
- For every startDate, endDate, issueDate, and expiryDate string you output, use one of these forms only: MM/YY, MM/YYYY, abbreviated month + year (e.g. Mar 2019), or full month + year (e.g. March 2019). Use the same style within the resume when possible. For current roles use endDate null with isPresent true (show as Present next to the formatted start date in the data; the template will render the range).
- Keep each work experience entry's own location field (city/region for that role) when present in the source; normalize dates the same way."""


def _build_user_prompt(data: ResumeGeneratorInput) -> str:
    job_ctx = f"Job title: {data.roleName or 'Not specified'}\n"
    if data.companyName:
        job_ctx += f"Company: {data.companyName}\n"
    job_ctx += f"Job description:\n{data.jobDescription}\n"
    selection_rules = ""
    if data.maxProjects is not None:
        selection_rules = f"\nIMPORTANT: Include at most {data.maxProjects} project(s) on the resume. Select the {data.maxProjects} project(s) that are MOST relevant to this job description. Omit all other projects.\n"
    return f"""Candidate profile (JSON):
{_profile_to_context(data)}

---
{job_ctx}
---{selection_rules}
Produce the tailored resume as a single JSON object with these exact keys (all required; use empty arrays [] or null where appropriate):
- name (string, from personalInfo)
- email (string)
- phone (string or null; copy from personalInfo.phone when provided, else null)
- location (string or null; copy from personalInfo.location when provided — city/state or metro for the header, else null)
- portfolioWebsite (string or null)
- githubUrl (string or null)
- linkedinUrl (string or null)
- professionalSummary (string or null, 2-4 sentences for this job)
- education: array of {{ universityName, courseName, courseType, major, gpa?, location?, startDate?, endDate?, isPresent, highlight? }}
- workExperience: array of {{ companyName, position, location?, startDate?, endDate?, isPresent, bullets: string[] }}
- projects: array of {{ projectName, link?, techStack: string[], bullets: string[] }}
- skills: string[] (flattened, most relevant first)
- certifications: array of {{ name, issuingOrganization, issueDate?, expiryDate?, hasNoExpiry, credentialId?, credentialUrl? }}
- volunteer: array of {{ organizationName, role, cause?, location?, startDate?, endDate?, isPresent, bullets: string[] }}
- leadership: array of {{ title, organization, startDate?, endDate?, isPresent, bullets: string[] }}
- extraSections: array of {{ title: string, items: string[] }} (optional)

Return only the JSON object, no other text."""


def parse_tailored_resume(obj: dict) -> TailoredResume:
    def get(key: str, default=None):
        if default is None and key in (
            "education",
            "workExperience",
            "projects",
            "skills",
            "certifications",
            "volunteer",
            "leadership",
            "extraSections",
        ):
            default = []
        return obj.get(key, default) or default

    education = [TailoredEducation(**e) for e in (get("education") or []) if isinstance(e, dict)]
    work = [TailoredWorkExperience(**w) for w in (get("workExperience") or []) if isinstance(w, dict)]
    work = _sort_work_reverse_chrono(work)
    projects = [TailoredProject(**p) for p in (get("projects") or []) if isinstance(p, dict)]
    skills = get("skills")
    if not isinstance(skills, list):
        skills = []
    certs = [TailoredCertification(**c) for c in (get("certifications") or []) if isinstance(c, dict)]
    volunteer = [TailoredVolunteer(**v) for v in (get("volunteer") or []) if isinstance(v, dict)]
    leadership = [TailoredLeadership(**l) for l in (get("leadership") or []) if isinstance(l, dict)]
    extra = [TailoredSection(**s) for s in (get("extraSections") or []) if isinstance(s, dict)]

    return TailoredResume(
        name=str(get("name", "")),
        email=str(get("email", "")),
        phone=get("phone"),
        location=get("location"),
        portfolioWebsite=get("portfolioWebsite"),
        githubUrl=get("githubUrl"),
        linkedinUrl=get("linkedinUrl"),
        professionalSummary=get("professionalSummary"),
        education=education,
        workExperience=work,
        projects=projects,
        skills=skills,
        certifications=certs,
        volunteer=volunteer,
        leadership=leadership,
        extraSections=extra,
    )


def tailor_resume(data: ResumeGeneratorInput, llm_config: Optional[LLMConfig] = None) -> TailoredResume:
    if llm_config is None:
        llm_config = LLMConfig(
            provider=settings.RESUME_LLM_PROVIDER,
            model=settings.RESUME_LLM_MODEL,
            api_key=settings.effective_google_api_key or None,
            max_output_tokens=8192,
            temperature=0.3,
        )
    provider = get_provider(llm_config)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(data)

    last_exc: BaseException | None = None
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            raw = provider.generate(
                user_prompt,
                system_prompt=system_prompt,
                max_tokens=8192,
                temperature=0.3,
            )
            obj = _parse_tailored_json_from_llm(raw)
            return parse_tailored_resume(obj)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_exc = e
            continue

    detail = str(last_exc) if last_exc else "unknown error"
    raise ValueError(
        "Resume tailoring failed after "
        f"{max_attempts} attempts (invalid JSON or resume shape). {detail}"
    ) from last_exc
