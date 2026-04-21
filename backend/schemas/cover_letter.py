from typing import Literal

from pydantic import BaseModel, Field


class CoverLetterRequest(BaseModel):
    profile_data: dict = Field(
        ...,
        description="The full optimized resume profile as a JSON object (matches ProfileFormData shape)"
    )
    job_description: str = Field(..., min_length=20, description="Full text of the job description")
    company_name: str = Field(..., min_length=1, description="Name of the target company")
    role_name: str = Field(..., min_length=1, description="Title of the role being applied to")
    tone: Literal["professional", "enthusiastic", "concise"] = Field(
        default="professional",
        description="Desired tone of the cover letter"
    )
    existing_cover_letter: str | None = Field(
        default=None,
        description="If set, the PDF endpoint renders this text instead of calling the LLM again.",
    )


class CoverLetterResponse(BaseModel):
    cover_letter: str = Field(..., description="The generated plain-text cover letter")
    company_name: str
    role_name: str
