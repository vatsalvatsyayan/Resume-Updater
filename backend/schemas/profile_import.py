from typing import Literal

from pydantic import BaseModel, Field


CourseType = Literal["Bachelor's", "Master's", "PhD", "Diploma", "Certificate", "Associate", ""]


class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    portfolioWebsite: str | None = None
    githubUrl: str | None = None
    linkedinUrl: str | None = None


class Education(BaseModel):
    universityName: str = ""
    courseName: str = ""
    courseType: CourseType = ""
    major: str = ""
    gpa: str | None = None
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False


class WorkExperience(BaseModel):
    companyName: str = ""
    position: str = ""
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    summary: str | None = None
    description: str | None = None


class Project(BaseModel):
    projectName: str = ""
    link: str | None = None
    techStack: list[str] = Field(default_factory=list)
    summary: str | None = None
    description: str | None = None


class Skills(BaseModel):
    programmingLanguages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    toolsAndTechnologies: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    ai: list[str] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str = ""
    issuingOrganization: str = ""
    issueDate: str | None = None
    expiryDate: str | None = None
    hasNoExpiry: bool = False
    credentialId: str | None = None
    credentialUrl: str | None = None


class Volunteer(BaseModel):
    organizationName: str = ""
    role: str = ""
    cause: str | None = None
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    description: str | None = None


class Leadership(BaseModel):
    title: str = ""
    organization: str = ""
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    description: str | None = None


class ImportedProfileData(BaseModel):
    personalInfo: PersonalInfo = Field(default_factory=PersonalInfo)
    education: list[Education] = Field(default_factory=list)
    workExperience: list[WorkExperience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: list[Certification] = Field(default_factory=list)
    volunteer: list[Volunteer] = Field(default_factory=list)
    leadership: list[Leadership] = Field(default_factory=list)


class ProfileImportResponse(BaseModel):
    message: str
    data: ImportedProfileData
    warnings: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
