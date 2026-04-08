from __future__ import annotations

import io
import json
import re

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError

from schemas.profile_import import ImportedProfileData
from services import llm_client


class ProfileImportService:
    async def import_profile(
        self,
        resume_file: UploadFile | None = None,
        resume_text: str | None = None,
    ) -> tuple[ImportedProfileData, list[str], list[str]]:
        sources: list[str] = []
        text_source = (resume_text or "").strip()

        if resume_file is not None:
            text_source = await self._extract_text_from_upload(resume_file)
            sources.append("resume")
        elif text_source:
            sources.append("resume_text")

        if not text_source:
            return ImportedProfileData(), [], sources

        data = self._parse_resume_text_with_llm(text_source)
        warnings = []
        if not self._has_any_data(data):
            warnings.append(
                "The uploaded resume could be read, but very little structured data was extracted."
            )

        return data, warnings, sources

    async def _extract_text_from_upload(self, upload: UploadFile) -> str:
        file_bytes = await upload.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded resume file is empty.",
            )

        filename = (upload.filename or "resume").lower()
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""

        try:
            if extension == "pdf":
                return self._extract_pdf_text(file_bytes)
            if extension == "docx":
                return self._extract_docx_text(file_bytes)
            if extension in {"txt", "md"} or upload.content_type == "text/plain":
                return self._decode_text_bytes(file_bytes).strip()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not read the uploaded resume: {exc}",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Upload a .pdf, .docx, or .txt resume.",
        )

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf is required to import PDF resumes.") from exc

        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

    def _extract_docx_text(self, file_bytes: bytes) -> str:
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError(
                "python-docx is required to import DOCX resumes."
            ) from exc

        document = Document(io.BytesIO(file_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    def _decode_text_bytes(self, file_bytes: bytes) -> str:
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return file_bytes.decode("utf-8", errors="ignore")

    def _parse_resume_text_with_llm(self, text: str) -> ImportedProfileData:
        raw = llm_client.generate(self._build_prompt(text))
        try:
            obj = json.loads(self._extract_json(raw))
            if isinstance(obj, dict) and isinstance(obj.get("data"), dict):
                obj = obj["data"]
            return ImportedProfileData.model_validate(obj)
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM did not return valid profile import data: {exc}",
            ) from exc

    def _build_prompt(self, text: str) -> str:
        return f"""Extract structured profile data from this resume for a user profile form.

Return only one valid JSON object. Do not include markdown or explanations.
Use empty strings, null, false, or [] for missing fields. Do not invent facts.
Dates should be ISO-like strings when possible, such as YYYY-MM-DD or YYYY-MM.

The JSON object must use exactly this shape:
{{
  "personalInfo": {{
    "name": "",
    "email": "",
    "portfolioWebsite": null,
    "githubUrl": null,
    "linkedinUrl": null
  }},
  "education": [
    {{
      "universityName": "",
      "courseName": "",
      "courseType": "Bachelor's",
      "major": "",
      "gpa": null,
      "location": null,
      "startDate": null,
      "endDate": null,
      "isPresent": false
    }}
  ],
  "workExperience": [
    {{
      "companyName": "",
      "position": "",
      "location": null,
      "startDate": null,
      "endDate": null,
      "isPresent": false,
      "summary": null,
      "description": null
    }}
  ],
  "projects": [
    {{
      "projectName": "",
      "link": null,
      "techStack": [],
      "summary": null,
      "description": null
    }}
  ],
  "skills": {{
    "programmingLanguages": [],
    "frameworks": [],
    "databases": [],
    "toolsAndTechnologies": [],
    "cloud": [],
    "ai": [],
    "other": []
  }},
  "certifications": [
    {{
      "name": "",
      "issuingOrganization": "",
      "issueDate": null,
      "expiryDate": null,
      "hasNoExpiry": false,
      "credentialId": null,
      "credentialUrl": null
    }}
  ],
  "volunteer": [
    {{
      "organizationName": "",
      "role": "",
      "cause": null,
      "location": null,
      "startDate": null,
      "endDate": null,
      "isPresent": false,
      "description": null
    }}
  ],
  "leadership": [
    {{
      "title": "",
      "organization": "",
      "startDate": null,
      "endDate": null,
      "isPresent": false,
      "description": null
    }}
  ]
}}

For courseType, use one of: "Bachelor's", "Master's", "PhD", "Diploma", "Certificate", "Associate", "".
If a section has no entries, return an empty array for that section.

Resume text:
{text}"""

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        return match.group(1).strip() if match else text

    def _has_any_data(self, data: ImportedProfileData) -> bool:
        personal_info = data.personalInfo
        return any(
            [
                personal_info.name,
                personal_info.email,
                personal_info.portfolioWebsite,
                personal_info.githubUrl,
                personal_info.linkedinUrl,
                data.education,
                data.workExperience,
                data.projects,
                data.certifications,
                data.volunteer,
                data.leadership,
                *data.skills.model_dump().values(),
            ]
        )
