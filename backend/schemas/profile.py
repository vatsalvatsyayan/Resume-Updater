# # app/schemas/profile.py
# from __future__ import annotations
# from typing import List, Optional
# from pydantic import BaseModel, Field

# def to_camel(string: str) -> str:
#     parts = string.split('_')
#     return parts[0] + ''.join(p.title() for p in parts[1:])

# class CamelModel(BaseModel):
#     class Config:
#         alias_generator = to_camel
#         allow_population_by_field_name = True
#         populate_by_name = True 


# class PersonalInfo(CamelModel):
#     full_name: Optional[str] = Field(None, alias="name")
#     email: Optional[str] = None
#     portfolio: Optional[str] = Field(None, alias="portfolioWebsite")
#     linkedin: Optional[str] = Field(None, alias="linkedinUrl")


# class EducationEntry(CamelModel):
#     id: Optional[str] = None
#     school: Optional[str] = Field(None, alias="universityName")
#     degree: Optional[str] = Field(None, alias="Degree/Course Name")
#     degree_type: Optional[str] = Field(None, alias="Type of Degree")
#     major: Optional[str] = None
#     gpa: Optional[str] = None
#     location: Optional[str] = None
#     start_date: Optional[str] = Field(None, alias="startDate")
#     end_date: Optional[str] = Field(None, alias="endDate")
#     currently_enrolled: Optional[bool] = Field(False, alias="isPresent")


# class WorkEntry(CamelModel):
#     id: Optional[str] = None
#     company: Optional[str] = Field(None, alias="companyName")
#     title: Optional[str] = Field(None, alias="position")
#     location: Optional[str] = None
#     start_date: Optional[str] = Field(None, alias="startDate")
#     end_date: Optional[str] = Field(None, alias="endDate")
#     currently_working: Optional[bool] = Field(False, alias="isPresent")
#     summary: Optional[str] = None
#     description: Optional[str] = None

# class ProjectEntry(CamelModel):
#     id: Optional[str] = None
#     name: Optional[str] = Field(None, alias="projectName")
#     link: Optional[str] = None
#     tech_stack: List[str] = Field(default_factory=list, alias="techStack")
#     summary: Optional[str] = None
#     description: Optional[str] = None

# class Skills(BaseModel):
#     programmingLanguages: List[str] = Field(default_factory=list, alias="programmingLanguages")
#     frameworks: List[str] = Field(default_factory=list, alias="frameworks")
#     databases: List[str] = Field(default_factory=list, alias="databases")
#     tools: List[str] = Field(default_factory=list, alias="toolsAndTechnologies")
#     cloud: List[str] = Field(default_factory=list, alias="cloud")
#     ai_ml: List[str] = Field(default_factory=list, alias="ai")   # frontend uses 'ai'
#     other: List[str] = Field(default_factory=list, alias="other")

# class Certification(CamelModel):
#     id: Optional[str] = None 
#     name: str
#     organization: str
#     issue_date: Optional[str] = None
#     expiry_date: Optional[str] = None
#     no_expiry: Optional[bool] = False
#     credential_id: Optional[str] = None
#     credential_url: Optional[str] = None


# class VolunteerEntry(CamelModel):
#     id: Optional[str] = None 
#     organization: str
#     role: str
#     cause: Optional[str] = None
#     location: Optional[str] = None
#     start_date: Optional[str] = None
#     end_date: Optional[str] = None
#     currently_volunteering: Optional[bool] = False
#     description: Optional[str] = None


# class LeadershipEntry(CamelModel):
#     id: Optional[str] = None
#     title: str
#     organization: str
#     start_date: Optional[str] = None
#     end_date: Optional[str] = None
#     current_position: Optional[bool] = False
#     description: Optional[str] = None


# class ResumeProfile(BaseModel):
#     personal_info: PersonalInfo
#     user_id: Optional[str] = None
#     email: Optional[str] = None
#     personal_info: PersonalInfo
#     education: List[EducationEntry] = Field(default_factory=list)
#     work_experience: List[WorkEntry] = Field(default_factory=list)
#     projects: List[ProjectEntry] = Field(default_factory=list)
#     skills: Skills = Field(default_factory=Skills)
#     certifications: List = Field(default_factory=list)
#     volunteer: List = Field(default_factory=list, alias="volunteer")
#     leadership_experience: List = Field(default_factory=list, alias="leadership")
#     created_at: Optional[str] = None
#     updated_at: Optional[str] = None

# app/schemas/profile.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])

class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        populate_by_name = True 
        # If you want, you can also set `allow_population_by_field_name = True`
        # so you can construct models either by snake_case fields or alias names.


class PersonalInfo(CamelModel):
    # frontend sends personalInfo: { name, email, portfolioWebsite, githubUrl, linkedinUrl }
    full_name: Optional[str] = Field(None, alias="name")
    email: Optional[str] = None
    portfolio: Optional[str] = Field(None, alias="portfolioWebsite")
    github: Optional[str] = Field(None, alias="githubUrl")
    linkedin: Optional[str] = Field(None, alias="linkedinUrl")


class EducationEntry(CamelModel):
    # frontend education objects use:
    # { id, universityName, courseName, courseType, major, gpa, location, startDate, endDate, isPresent }
    id: Optional[str] = None
    school: Optional[str] = Field(None, alias="universityName")
    degree: Optional[str] = Field(None, alias="courseName")
    degree_type: Optional[str] = Field(None, alias="courseType")
    major: Optional[str] = None
    gpa: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    currently_enrolled: Optional[bool] = Field(False, alias="isPresent")


class WorkEntry(CamelModel):
    # frontend workExperience entries use:
    # { id?, companyName, position, location, startDate, endDate, isPresent, summary, description }
    id: Optional[str] = None
    company: Optional[str] = Field(None, alias="companyName")
    title: Optional[str] = Field(None, alias="position")
    location: Optional[str] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    currently_working: Optional[bool] = Field(False, alias="isPresent")
    summary: Optional[str] = None
    description: Optional[str] = None


class ProjectEntry(CamelModel):
    # frontend project entries:
    # { id, projectName, link, techStack, summary, description }
    id: Optional[str] = None
    name: Optional[str] = Field(None, alias="projectName")
    link: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list, alias="techStack")
    summary: Optional[str] = None
    description: Optional[str] = None


class Skills(CamelModel):
    # frontend skills object uses keys:
    # programmingLanguages, frameworks, databases, toolsAndTechnologies, cloud, ai, other
    programming_languages: List[str] = Field(default_factory=list, alias="programmingLanguages")
    frameworks: List[str] = Field(default_factory=list, alias="frameworks")
    databases: List[str] = Field(default_factory=list, alias="databases")
    tools: List[str] = Field(default_factory=list, alias="toolsAndTechnologies")
    cloud: List[str] = Field(default_factory=list, alias="cloud")
    ai_ml: List[str] = Field(default_factory=list, alias="ai")
    other: List[str] = Field(default_factory=list, alias="other")


class Certification(CamelModel):
    # your screenshots showed certification fields in snake_case:
    # { name, issuing_organization, issue_date, expiry_date, has_no_expiry, credential_id, credential_url }
    id: Optional[str] = None
    name: Optional[str] = None
    issuing_organization: Optional[str] = Field(None, alias="issuing_organization")
    issue_date: Optional[str] = Field(None, alias="issue_date")
    expiry_date: Optional[str] = Field(None, alias="expiry_date")
    has_no_expiry: Optional[bool] = Field(False, alias="has_no_expiry")
    credential_id: Optional[str] = Field(None, alias="credential_id")
    credential_url: Optional[str] = Field(None, alias="credential_url")


class VolunteerEntry(CamelModel):
    # align with frontend payload names where possible:
    # { id?, organizationName, role, cause, location, startDate, endDate, isPresent, description }
    id: Optional[str] = None
    organization: Optional[str] = Field(None, alias="organizationName")
    role: Optional[str] = None
    cause: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    currently_volunteering: Optional[bool] = Field(False, alias="isPresent")
    description: Optional[str] = None


class LeadershipEntry(CamelModel):
    # frontend leadership entries likely use:
    # { id?, title, organization, startDate, endDate, isPresent, description }
    id: Optional[str] = None
    title: Optional[str] = None
    organization: Optional[str] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    current_position: Optional[bool] = Field(False, alias="isPresent")
    description: Optional[str] = None


class ResumeProfile(CamelModel):
    # top-level keys in frontend payload:
    # personalInfo, education, workExperience, projects, skills, certifications,
    # volunteer, leadership, email, updated_at, created_at, user_id
    personal_info: PersonalInfo = Field(..., alias="personalInfo")
    email: Optional[str] = None
    user_id: Optional[str] = Field(None, alias="user_id")
    created_at: Optional[str] = Field(None, alias="created_at")
    updated_at: Optional[str] = Field(None, alias="updated_at")

    education: List[EducationEntry] = Field(default_factory=list, alias="education")
    work_experience: List[WorkEntry] = Field(default_factory=list, alias="workExperience")
    projects: List[ProjectEntry] = Field(default_factory=list, alias="projects")
    skills: Skills = Field(default_factory=Skills, alias="skills")
    certifications: List[Certification] = Field(default_factory=list, alias="certifications")
    volunteer: List[VolunteerEntry] = Field(default_factory=list, alias="volunteer")
    leadership_experience: List[LeadershipEntry] = Field(default_factory=list, alias="leadership")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True