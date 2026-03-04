"""
Manual integration test for the cover letter generation service.

Usage (from the backend/ directory, with venv activated):
    python -m tests.test_cover_letter

For a specific job only:
    python -m tests.test_cover_letter job1

Reads all job*/  directories under tests/fixtures/ automatically.
Each directory must contain:
    - optimized_resume.json   (ProfileFormData shape)
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
from services.cover_letter_service import _extract_profile_summary, _build_prompt

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


def run(job_filter: str | None = None) -> None:
    job_dirs = sorted(
        d for d in FIXTURES_DIR.iterdir()
        if d.is_dir() and (job_filter is None or d.name == job_filter)
    )

    if not job_dirs:
        print(f"No fixture directories found under {FIXTURES_DIR}")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

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
        print("  Calling Gemini...")

        cover_letter = cover_letter_service.generate_cover_letter(request)
        
        profile = _extract_profile_summary(request.profile_data)

        output_file = OUTPUT_DIR / f"{job_dir.name}_cover_letter.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cover_letter)

        print(f"\n--- Generated Cover Letter ({job_dir.name}) ---\n")
        print(cover_letter)
        print(f"\n[Saved to {output_file}]")


if __name__ == "__main__":
    job_filter = sys.argv[1] if len(sys.argv) > 1 else None
    run(job_filter)
