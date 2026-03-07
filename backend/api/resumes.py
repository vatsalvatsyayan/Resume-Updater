import base64

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from resume_generation import generate_resume
from resume_generation.schemas.input_schema import ResumeGeneratorInput

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_resumes():
    return {
        "message": "Get all resumes endpoint",
        "resumes": []
    }


# Generate tailored resume + base64 PDF
@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_tailored_resume(body: ResumeGeneratorInput):
    try:
        tailored, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)

        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

        return {
            "tailored_resume": tailored.model_dump(),
            "pdf_base64": pdf_b64
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate only PDF file
@router.post("/generate/pdf", response_class=Response)
async def generate_tailored_resume_pdf(body: ResumeGeneratorInput):
    try:
        _, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume.pdf"
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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