import base64

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import ValidationError

from resume_generation import generate_resume
from resume_generation.generator import (
    input_to_tailored_no_llm,
    resume_input_from_profile_dict,
    tailored_resume_to_pdf_bytes,
)
from resume_generation.match_score import (
    compute_baseline_profile_evaluation,
    compute_resume_match_evaluation,
    ensure_tailored_final_exceeds_baseline,
)
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

        return {
            "tailored_resume": tailored.model_dump(),
            "pdf_base64": pdf_b64,
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


@router.post("/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_tailored_resume(body: dict):
    """Evaluate tailored resume ATS quality + hallucination risk as a separate on-demand LLM call."""
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be a JSON object",
        )

    job_description = body.get("jobDescription") or body.get("job_description")
    tailored_raw = body.get("tailoredResume") or body.get("tailored_resume")
    original_profile = body.get("originalProfile") or body.get("original_profile") or {}

    if not isinstance(job_description, str) or len(job_description.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jobDescription must be a non-empty string (min 20 chars)",
        )
    if not isinstance(tailored_raw, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tailoredResume must be a JSON object",
        )
    if not isinstance(original_profile, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="originalProfile must be a JSON object",
        )

    try:
        tailored = parse_tailored_resume(tailored_raw)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors(include_url=False),
        ) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    try:
        evaluation = compute_resume_match_evaluation(
            job_description=job_description.strip(),
            tailored=tailored,
            original_profile_data=original_profile,
        )
        tailored_final = int(evaluation.get("final_score", 0))

        raw_ib = body.get("includeBaseline")
        if raw_ib is None:
            raw_ib = body.get("include_baseline")
        if isinstance(raw_ib, bool):
            include_baseline = raw_ib
        elif isinstance(raw_ib, str):
            include_baseline = raw_ib.strip().lower() in ("true", "1", "yes")
        elif raw_ib is None:
            include_baseline = False
        else:
            include_baseline = bool(raw_ib)

        baseline_evaluation: dict | None = None
        baseline_final: int | None = None
        score_delta: int | None = None
        if include_baseline and isinstance(original_profile, dict) and original_profile:
            try:
                resume_input = resume_input_from_profile_dict(original_profile)
                base_resume_model = input_to_tailored_no_llm(resume_input)
                baseline_evaluation = compute_baseline_profile_evaluation(
                    job_description.strip(),
                    base_resume_model.model_dump(),
                )
                baseline_final = int(baseline_evaluation.get("final_score", 0))
                evaluation = ensure_tailored_final_exceeds_baseline(
                    evaluation,
                    baseline_final,
                )
                tailored_final = int(evaluation.get("final_score", 0))
                score_delta = tailored_final - baseline_final
            except Exception:
                baseline_evaluation = None
                baseline_final = None
                score_delta = None

        out: dict = {
            "match_score": tailored_final,
            "match_evaluation": evaluation,
            "baseline_match_score": baseline_final,
            "baseline_match_evaluation": baseline_evaluation,
            "score_delta": score_delta,
            "include_baseline": include_baseline,
        }
        return out
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


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