"""
Output schema for the resume generator.

Structured tailored resume content (after AI selection and rewriting).
Used internally and for PDF rendering.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TailoredEducation(BaseModel):
    """Education entry as it should appear on the resume (possibly reordered/trimmed)."""

    universityName: str
    courseName: str
    courseType: str
    major: str
    gpa: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    highlight: Optional[str] = None


class TailoredWorkExperience(BaseModel):
    """Work experience with tailored bullets."""

    companyName: str
    position: str
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredProject(BaseModel):
    """Project with tailored description/bullets."""

    projectName: str
    link: Optional[str] = None
    techStack: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class TailoredCertification(BaseModel):
    """Certification entry (possibly filtered)."""

    name: str
    issuingOrganization: str
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    hasNoExpiry: bool = False
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None


class TailoredVolunteer(BaseModel):
    """Volunteer entry with optional tailored description."""

    organizationName: str
    role: str
    cause: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredLeadership(BaseModel):
    """Leadership entry with optional tailored description."""

    title: str
    organization: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredSection(BaseModel):
    """Optional section with a title and list of one-line items (e.g. Skills)."""

    title: str
    items: list[str] = Field(default_factory=list)


class TailoredResume(BaseModel):
    """
    Full tailored resume content.

    All lists are already selected and ordered for the target job.
    Bullets and highlights are rewritten to match the job description.
    """

    # Contact / header (from personalInfo, possibly rephrased)
    name: str = ""
    email: str = ""
    portfolioWebsite: Optional[str] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None

    # Optional professional summary (AI-generated for the job)
    professionalSummary: Optional[str] = None

    education: list[TailoredEducation] = Field(default_factory=list)
    workExperience: list[TailoredWorkExperience] = Field(default_factory=list)
    projects: list[TailoredProject] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)  # Flattened, ordered for job
    certifications: list[TailoredCertification] = Field(default_factory=list)
    volunteer: list[TailoredVolunteer] = Field(default_factory=list)
    leadership: list[TailoredLeadership] = Field(default_factory=list)

    # Optional extra sections (e.g. "Relevant coursework")
    extraSections: list[TailoredSection] = Field(default_factory=list)
