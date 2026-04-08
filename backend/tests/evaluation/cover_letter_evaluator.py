"""LLM-as-a-judge evaluator for generated cover letters.

Purpose: offline quality measurement of the cover letter service at scale.
Run this via the --evaluate flag in tests/test_cover_letter.py, NOT as part
of the production API flow.

Each of the 8 constraints defined in the cover letter prompt is evaluated by a
dedicated Gemini call. Each call returns 1 (constraint followed) or 0
(constraint violated). Final accuracy = total_score / 8.

Usage (from backend/ with venv activated):
    python -m tests.test_cover_letter --evaluate
    python -m tests.test_cover_letter job1 --evaluate
"""

import sys
from pathlib import Path

# Allow imports from backend/ root when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from services import llm_client

# ---------------------------------------------------------------------------
# Constraint definitions
# Each entry maps constraint_key → evaluation question sent to Gemini
# ---------------------------------------------------------------------------
CONSTRAINTS: dict[str, str] = {
    "tone": (
        "Does the cover letter use a clear, professional and conversational tone? "
    ),
    "paragraph_count": (
        "Does the cover letter contain strictly 4 or fewer paragraphs? "
        "Count only full paragraphs separated by blank lines; "
        "a short closing line does not count as a paragraph."
    ),
    "focus": (
        "Does the cover letter focus on the value the candidate brings to the employer "
        "rather than simply listing past jobs? It should answer 'why should they care about my skills?' "
        "with context and relevance to the role."
    ),
    "honesty": (
        "If any requirement mentioned in the job description is clearly absent from the candidate's resume, "
        "does the cover letter either omit it or frame it honestly as a growth opportunity "
        "(e.g., 'While I am newer to X, I have been building it through Y')? "
        "It must NOT claim the candidate has skills they demonstrably lack based on the resume provided."
    ),
    "no_invented_facts": (
        "Does the cover letter avoid inventing facts, credentials, projects, or experiences "
        "that are not present in the candidate resume provided? "
        "Every specific claim must be traceable to the resume or company research."
    ),
    "plain_text": (
        "Is the cover letter written in plain text only, with no markdown formatting, "
        "no bullet points, no numbered lists, and no section headers?"
    ),
}


def _evaluate_constraint(
    constraint_question: str,
    cover_letter: str,
    resume_summary: str,
    job_description: str,
    candidate_name: str,
) -> int:
    """Make one Gemini call to evaluate a single constraint.

    Returns 1 if the constraint is followed, 0 otherwise.
    Defaults to 0 on any unexpected response or API error.
    """
    prompt = f"""You are a strict evaluator assessing whether a cover letter follows a specific writing constraint.

## Constraint to Evaluate
{constraint_question}

## Candidate Name (for reference)
{candidate_name}

## Candidate Resume Summary (for reference)
{resume_summary}

## Job Description (for reference)
{job_description}

## Cover Letter Under Evaluation
{cover_letter}

## Your Task
Determine whether the cover letter follows the constraint above.

Reply with ONLY a single digit:
- "1" if the constraint IS followed
- "0" if the constraint is NOT followed

Do not explain. Do not add any other text. Output only "1" or "0".
"""
    try:
        result = llm_client.generate(prompt).strip()
        return 1 if result == "1" else 0
    except Exception:
        return 0


def evaluate(
    cover_letter: str,
    job_description: str,
    resume_summary: str,
    candidate_name: str,
) -> dict:
    """Run all 8 constraint evaluations and return a structured result.

    Makes 8 sequential Gemini calls — one per constraint.

    Returns:
        {
            "scores":      {constraint_key: 0 or 1, ...},
            "total_score": int (0–8),
            "accuracy":    float (0.0–1.0),
        }
    """
    scores: dict[str, int] = {}

    for key, question in CONSTRAINTS.items():
        score = _evaluate_constraint(
            constraint_question=question,
            cover_letter=cover_letter,
            resume_summary=resume_summary,
            job_description=job_description,
            candidate_name=candidate_name,
        )
        scores[key] = score
        status = "PASS" if score == 1 else "FAIL"
        print(f"    [{status}] {key}")

    total_score = sum(scores.values())
    accuracy = round(total_score / len(CONSTRAINTS), 2)

    return {
        "scores": scores,
        "total_score": total_score,
        "accuracy": accuracy,
    }
