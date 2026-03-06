"""
Input schema for the resume generator.

This is the data structure the backend must pass to the resume generation service.
Aligned with the frontend ProfileFormData + job context.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PersonalInfoInput(BaseModel):
    """Personal/contact information."""

    name: str = ""
    email: str = ""
    portfolioWebsite: Optional[str] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None


class EducationInput(BaseModel):
    """Single education entry."""

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
    """Single work experience entry."""

    companyName: str = ""
    position: str = ""
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    summary: Optional[str] = None
    description: Optional[str] = None


class ProjectInput(BaseModel):
    """Single project entry."""

    projectName: str = ""
    link: Optional[str] = None
    techStack: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None


class SkillsInput(BaseModel):
    """Skills grouped by category."""

    programmingLanguages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    toolsAndTechnologies: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    ai: list[str] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)


class CertificationInput(BaseModel):
    """Single certification entry."""

    name: str = ""
    issuingOrganization: str = ""
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    hasNoExpiry: bool = False
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None


class VolunteerInput(BaseModel):
    """Single volunteer entry."""

    organizationName: str = ""
    role: str = ""
    cause: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    description: Optional[str] = None


class LeadershipInput(BaseModel):
    """Single leadership entry."""

    title: str = ""
    organization: str = ""
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    isPresent: bool = False
    description: Optional[str] = None


class ResumeGeneratorInput(BaseModel):
    """
    Full input for resume generation.

    Pass this (as JSON/dict) to the resume generator service.
    """

    # Profile data (same shape as frontend form / backend user profile)
    personalInfo: PersonalInfoInput = Field(default_factory=PersonalInfoInput)
    education: list[EducationInput] = Field(default_factory=list)
    workExperience: list[WorkExperienceInput] = Field(default_factory=list)
    projects: list[ProjectInput] = Field(default_factory=list)
    skills: SkillsInput = Field(default_factory=SkillsInput)
    certifications: list[CertificationInput] = Field(default_factory=list)
    volunteer: list[VolunteerInput] = Field(default_factory=list)
    leadership: list[LeadershipInput] = Field(default_factory=list)

    # Job context (required for tailoring)
    jobDescription: str = Field(
        ...,
        min_length=50,
        description="Full job description text. Used to select and tailor content.",
    )
    roleName: Optional[str] = Field(
        default=None,
        description="Job title/role name (e.g. 'Senior Software Engineer').",
    )
    companyName: Optional[str] = Field(
        default=None,
        description="Company name for this application (optional).",
    )

    # Selection limits (optional): cap how many items to include; LLM picks the best fit
    maxProjects: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="If set, include at most this many projects on the resume. The API will select the most relevant projects for the job.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "personalInfo": {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "portfolioWebsite": "https://jane.dev",
                    "githubUrl": "https://github.com/jane",
                    "linkedinUrl": "https://linkedin.com/in/janedoe",
                },
                "education": [
                    {
                        "universityName": "Example University",
                        "courseName": "B.S. Computer Science",
                        "courseType": "Bachelor's",
                        "major": "Computer Science",
                        "gpa": "3.8",
                        "location": "City, State",
                        "startDate": "2018-09",
                        "endDate": "2022-05",
                        "isPresent": False,
                    }
                ],
                "workExperience": [
                    {
                        "companyName": "Tech Corp",
                        "position": "Software Engineer",
                        "location": "Remote",
                        "startDate": "2022-06",
                        "endDate": None,
                        "isPresent": True,
                        "summary": "Full-stack development",
                        "description": "Built APIs and web apps. Led migration to microservices.",
                    }
                ],
                "projects": [
                    {
                        "projectName": "Open Source Tool",
                        "link": "https://github.com/jane/tool",
                        "techStack": ["Python", "FastAPI", "PostgreSQL"],
                        "summary": "CLI tool for developers",
                        "description": "Designed and shipped a CLI used by 10k+ developers.",
                    }
                ],
                "skills": {
                    "programmingLanguages": ["Python", "JavaScript", "TypeScript"],
                    "frameworks": ["React", "FastAPI", "Django"],
                    "databases": ["PostgreSQL", "MongoDB"],
                    "toolsAndTechnologies": ["Docker", "Git", "CI/CD"],
                    "cloud": ["AWS"],
                    "ai": [],
                    "other": [],
                },
                "certifications": [],
                "volunteer": [],
                "leadership": [],
                "jobDescription": "We are looking for a Senior Software Engineer with 3+ years of experience in Python and React. You will own backend services and collaborate with product. Experience with AWS and distributed systems is a plus.",
                "roleName": "Senior Software Engineer",
                "companyName": "Acme Inc",
            }
        }
