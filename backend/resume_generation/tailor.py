from __future__ import annotations

import json
import re
from typing import Optional

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


def _build_system_prompt() -> str:
    return """You are an expert resume writer and ATS (Applicant Tracking System) specialist.
Your task is to tailor a candidate's resume for a specific job.

Rules:
1. Select only the most relevant education, work experience, projects, certifications, volunteer, and leadership entries for this job. Omit or reorder to emphasize fit.
2. Rewrite bullet points and descriptions to use keywords from the job description and to highlight impact (metrics, outcomes). Keep each bullet to 1-2 lines.
3. Flatten and order the skills list to put the most relevant skills for the job first. Combine categories into one list.
4. Add a short professionalSummary (2-4 sentences) that positions the candidate for this specific role.
5. Preserve factual accuracy: do not invent companies, dates, or titles. Only rephrase and reorder.
6. Return a single JSON object that exactly matches the required output schema. No markdown, no explanation outside the JSON."""


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


def _parse_tailored_resume(obj: dict) -> TailoredResume:
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
            provider="gemini",
            model="gemini-2.5-flash",
            max_output_tokens=8192,
            temperature=0.3,
        )
    provider = get_provider(llm_config)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(data)
    raw = provider.generate(
        user_prompt,
        system_prompt=system_prompt,
        max_tokens=8192,
        temperature=0.3,
    )
    json_str = _extract_json_from_response(raw)
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}") from e
    return _parse_tailored_resume(obj)
