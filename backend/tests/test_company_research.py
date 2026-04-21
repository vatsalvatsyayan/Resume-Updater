"""
Manual integration test for the company research service.

Uses Gemini Deep Research to produce a structured company summary and
prints/saves the result. Deep Research can take 1-5 minutes per company,
so the script prints progress while polling.

Usage (from the backend/ directory, with venv activated):

  Research a company (no role context):
    python -m tests.test_company_research "Google"

  Research a company with a specific role for focused results:
    python -m tests.test_company_research "Google" --role "Software Engineer"

  Research multiple companies (no role):
    python -m tests.test_company_research "Google" "Stripe" "OpenAI"

  No arguments — runs a default set of companies:
    python -m tests.test_company_research

Output is saved to tests/output/research_<company>.txt

Requires GEMINI_API_KEY to be set in backend/.env
"""

import sys
import time
from pathlib import Path

# Allow imports from the backend/ root (services, core)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.company_research_service import research

OUTPUT_DIR = Path(__file__).parent / "output"

_DEFAULT_COMPANIES = ["Google", "Stripe"]


def _safe_filename(name: str) -> str:
    """Convert a string to a safe filename slug."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def run(companies: list[str], role: str | None = None) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    for company in companies:
        print(f"\n{'='*60}")
        print(f"Researching : {company}")
        if role:
            print(f"Role context: {role}")
        print("=" * 60)
        print("  Calling Gemini Deep Research (this may take 1-5 minutes)...")

        start = time.time()
        result = research(company, role=role)
        elapsed = time.time() - start

        if result:
            label = f"{company}" + (f" ({role})" if role else "")
            print(f"\n--- Research Output ({label}) ---\n")
            print(result)
            print(f"\n[Completed in {elapsed:.0f}s]")

            slug = _safe_filename(company)
            if role:
                slug += f"_{_safe_filename(role)}"
            output_file = OUTPUT_DIR / f"research_{slug}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"[Saved to {output_file}]")
        else:
            print(f"\n  [FAILED] research() returned None for '{company}'")
            print("  Possible causes:")
            print("    - GEMINI_API_KEY not set in backend/.env")
            print("    - Deep Research agent unavailable or timed out (5 min limit)")
            print("    - Network error during polling")


if __name__ == "__main__":
    args = sys.argv[1:]

    role: str | None = None
    if "--role" in args:
        idx = args.index("--role")
        if idx + 1 < len(args):
            role = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    companies = args if args else _DEFAULT_COMPANIES
    run(companies, role=role)
