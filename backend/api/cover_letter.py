from fastapi import APIRouter
from schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from services import cover_letter_service

router = APIRouter(prefix="/cover-letter", tags=["Cover Letter"])


@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterRequest) -> CoverLetterResponse:
    """Generate a cover letter for an optimized resume and a target job role.

    Accepts the candidate's full profile (optimized resume as JSON), the job
    description, company name, role name, and an optional tone preference.
    Returns a plain-text cover letter produced by the Gemini LLM.
    """
    cover_letter_text = cover_letter_service.generate_cover_letter(request)
    return CoverLetterResponse(
        cover_letter=cover_letter_text,
        company_name=request.company_name,
        role_name=request.role_name,
    )
