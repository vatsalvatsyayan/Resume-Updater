"""Pydantic schemas for resume generator input and output."""

from .input_schema import (
    ResumeGeneratorInput,
    PersonalInfoInput,
    EducationInput,
    WorkExperienceInput,
    ProjectInput,
    SkillsInput,
    CertificationInput,
    VolunteerInput,
    LeadershipInput,
)
from .output_schema import (
    TailoredResume,
    TailoredSection,
    TailoredEducation,
    TailoredWorkExperience,
    TailoredProject,
    TailoredCertification,
    TailoredVolunteer,
    TailoredLeadership,
)

__all__ = [
    "ResumeGeneratorInput",
    "PersonalInfoInput",
    "EducationInput",
    "WorkExperienceInput",
    "ProjectInput",
    "SkillsInput",
    "CertificationInput",
    "VolunteerInput",
    "LeadershipInput",
    "TailoredResume",
    "TailoredSection",
    "TailoredEducation",
    "TailoredWorkExperience",
    "TailoredProject",
    "TailoredCertification",
    "TailoredVolunteer",
    "TailoredLeadership",
]
