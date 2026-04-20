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
