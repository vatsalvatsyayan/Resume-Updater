#!/usr/bin/env python3
"""
Standalone test script for the resume generator.

Usage:
  1. Install deps: pip install -r requirements.txt
  2. Set API key (for direct/API): export GOOGLE_API_KEY=your_gemini_api_key

  Direct (no server):
    python run_test.py [--no-pdf] [--output path/to/resume.pdf] [--input sample_input.json]

  Via FastAPI (server must be running on --api URL):
    python run_test.py --api http://localhost:8001 [--output path/to/resume.pdf] [--input sample_input.json]
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

# Ensure package is importable: add resume-generator folder to path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Test the resume generator")
    parser.add_argument(
        "--input",
        type=Path,
        default=_root / "sample_input.json",
        help="Path to input JSON (ResumeGeneratorInput)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_root / "generated_resume.pdf",
        help="Path for output PDF (default: generated_resume.pdf in this folder)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation; only run tailoring and print tailored JSON (direct mode only)",
    )
    parser.add_argument(
        "--api",
        metavar="URL",
        default=None,
        help="Use FastAPI server instead of direct call (e.g. http://localhost:8001)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    try:
        from resume_generator.schemas import ResumeGeneratorInput
        ResumeGeneratorInput.model_validate(data)
    except Exception as e:
        print(f"Error: Invalid input schema: {e}", file=sys.stderr)
        return 1

    if args.api:
        return _run_via_api(args, data)
    return _run_direct(args, data)


def _run_via_api(args, data: dict) -> int:
    """Call POST /generate on the FastAPI server and optionally save PDF."""
    try:
        import urllib.request
        req = urllib.request.Request(
            args.api.rstrip("/") + "/generate",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        return 1
    tailored = out.get("tailored_resume")
    pdf_b64 = out.get("pdf_base64")
    if tailored:
        print(json.dumps(tailored, indent=2))
    if pdf_b64:
        pdf_bytes = base64.b64decode(pdf_b64)
        args.output.write_bytes(pdf_bytes)
        print(f"\nPDF saved to: {args.output}", file=sys.stderr)
    return 0


def _run_direct(args, data: dict) -> int:
    """Run generator in-process (no server)."""
    from resume_generator.generator import generate_resume
    from resume_generator.schemas import ResumeGeneratorInput

    input_schema = ResumeGeneratorInput.model_validate(data)
    print("Running resume tailor (LLM may take 10–30 seconds)...")
    try:
        if args.no_pdf:
            from resume_generator.config import ResumeGeneratorConfig
            from resume_generator.services import TailorService
            cfg = ResumeGeneratorConfig()
            tailor = TailorService(llm_config=cfg.llm_config())
            tailored = tailor.tailor(input_schema)
            print(json.dumps(tailored.model_dump(), indent=2))
            print("\nTailored resume (JSON) printed above. No PDF generated (--no-pdf).")
            return 0
        tailored, pdf_result = generate_resume(
            input_schema,
            output_pdf_path=args.output,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Tailored resume generated successfully.")
    print(f"PDF written to: {pdf_result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
