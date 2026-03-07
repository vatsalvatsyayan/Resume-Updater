from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PersonalInfoInput(BaseModel):
    name: str = ""
    email: str = ""
    portfolioWebsite: Optional[str] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None


class EducationInput(BaseModel):
    universityName: str = ""
    courseName: str = ""
    courseType: str = ""
    major: str = ""
    gpa: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False


class WorkExperienceInput(BaseModel):
    companyName: str = ""
    position: str = ""
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    summary: Optional[str] = None
    description: Optional[str] = None


class ProjectInput(BaseModel):
    projectName: str = ""
    link: Optional[str] = None
    techStack: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None


class SkillsInput(BaseModel):
    programmingLanguages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    toolsAndTechnologies: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    ai: list[str] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)


class CertificationInput(BaseModel):
    name: str = ""
    issuingOrganization: str = ""
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    hasNoExpiry: bool = False
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None


class VolunteerInput(BaseModel):
    organizationName: str = ""
    role: str = ""
    cause: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    description: Optional[str] = None


class LeadershipInput(BaseModel):
    title: str = ""
    organization: str = ""
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    description: Optional[str] = None


class ResumeGeneratorInput(BaseModel):
    personalInfo: PersonalInfoInput = Field(default_factory=PersonalInfoInput)
    education: list[EducationInput] = Field(default_factory=list)
    workExperience: list[WorkExperienceInput] = Field(default_factory=list)
    projects: list[ProjectInput] = Field(default_factory=list)
    skills: SkillsInput = Field(default_factory=SkillsInput)
    certifications: list[CertificationInput] = Field(default_factory=list)
    volunteer: list[VolunteerInput] = Field(default_factory=list)
    leadership: list[LeadershipInput] = Field(default_factory=list)
    jobDescription: str = Field(..., min_length=50)
    roleName: Optional[str] = None
    companyName: Optional[str] = None
    maxProjects: Optional[int] = Field(default=None, ge=1, le=20)
