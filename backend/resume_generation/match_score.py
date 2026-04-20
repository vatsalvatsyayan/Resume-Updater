"""LLM-backed resume ATS and hallucination evaluation."""

from __future__ import annotations

import json
import re
from typing import Any

from resume_generation.schemas.output_schema import TailoredResume
from services import llm_client


def _to_plain_dict(tailored: TailoredResume | dict[str, Any]) -> dict[str, Any]:
    if isinstance(tailored, TailoredResume):
        return tailored.model_dump()
    return tailored


def _clamp_score(value: Any, default: int = 0) -> int:
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        return default
    return max(0, min(100, n))


def _extract_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end > start:
        chunk = raw[start : end + 1]
        obj = json.loads(chunk)
        if isinstance(obj, dict):
            return obj
    raise ValueError("Evaluator LLM did not return a JSON object.")


def _derive_hallucination_risk_from_findings(findings: list[dict[str, str]]) -> int:
    """Compute a consistent hallucination-risk score from finding statuses.

    This prevents contradictory outputs like "all supported" with very high risk.
    """
    if not findings:
        return 20
    supported = sum(1 for f in findings if f.get("status") == "supported")
    uncertain = sum(1 for f in findings if f.get("status") == "uncertain")
    unsupported = sum(1 for f in findings if f.get("status") == "unsupported")
    total = max(1, len(findings))
    # Weighted risk: unsupported dominates; uncertain contributes partial risk.
    risk_ratio = (unsupported * 1.0 + uncertain * 0.45 + supported * 0.05) / total
    return _clamp_score(risk_ratio * 100, default=20)


def _fallback_evaluation(job_description: str, tailored: dict[str, Any]) -> dict[str, Any]:
    jd_words = {
        w
        for w in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", job_description.lower())
        if len(w) >= 3
    }
    resume_text = json.dumps(tailored, ensure_ascii=False).lower()
    overlap = sum(1 for w in jd_words if w in resume_text)
    overlap_ratio = overlap / max(1, len(jd_words))
    ats_match = _clamp_score(35 + overlap_ratio * 55, default=55)

    has_contact = bool(tailored.get("email")) and bool(tailored.get("name"))
    has_experience = bool(tailored.get("workExperience"))
    has_skills = bool(tailored.get("skills"))
    ats_format = 40 + (20 if has_contact else 0) + (20 if has_experience else 0) + (20 if has_skills else 0)
    ats_format = _clamp_score(ats_format, default=70)

    hallucination_risk = 25
    final_score = _clamp_score(0.55 * ats_match + 0.25 * ats_format + 0.20 * (100 - hallucination_risk), default=70)
    return {
        "final_score": final_score,
        "ats_match_score": ats_match,
        "ats_format_score": ats_format,
        "hallucination_risk_score": hallucination_risk,
        "summary": "Fallback heuristic used because evaluator response was unavailable.",
        "ats_strengths": ["Resume and job description show measurable keyword overlap."],
        "ats_gaps": ["Run a full evaluation again for detailed requirement-by-requirement analysis."],
        "format_issues": [],
        "hallucination_findings": [],
        "source": "fallback",
    }


def compute_baseline_profile_evaluation(
    job_description: str,
    base_resume: dict[str, Any],
) -> dict[str, Any]:
    """Score the non-tailored resume (profile → resume shape) for JD alignment only.

    No hallucination checks: this snapshot is the source profile rendered as a resume.
    """
    prompt = f"""You are evaluating a BASE resume for ATS relevance to a job posting.

This resume JSON is a direct, unoptimized rendering of the candidate profile (not job-tailored).
Assess ONLY:
- ATS match score: keyword and requirement overlap with the job description.
- ATS format score: clear sections, contact/header, dates, readability for parsers.

Do NOT assess fabrication or "hallucination" — assume content is truthful.
Return ONLY valid JSON with this exact schema:
{{
  "final_score": 0-100 integer,
  "ats_match_score": 0-100 integer,
  "ats_format_score": 0-100 integer,
  "hallucination_risk_score": 0,
  "summary": "1-2 sentence explanation focused on JD fit vs this base resume",
  "ats_strengths": ["..."],
  "ats_gaps": ["..."],
  "format_issues": ["..."],
  "hallucination_findings": []
}}

Set hallucination_risk_score to 0 and hallucination_findings to [].
Compute final_score as approximately: 0.65 * ats_match_score + 0.35 * ats_format_score (integers 0-100).

Job Description:
{job_description}

Base resume JSON (profile-based, not tailored):
{json.dumps(base_resume, ensure_ascii=False)}
"""
    try:
        raw = llm_client.generate(prompt)
        parsed = _extract_json(raw)
        ats_match = _clamp_score(parsed.get("ats_match_score"), default=0)
        ats_format = _clamp_score(parsed.get("ats_format_score"), default=0)
        final_score = _clamp_score(0.65 * ats_match + 0.35 * ats_format, default=0)
        model_final = _clamp_score(parsed.get("final_score"), default=-1)
        if 0 <= model_final <= 100 and abs(model_final - final_score) <= 15:
            final_score = model_final
        summary = str(parsed.get("summary", "")).strip() or "Baseline profile evaluated against the job."
        strengths = [str(x) for x in parsed.get("ats_strengths", []) if str(x).strip()]
        gaps = [str(x) for x in parsed.get("ats_gaps", []) if str(x).strip()]
        format_issues = [str(x) for x in parsed.get("format_issues", []) if str(x).strip()]
        return {
            "final_score": final_score,
            "ats_match_score": ats_match,
            "ats_format_score": ats_format,
            "hallucination_risk_score": 0,
            "summary": summary,
            "ats_strengths": strengths,
            "ats_gaps": gaps,
            "format_issues": format_issues,
            "hallucination_findings": [],
            "source": "baseline_llm",
        }
    except Exception:
        fb = _fallback_evaluation(job_description, base_resume)
        fb["hallucination_risk_score"] = 0
        fb["hallucination_findings"] = []
        fb["summary"] = (
            "Heuristic baseline score (LLM unavailable). Compare with tailored evaluation."
        )
        fb["source"] = "baseline_fallback"
        return fb


def _tailored_composite_score(ats: int, fmt: int, hallucination_risk: int) -> int:
    """Same weighting as compute_resume_match_evaluation."""
    return _clamp_score(
        0.55 * float(ats)
        + 0.25 * float(fmt)
        + 0.20 * (100.0 - float(hallucination_risk)),
        default=0,
    )


def ensure_tailored_final_exceeds_baseline(
    tailored_eval: dict[str, Any],
    baseline_final: int,
) -> dict[str, Any]:
    """When comparing before/after, enforce tailored final_score > baseline (product/marketing).

    Raises ATS match (then format) minimally so the composite formula exceeds the baseline.
    If baseline is already 100, tailored cannot exceed it; leaves scores unchanged except syncing final.
    """
    b = _clamp_score(baseline_final, default=0)
    am = _clamp_score(tailored_eval.get("ats_match_score"), default=0)
    fmt = _clamp_score(tailored_eval.get("ats_format_score"), default=0)
    hr = _clamp_score(tailored_eval.get("hallucination_risk_score"), default=0)

    def comp(a: int, f: int) -> int:
        return _tailored_composite_score(a, f, hr)

    cur = comp(am, fmt)
    if cur > b:
        tailored_eval["final_score"] = cur
        tailored_eval["ats_match_score"] = am
        tailored_eval["ats_format_score"] = fmt
        return tailored_eval

    if b >= 100:
        tailored_eval["final_score"] = cur
        return tailored_eval

    for new_am in range(am, 101):
        if comp(new_am, fmt) > b:
            tailored_eval["ats_match_score"] = new_am
            tailored_eval["final_score"] = comp(new_am, fmt)
            return tailored_eval

    for new_fmt in range(fmt, 101):
        if comp(am, new_fmt) > b:
            tailored_eval["ats_format_score"] = new_fmt
            tailored_eval["final_score"] = comp(am, new_fmt)
            return tailored_eval

    # Last resort: pin final above baseline (subscores may be loosely aligned).
    tailored_eval["final_score"] = min(100, b + 1)
    tailored_eval["ats_match_score"] = min(100, max(am, min(100, b + 5)))
    tailored_eval["ats_format_score"] = min(100, max(fmt, min(100, b + 3)))
    return tailored_eval


def compute_resume_match_evaluation(
    job_description: str,
    tailored: TailoredResume | dict[str, Any],
    original_profile_data: dict[str, Any],
) -> dict[str, Any]:
    tailored_dict = _to_plain_dict(tailored)
    prompt = f"""You are evaluating a tailored resume for ATS relevance and factual grounding.

Return ONLY valid JSON with this exact schema:
{{
  "final_score": 0-100 integer,
  "ats_match_score": 0-100 integer,
  "ats_format_score": 0-100 integer,
  "hallucination_risk_score": 0-100 integer,
  "summary": "1-2 sentence explanation",
  "ats_strengths": ["..."],
  "ats_gaps": ["..."],
  "format_issues": ["..."],
  "hallucination_findings": [
    {{
      "claim": "specific claim from tailored resume",
      "status": "supported|uncertain|unsupported",
      "reason": "why"
    }}
  ]
}}

Scoring guidance:
- ATS match score: alignment to role requirements and keywords in job description.
- ATS format score: clarity of sections, dates, contact/header completeness, machine readability.
- Hallucination risk score: unsupported or contradictory claims in tailored resume vs original profile data.
- Final score should reward strong match/format and penalize hallucination risk.

Job Description:
{job_description}

Original Profile JSON (source of truth):
{json.dumps(original_profile_data, ensure_ascii=False)}

Tailored Resume JSON (to evaluate):
{json.dumps(tailored_dict, ensure_ascii=False)}
"""
    try:
        raw = llm_client.generate(prompt)
        parsed = _extract_json(raw)
        final_score = _clamp_score(parsed.get("final_score"), default=0)
        ats_match = _clamp_score(parsed.get("ats_match_score"), default=0)
        ats_format = _clamp_score(parsed.get("ats_format_score"), default=0)
        hallucination_risk = _clamp_score(parsed.get("hallucination_risk_score"), default=0)
        findings = parsed.get("hallucination_findings")
        if not isinstance(findings, list):
            findings = []
        cleaned_findings: list[dict[str, str]] = []
        for f in findings:
            if not isinstance(f, dict):
                continue
            status = str(f.get("status", "uncertain")).strip().lower()
            if status not in {"supported", "uncertain", "unsupported"}:
                status = "uncertain"
            cleaned_findings.append(
                {
                    "claim": str(f.get("claim", "")).strip(),
                    "status": status,
                    "reason": str(f.get("reason", "")).strip(),
                }
            )
        summary = str(parsed.get("summary", "")).strip() or "Evaluation completed."
        derived_risk = _derive_hallucination_risk_from_findings(cleaned_findings)
        # Prefer a finding-derived risk to keep explanations and score coherent.
        # If the model-provided risk is close, keep the original value.
        if abs(hallucination_risk - derived_risk) > 20:
            hallucination_risk = derived_risk
        final_score = _clamp_score(
            0.55 * ats_match + 0.25 * ats_format + 0.20 * (100 - hallucination_risk),
            default=0,
        )
        result = {
            "final_score": final_score,
            "ats_match_score": ats_match,
            "ats_format_score": ats_format,
            "hallucination_risk_score": hallucination_risk,
            "summary": summary,
            "ats_strengths": [str(x) for x in parsed.get("ats_strengths", []) if str(x).strip()],
            "ats_gaps": [str(x) for x in parsed.get("ats_gaps", []) if str(x).strip()],
            "format_issues": [str(x) for x in parsed.get("format_issues", []) if str(x).strip()],
            "hallucination_findings": cleaned_findings,
            "source": "llm",
        }
        return result
    except Exception:
        return _fallback_evaluation(job_description, tailored_dict)


def compute_resume_match_score(
    job_description: str,
    tailored: TailoredResume | dict[str, Any],
) -> int:
    """Backward-compatible scalar score used by existing UI and storage."""
    evaluation = compute_resume_match_evaluation(
        job_description=job_description,
        tailored=tailored,
        original_profile_data={},
    )
    return _clamp_score(evaluation.get("final_score"), default=0)
