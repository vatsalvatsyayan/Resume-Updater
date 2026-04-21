"""
Generate PDF from sample_resume_input1.json without calling the API or LLM.
Run from backend/:
  python run_pdf_test.py
"""
from pathlib import Path

from resume_generation.generator import input_to_tailored_no_llm
from resume_generation.pdf_template import build_pdf_template

BACKEND_DIR = Path(__file__).resolve().parent
SAMPLE_JSON = BACKEND_DIR / "sample_resume_input1.json"
OUT_PDF = BACKEND_DIR / "out_resume.pdf"


def main():
    import json
    if not SAMPLE_JSON.exists():
        print(f"Missing {SAMPLE_JSON}")
        return
    with open(SAMPLE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    tailored = input_to_tailored_no_llm(data)
    print("Built TailoredResume from sample_resume_input1.json (no API/LLM).")
    build_pdf_template(tailored, output=OUT_PDF)
    print(f"Wrote -> {OUT_PDF}")
    print("Done.")


if __name__ == "__main__":
    main()
