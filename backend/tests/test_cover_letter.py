"""
Manual integration test for the cover letter generation service.

Usage (from the backend/ directory, with venv activated):

  Generate cover letters for all jobs:
    python -m tests.test_cover_letter

  Generate for a specific job only:
    python -m tests.test_cover_letter job1

  Generate + evaluate quality (LLM-as-a-judge, 8 Gemini calls per job):
    python -m tests.test_cover_letter --evaluate
    python -m tests.test_cover_letter job1 --evaluate

Each job directory under tests/test-data/ must contain:
    - optimized_resume.json   (optimized resume in the expected schema)
    - job_description.txt     (raw job description text)

Requires GEMINI_API_KEY to be set in backend/.env
"""

import json
import sys
from pathlib import Path

# Allow imports from the backend/ root (schemas, services, core)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas.cover_letter import CoverLetterRequest
from services import cover_letter_service
from services.cover_letter_service import _extract_profile_summary

FIXTURES_DIR = Path(__file__).parent / "test-data"
OUTPUT_DIR = Path(__file__).parent / "output"


def load_fixture(job_dir: Path) -> CoverLetterRequest | None:
    resume_path = job_dir / "optimized_resume.json"
    jd_path = job_dir / "job_description.txt"

    if not resume_path.exists() or not jd_path.exists():
        print(f"  [SKIP] Missing optimized_resume.json or job_description.txt in {job_dir.name}")
        return None

    with open(resume_path, encoding="utf-8") as f:
        profile_data = json.load(f)

    with open(jd_path, encoding="utf-8") as f:
        job_description = f.read().strip()

    # Skip directories that still have placeholder content
    if "_comment" in profile_data:
        print(f"  [SKIP] {job_dir.name}/optimized_resume.json still contains placeholder data")
        return None

    if job_description.startswith("#"):
        print(f"  [SKIP] {job_dir.name}/job_description.txt still contains placeholder data")
        return None

    company_name = profile_data.get("Target company", job_dir.name)
    role_name = profile_data.get("Target role", job_dir.name)

    return CoverLetterRequest(
        profile_data=profile_data,
        job_description=job_description,
        company_name=company_name,
        role_name=role_name,
        tone="professional",
    )


def run(job_filter: str | None = None, evaluate: bool = False) -> None:
    job_dirs = sorted(
        d for d in FIXTURES_DIR.iterdir()
        if d.is_dir() and (job_filter is None or d.name == job_filter)
    )

    if not job_dirs:
        print(f"No fixture directories found under {FIXTURES_DIR}")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    all_eval_results: list[dict] = []

    for job_dir in job_dirs:
        print(f"\n{'='*60}")
        print(f"Processing: {job_dir.name}")
        print("=" * 60)

        request = load_fixture(job_dir)
        if request is None:
            continue

        print(f"  Company : {request.company_name}")
        print(f"  Role    : {request.role_name}")
        print(f"  Tone    : {request.tone}")
        print("  Generating cover letter...")

        cover_letter = cover_letter_service.generate_cover_letter(request)

        output_file = OUTPUT_DIR / f"{job_dir.name}_cover_letter.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cover_letter)

        print(f"\n--- Generated Cover Letter ({job_dir.name}) ---\n")
        print(cover_letter)
        print(f"\n[Saved to {output_file}]")

        # --- Optional LLM-as-a-judge evaluation ---
        if evaluate:
            print(f"\n--- Evaluating constraints ({job_dir.name}) ---")
            from tests.evaluation.cover_letter_evaluator import evaluate as run_evaluation

            profile = _extract_profile_summary(request.profile_data)
            resume_summary = (
                f"Experience:\n{profile['experience']}\n\n"
                f"Skills:\n{profile['skills']}\n\n"
                f"Projects:\n{profile['projects']}"
            )

            result = run_evaluation(
                cover_letter=cover_letter,
                job_description=request.job_description,
                resume_summary=resume_summary,
                candidate_name=profile["name"],
            )

            print(f"\n  Total Score : {result['total_score']} / 8")
            print(f"  Accuracy    : {result['accuracy'] * 100:.0f}%")

            eval_output_file = OUTPUT_DIR / f"{job_dir.name}_evaluation.json"
            with open(eval_output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"  [Evaluation saved to {eval_output_file}]")

            all_eval_results.append({"job": job_dir.name, **result})

    # --- Aggregate summary when evaluating multiple jobs ---
    if evaluate and len(all_eval_results) > 1:
        print(f"\n{'='*60}")
        print("AGGREGATE EVALUATION SUMMARY")
        print("=" * 60)
        avg_accuracy = sum(r["accuracy"] for r in all_eval_results) / len(all_eval_results)
        for r in all_eval_results:
            print(f"  {r['job']:10s}  score={r['total_score']}/8  accuracy={r['accuracy']*100:.0f}%")
        print(f"\n  Average accuracy across {len(all_eval_results)} jobs: {avg_accuracy*100:.0f}%")


if __name__ == "__main__":
    args = sys.argv[1:]
    run_evaluate = "--evaluate" in args
    remaining = [a for a in args if a != "--evaluate"]
    job_filter = remaining[0] if remaining else None
    run(job_filter, evaluate=run_evaluate)
