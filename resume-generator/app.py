"""
FastAPI application for the Resume Generator Service.

Run with:
  cd resume-generator && uvicorn app:app --reload --host 0.0.0.0 --port 8001

API docs: http://localhost:8001/docs
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from resume_generator import generate_resume
from resume_generator.schemas import ResumeGeneratorInput

app = FastAPI(
    title="Resume Generator API",
    description="Tailors a resume to a job description using AI and returns structured data + PDF.",
    version="1.0.0",
)


@app.get("/health")
async def health():
    """Health check for load balancers and monitoring."""
    return {"status": "ok", "service": "resume-generator"}


@app.post("/generate")
async def generate(body: ResumeGeneratorInput):
    """
    Generate a tailored resume and PDF from profile + job description.

    Request body: JSON matching ResumeGeneratorInput (see README and /docs).
    Returns: tailored_resume (JSON) and pdf_base64 (string; decode to get PDF bytes).
    """
    try:
        tailored, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        return {
            "tailored_resume": tailored.model_dump(),
            "pdf_base64": pdf_b64,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/pdf", response_class=Response)
async def generate_pdf(body: ResumeGeneratorInput):
    """
    Generate a tailored resume and return only the PDF file.

    Request body: same as POST /generate.
    Response: application/pdf (binary). Use for direct download.
    """
    try:
        tailored, pdf_bytes = generate_resume(body.model_dump(), output_pdf_path=None)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume.pdf",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
