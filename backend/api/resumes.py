import base64

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import ValidationError

from resume_generation import generate_resume
from resume_generation.generator import tailored_resume_to_pdf_bytes
from resume_generation.match_score import compute_resume_match_score
from resume_generation.schemas.input_schema import ResumeGeneratorInput
from resume_generation.tailor import parse_tailored_resume

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_resumes():
    return {
        "message": "Get all resumes endpoint",
        "resumes": []
    }


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_tailored_resume(body: ResumeGeneratorInput):
    try:
        tailored, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        match_score = compute_resume_match_score(body.jobDescription, tailored)

        return {
            "tailored_resume": tailored.model_dump(),
            "pdf_base64": pdf_b64,
            "match_score": match_score,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/pdf", response_class=Response)
async def generate_tailored_resume_pdf(body: ResumeGeneratorInput):
    try:
        _, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)

        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=resume.pdf"},
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render/pdf", response_class=Response)
async def render_tailored_resume_pdf(body: dict):
    """Build a PDF from an existing tailored resume JSON (no LLM). Used after editing stored output."""
    raw = body.get("tailoredResume") if isinstance(body, dict) else None
    if raw is None and isinstance(body, dict):
        raw = body.get("tailored_resume")
    if not isinstance(raw, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must include a tailoredResume object",
        )
    try:
        # Same parsing path as POST /resumes/generate after the LLM — avoids schema drift vs model_validate().
        tailored = parse_tailored_resume(raw)
        pdf_bytes = tailored_resume_to_pdf_bytes(tailored)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="resume.pdf"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors(include_url=False),
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{resume_id}", status_code=status.HTTP_200_OK)
async def get_resume(resume_id: str):
    return {
        "message": f"Get resume with ID: {resume_id}",
        "resume": None
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resume(resume_data: dict):
    return {
        "message": "Resume created successfully",
        "resume_id": "example_id"
    }


@router.put("/{resume_id}", status_code=status.HTTP_200_OK)
async def update_resume(resume_id: str, resume_data: dict):
    return {
        "message": f"Resume {resume_id} updated successfully"
    }


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str):
    return None