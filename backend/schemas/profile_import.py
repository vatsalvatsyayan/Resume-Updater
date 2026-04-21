from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator

from utils.date_import import coerce_date_scalar


CourseType = Literal["Bachelor's", "Master's", "PhD", "Diploma", "Certificate", "Associate", ""]


class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str | None = Field(
        None,
        validation_alias=AliasChoices(
            "phone",
            "phone_number",
            "phoneNumber",
            "mobile",
            "tel",
            "telephone",
        ),
    )
    location: str | None = Field(
        None,
        validation_alias=AliasChoices(
            "location",
            "city",
            "city_state",
            "cityState",
            "mailing_address",
            "mailingAddress",
            "address",
        ),
    )
    portfolioWebsite: str | None = None
    githubUrl: str | None = None
    linkedinUrl: str | None = None

    @field_validator("phone", "location", mode="before")
    @classmethod
    def strip_optional_text(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None


class Education(BaseModel):
    universityName: str = Field(
        "",
        validation_alias=AliasChoices("universityName", "university_name", "school", "institution"),
    )
    courseName: str = Field(
        "",
        validation_alias=AliasChoices("courseName", "course_name", "degree", "program"),
    )
    courseType: CourseType = ""
    major: str = ""
    gpa: str | None = Field(
        None,
        validation_alias=AliasChoices(
            "gpa",
            "GPA",
            "grade_point_average",
            "gradePointAverage",
            "cgpa",
            "CGPA",
        ),
    )
    location: str | None = Field(
        None,
        validation_alias=AliasChoices(
            "location",
            "campus",
            "school_location",
            "schoolLocation",
            "university_location",
            "universityLocation",
        ),
    )
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False

    @field_validator("gpa", mode="before")
    @classmethod
    def coerce_gpa_to_string(cls, v: object) -> str | None:
        """LLMs often return GPA as a number; the app stores GPA as a string."""
        if v is None:
            return None
        if isinstance(v, bool):
            return None
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            s = v.strip()
            return s or None
        return str(v)

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def coerce_education_dates(cls, v: object) -> str | None:
        return coerce_date_scalar(v)


class WorkExperience(BaseModel):
    companyName: str = ""
    position: str = ""
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    summary: str | None = None
    description: str | None = None

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def coerce_work_dates(cls, v: object) -> str | None:
        return coerce_date_scalar(v)


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

    @field_validator("issueDate", "expiryDate", mode="before")
    @classmethod
    def coerce_cert_dates(cls, v: object) -> str | None:
        return coerce_date_scalar(v)


class Volunteer(BaseModel):
    organizationName: str = ""
    role: str = ""
    cause: str | None = None
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    description: str | None = None

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def coerce_volunteer_dates(cls, v: object) -> str | None:
        return coerce_date_scalar(v)


class Leadership(BaseModel):
    title: str = ""
    organization: str = ""
    startDate: str | None = None
    endDate: str | None = None
    isPresent: bool = False
    description: str | None = None

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def coerce_leadership_dates(cls, v: object) -> str | None:
        return coerce_date_scalar(v)


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
