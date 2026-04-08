from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TailoredEducation(BaseModel):
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
    companyName: str
    position: str
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredProject(BaseModel):
    projectName: str
    link: Optional[str] = None
    techStack: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class TailoredCertification(BaseModel):
    name: str
    issuingOrganization: str
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    hasNoExpiry: bool = False
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None


class TailoredVolunteer(BaseModel):
    organizationName: str
    role: str
    cause: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredLeadership(BaseModel):
    title: str
    organization: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    bullets: list[str] = Field(default_factory=list)


class TailoredSection(BaseModel):
    title: str
    items: list[str] = Field(default_factory=list)


class TailoredResume(BaseModel):
    name: str = ""
    email: str = ""
    portfolioWebsite: Optional[str] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None
    professionalSummary: Optional[str] = None
    education: list[TailoredEducation] = Field(default_factory=list)
    workExperience: list[TailoredWorkExperience] = Field(default_factory=list)
    projects: list[TailoredProject] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[TailoredCertification] = Field(default_factory=list)
    volunteer: list[TailoredVolunteer] = Field(default_factory=list)
    leadership: list[TailoredLeadership] = Field(default_factory=list)
    extraSections: list[TailoredSection] = Field(default_factory=list)
