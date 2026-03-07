from __future__ import annotations

import io
import re
from html import unescape
from typing import Iterable
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, UploadFile, status
from schemas.profile_import import (
    Certification,
    Education,
    ImportedProfileData,
    Leadership,
    PersonalInfo,
    Project,
    Skills,
    Volunteer,
    WorkExperience,
)

MONTH_LOOKUP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

MONTH_PATTERN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_TOKEN_PATTERN = rf"(?:{MONTH_PATTERN}\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
DATE_RANGE_PATTERN = re.compile(
    rf"(?P<start>{DATE_TOKEN_PATTERN})\s*(?:-|–|—|to)\s*(?P<end>{DATE_TOKEN_PATTERN}|Present|Current|Now)",
    re.IGNORECASE,
)

SECTION_ALIASES = {
    "education": {"education", "academic background"},
    "workExperience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    },
    "projects": {"projects", "personal projects", "selected projects"},
    "skills": {
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "tools",
    },
    "certifications": {"certifications", "licenses", "licenses and certifications"},
    "volunteer": {"volunteer", "volunteer experience", "community involvement"},
    "leadership": {
        "leadership",
        "leadership experience",
        "activities",
        "extracurriculars",
    },
}

SKILL_KEYWORDS = {
    "programmingLanguages": {
        "python",
        "java",
        "javascript",
        "typescript",
        "go",
        "golang",
        "c",
        "c++",
        "c#",
        "ruby",
        "rust",
        "swift",
        "kotlin",
        "php",
        "scala",
        "r",
        "sql",
        "html",
        "css",
        "bash",
    },
    "frameworks": {
        "react",
        "next.js",
        "vue",
        "angular",
        "svelte",
        "node.js",
        "express",
        "django",
        "flask",
        "fastapi",
        "spring",
        "laravel",
        "tailwind",
        "bootstrap",
        "pandas",
        "numpy",
        "pytest",
    },
    "databases": {
        "postgresql",
        "postgres",
        "mysql",
        "mongodb",
        "redis",
        "sqlite",
        "dynamodb",
        "cassandra",
        "elasticsearch",
        "bigquery",
    },
    "toolsAndTechnologies": {
        "git",
        "github",
        "docker",
        "kubernetes",
        "terraform",
        "linux",
        "jira",
        "postman",
        "graphql",
        "rest",
        "rest api",
        "ci/cd",
        "github actions",
        "jenkins",
        "figma",
    },
    "cloud": {
        "aws",
        "amazon web services",
        "gcp",
        "google cloud",
        "azure",
        "firebase",
        "vercel",
        "netlify",
        "cloudflare",
    },
    "ai": {
        "openai",
        "langchain",
        "llamaindex",
        "pytorch",
        "tensorflow",
        "hugging face",
        "scikit-learn",
        "machine learning",
        "deep learning",
        "nlp",
        "generative ai",
        "llm",
    },
}

SKILL_LABELS = {
    "programmingLanguages": {
        "language",
        "languages",
        "programming language",
        "programming languages",
    },
    "frameworks": {"frameworks", "libraries", "framework", "library"},
    "databases": {"database", "databases"},
    "toolsAndTechnologies": {"tools", "technologies", "platforms", "tooling"},
    "cloud": {"cloud", "cloud platforms", "cloud services"},
    "ai": {"ai", "ml", "machine learning", "artificial intelligence"},
}

DEGREE_KEYWORDS = {
    "Bachelor's": {"bachelor", "b.s", "bs", "b.a", "ba", "b.eng", "undergraduate"},
    "Master's": {"master", "m.s", "ms", "m.eng", "mba", "graduate"},
    "PhD": {"phd", "ph.d", "doctorate"},
    "Diploma": {"diploma"},
    "Certificate": {"certificate"},
    "Associate": {"associate"},
}

COMPANY_HINTS = (
    "inc",
    "llc",
    "corp",
    "corporation",
    "company",
    "technologies",
    "solutions",
    "labs",
    "university",
    "college",
    "school",
    "bank",
)


class ProfileImportService:
    async def import_profile(
        self,
        resume_file: UploadFile | None = None,
        resume_text: str | None = None,
        linkedin_url: str | None = None,
    ) -> tuple[ImportedProfileData, list[str], list[str]]:
        data = ImportedProfileData()
        warnings: list[str] = []
        sources: list[str] = []

        text_source = (resume_text or "").strip()
        if resume_file is not None:
            text_source = await self._extract_text_from_upload(resume_file)
            sources.append("resume")
        elif text_source:
            sources.append("resume_text")

        if text_source:
            data = self._merge_profile_data(data, self._parse_resume_text(text_source))
            if not self._has_any_data(data):
                warnings.append(
                    "The uploaded resume could be read, but very little structured data was extracted."
                )

        if linkedin_url:
            linkedin_data, linkedin_warnings = await self._parse_linkedin_profile(
                linkedin_url
            )
            data = self._merge_profile_data(data, linkedin_data)
            warnings.extend(linkedin_warnings)
            sources.append("linkedin")

        return data, self._unique_strings(warnings), self._unique_strings(sources)

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
                return self._decode_text_bytes(file_bytes)
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

    def _parse_resume_text(self, text: str) -> ImportedProfileData:
        normalized_text = self._normalize_text(text)
        section_map, header_lines = self._split_sections(normalized_text)

        return ImportedProfileData(
            personalInfo=self._extract_personal_info(normalized_text, header_lines),
            education=self._parse_education_section(section_map.get("education", "")),
            workExperience=self._parse_work_experience_section(
                section_map.get("workExperience", "")
            ),
            projects=self._parse_projects_section(section_map.get("projects", "")),
            skills=self._extract_skills(section_map.get("skills", "")),
            certifications=self._parse_certifications_section(
                section_map.get("certifications", "")
            ),
            volunteer=self._parse_volunteer_section(section_map.get("volunteer", "")),
            leadership=self._parse_leadership_section(
                section_map.get("leadership", "")
            ),
        )

    async def _parse_linkedin_profile(
        self,
        linkedin_url: str,
    ) -> tuple[ImportedProfileData, list[str]]:
        normalized_url = self._normalize_linkedin_url(linkedin_url)
        data = ImportedProfileData(
            personalInfo=PersonalInfo(linkedinUrl=normalized_url)
        )
        warnings: list[str] = []

        html = await self._fetch_public_profile(normalized_url)
        if not html:
            guessed_name = self._guess_name_from_url(normalized_url)
            if guessed_name:
                data.personalInfo.name = guessed_name
            warnings.append(
                "LinkedIn import is best-effort and only works reliably for public profiles."
            )
            return data, warnings

        title = self._extract_meta_content(html, "og:title") or self._extract_title(
            html
        )
        description = self._extract_meta_content(html, "og:description")

        clean_name = self._clean_linkedin_name(title)
        if clean_name:
            data.personalInfo.name = clean_name
        elif guessed_name := self._guess_name_from_url(normalized_url):
            data.personalInfo.name = guessed_name

        if description:
            headline = self._strip_linkedin_suffix(description)
            work_experience = self._work_from_headline(headline)
            if work_experience:
                data.workExperience.append(work_experience)

        if not data.personalInfo.name and not data.workExperience:
            warnings.append(
                "LinkedIn returned limited public metadata, so only the profile URL could be imported."
            )

        return data, warnings

    async def _fetch_public_profile(self, url: str) -> str | None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=8.0, headers=headers
            ) as client:
                response = await client.get(url)
        except httpx.HTTPError:
            return None

        if response.status_code >= 400:
            return None

        if "Sign in" in response.text and "LinkedIn" in response.text:
            return None

        return response.text

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _split_sections(self, text: str) -> tuple[dict[str, str], list[str]]:
        section_content: dict[str, list[str]] = {}
        header_lines: list[str] = []
        current_section: str | None = None

        for line in text.splitlines():
            stripped_line = line.strip()
            matched_section = self._match_section_heading(stripped_line)
            if matched_section:
                current_section = matched_section
                section_content.setdefault(current_section, [])
                continue

            if current_section is None:
                header_lines.append(stripped_line)
            else:
                section_content[current_section].append(stripped_line)

        return (
            {key: "\n".join(value).strip() for key, value in section_content.items()},
            header_lines,
        )

    def _match_section_heading(self, line: str) -> str | None:
        if not line:
            return None

        normalized = re.sub(r"[^a-z/& ]", "", line.lower()).strip()
        normalized = normalized.replace("&", "and")

        for section, aliases in SECTION_ALIASES.items():
            if normalized in {alias.replace("&", "and") for alias in aliases}:
                return section
        return None

    def _extract_personal_info(
        self, text: str, header_lines: list[str]
    ) -> PersonalInfo:
        urls = self._extract_urls(text)
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        linkedin_url = next(
            (url for url in urls if "linkedin.com" in url.lower()), None
        )
        github_url = next((url for url in urls if "github.com" in url.lower()), None)
        portfolio_url = next(
            (
                url
                for url in urls
                if "linkedin.com" not in url.lower() and "github.com" not in url.lower()
            ),
            None,
        )

        return PersonalInfo(
            name=self._extract_name_from_header(header_lines),
            email=email_match.group(0) if email_match else "",
            portfolioWebsite=portfolio_url,
            githubUrl=github_url,
            linkedinUrl=linkedin_url,
        )

    def _extract_name_from_header(self, header_lines: list[str]) -> str:
        for line in header_lines[:6]:
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
            if any(
                token in cleaned_line.lower()
                for token in ("http", "@", "linkedin", "github")
            ):
                continue
            if any(char.isdigit() for char in cleaned_line):
                continue

            words = cleaned_line.replace("|", " ").split()
            if 2 <= len(words) <= 5:
                return cleaned_line.title() if cleaned_line.isupper() else cleaned_line
        return ""

    def _extract_urls(self, text: str) -> list[str]:
        raw_urls = re.findall(
            r"(?:(?:https?://|www\.)[^\s<>()]+|(?:linkedin|github)\.com/[^\s<>()]+)",
            text,
            flags=re.IGNORECASE,
        )

        cleaned_urls: list[str] = []
        for raw_url in raw_urls:
            cleaned_url = raw_url.rstrip(".,);")
            if not cleaned_url.startswith(("http://", "https://")):
                cleaned_url = f"https://{cleaned_url}"
            cleaned_urls.append(cleaned_url)
        return self._unique_strings(cleaned_urls)

    def _parse_work_experience_section(self, text: str) -> list[WorkExperience]:
        entries: list[WorkExperience] = []
        for block in self._split_blocks(text):
            parsed = self._parse_work_block(block)
            if parsed and (parsed.position or parsed.companyName):
                entries.append(parsed)
        return entries

    def _parse_education_section(self, text: str) -> list[Education]:
        entries: list[Education] = []
        for block in self._split_blocks(text):
            parsed = self._parse_education_block(block)
            if parsed and (parsed.universityName or parsed.courseName or parsed.major):
                entries.append(parsed)
        return entries

    def _parse_projects_section(self, text: str) -> list[Project]:
        entries: list[Project] = []
        for block in self._split_blocks(text):
            parsed = self._parse_project_block(block)
            if parsed and parsed.projectName:
                entries.append(parsed)
        return entries

    def _parse_certifications_section(self, text: str) -> list[Certification]:
        entries: list[Certification] = []
        for block in self._split_blocks(text):
            parsed = self._parse_certification_block(block)
            if parsed and parsed.name:
                entries.append(parsed)
        return entries

    def _parse_volunteer_section(self, text: str) -> list[Volunteer]:
        entries: list[Volunteer] = []
        for block in self._split_blocks(text):
            parsed = self._parse_volunteer_block(block)
            if parsed and (parsed.organizationName or parsed.role):
                entries.append(parsed)
        return entries

    def _parse_leadership_section(self, text: str) -> list[Leadership]:
        entries: list[Leadership] = []
        for block in self._split_blocks(text):
            parsed = self._parse_leadership_block(block)
            if parsed and (parsed.title or parsed.organization):
                entries.append(parsed)
        return entries

    def _split_blocks(self, text: str) -> list[str]:
        if not text.strip():
            return []

        blocks = [block.strip() for block in re.split(r"\n{2,}", text) if block.strip()]
        if blocks:
            return blocks
        return [text.strip()]

    def _parse_work_block(self, block: str) -> WorkExperience | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        start_date, end_date, is_present = self._extract_date_range(block)
        description_lines = [
            line for line in lines if not self._contains_date_range(line)
        ]
        position, company_name = self._extract_role_and_company(description_lines[:2])
        location = self._extract_location(lines)
        summary, description = self._summarize_description(description_lines[2:])

        return WorkExperience(
            companyName=company_name,
            position=position,
            location=location,
            startDate=start_date,
            endDate=end_date,
            isPresent=is_present,
            summary=summary,
            description=description,
        )

    def _parse_education_block(self, block: str) -> Education | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        block_text = " | ".join(lines)
        degree_line = next(
            (line for line in lines if self._detect_course_type(line)), ""
        )
        school_line = next(
            (
                line
                for line in lines
                if any(
                    token in line.lower()
                    for token in ("university", "college", "school", "institute")
                )
            ),
            lines[0],
        )
        start_date, end_date, is_present = self._extract_date_range(block)
        gpa_match = re.search(
            r"gpa[: ]+([0-4]\.\d{1,2}|[0-4])", block_text, re.IGNORECASE
        )
        major = self._extract_major(degree_line or block_text)

        return Education(
            universityName=school_line,
            courseName=degree_line or school_line,
            courseType=self._detect_course_type(degree_line or block_text),
            major=major,
            gpa=gpa_match.group(1) if gpa_match else None,
            location=self._extract_location(lines),
            startDate=start_date,
            endDate=end_date,
            isPresent=is_present,
        )

    def _parse_project_block(self, block: str) -> Project | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        urls = self._extract_urls(block)
        tech_line = next(
            (
                line
                for line in lines
                if any(
                    line.lower().startswith(prefix)
                    for prefix in ("tech", "stack", "tools", "built with")
                )
            ),
            "",
        )
        description_lines = [
            line for line in lines[1:] if line != tech_line and line not in urls
        ]
        summary, description = self._summarize_description(description_lines)

        return Project(
            projectName=lines[0],
            link=urls[0] if urls else None,
            techStack=self._extract_skill_tokens(tech_line),
            summary=summary,
            description=description,
        )

    def _parse_certification_block(self, block: str) -> Certification | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        start_date, end_date, _ = self._extract_date_range(block)
        credential_id_match = re.search(r"credential id[: ]+(.+)", block, re.IGNORECASE)
        urls = self._extract_urls(block)
        organization = ""
        if len(lines) > 1 and not self._contains_date_range(lines[1]):
            organization = lines[1]

        return Certification(
            name=lines[0],
            issuingOrganization=organization,
            issueDate=start_date,
            expiryDate=end_date,
            hasNoExpiry=bool(start_date and not end_date),
            credentialId=credential_id_match.group(1).strip()
            if credential_id_match
            else None,
            credentialUrl=urls[0] if urls else None,
        )

    def _parse_volunteer_block(self, block: str) -> Volunteer | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        start_date, end_date, is_present = self._extract_date_range(block)
        role, organization = self._extract_role_and_company(lines[:2])
        _, description = self._summarize_description(lines[2:])

        return Volunteer(
            organizationName=organization,
            role=role,
            location=self._extract_location(lines),
            startDate=start_date,
            endDate=end_date,
            isPresent=is_present,
            description=description,
        )

    def _parse_leadership_block(self, block: str) -> Leadership | None:
        lines = self._meaningful_lines(block)
        if not lines:
            return None

        start_date, end_date, is_present = self._extract_date_range(block)
        title, organization = self._extract_role_and_company(lines[:2])
        _, description = self._summarize_description(lines[2:])

        return Leadership(
            title=title,
            organization=organization,
            startDate=start_date,
            endDate=end_date,
            isPresent=is_present,
            description=description,
        )

    def _extract_role_and_company(self, lines: list[str]) -> tuple[str, str]:
        if not lines:
            return "", ""

        first_line = lines[0]
        if " at " in first_line.lower():
            position, company = re.split(
                r"\sat\s", first_line, maxsplit=1, flags=re.IGNORECASE
            )
            return position.strip(), company.strip()

        for separator in (" | ", " @ ", " - "):
            if separator in first_line:
                left, right = first_line.split(separator, 1)
                if self._looks_like_company(left):
                    return right.strip(), left.strip()
                return left.strip(), right.strip()

        if len(lines) > 1:
            second_line = lines[1]
            if self._looks_like_company(first_line) and not self._contains_date_range(
                second_line
            ):
                return second_line.strip(), first_line.strip()
            if not self._contains_date_range(second_line):
                return first_line.strip(), second_line.split(" | ")[0].strip()

        return first_line.strip(), ""

    def _extract_location(self, lines: list[str]) -> str | None:
        for line in lines:
            if self._contains_date_range(line):
                continue
            lowered = line.lower()
            if "remote" in lowered:
                return "Remote"
            if any(
                keyword in lowered
                for keyword in (
                    "university",
                    "college",
                    "school",
                    "institute",
                    "bachelor",
                    "master",
                    "phd",
                    "certificate",
                )
            ):
                continue
            if any(token in lowered for token in COMPANY_HINTS):
                continue
            if re.fullmatch(r"[A-Za-z .'-]+,\s*[A-Z]{2}", line) or re.fullmatch(
                r"[A-Za-z .'-]+,\s*[A-Za-z .'-]+",
                line,
            ):
                return line
        return None

    def _extract_major(self, text: str) -> str:
        major_match = re.search(
            r"(?:major|field of study|in)\s*[:\-]?\s*([A-Za-z& /]+)",
            text,
            re.IGNORECASE,
        )
        if major_match:
            return major_match.group(1).strip()
        return ""

    def _detect_course_type(self, text: str) -> str:
        lowered = text.lower()
        for course_type, keywords in DEGREE_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return course_type
        return ""

    def _extract_skills(self, section_text: str) -> Skills:
        categorized = {key: [] for key in Skills().model_dump().keys()}
        remaining_tokens: list[str] = []

        for line in self._meaningful_lines(section_text):
            if ":" in line:
                label, values = line.split(":", 1)
                category = self._match_skill_label(label)
                tokens = self._extract_skill_tokens(values)
                if category:
                    categorized[category].extend(tokens)
                    continue
            remaining_tokens.extend(self._extract_skill_tokens(line))

        for token in remaining_tokens:
            category = self._categorize_skill(token)
            categorized[category].append(token)

        return Skills(
            **{key: self._unique_strings(value) for key, value in categorized.items()}
        )

    def _match_skill_label(self, label: str) -> str | None:
        normalized = label.strip().lower()
        for category, aliases in SKILL_LABELS.items():
            if normalized in aliases:
                return category
        return None

    def _extract_skill_tokens(self, text: str) -> list[str]:
        cleaned_text = re.sub(
            r"^(tech stack|technologies|tools|built with)[: ]*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        raw_tokens = re.split(r"[,;/|]\s*|\s{2,}", cleaned_text)
        tokens = [self._clean_token(token) for token in raw_tokens]
        return [token for token in tokens if token]

    def _categorize_skill(self, token: str) -> str:
        lowered = token.lower()
        for category, keywords in SKILL_KEYWORDS.items():
            if lowered in keywords:
                return category
        return "other"

    def _extract_date_range(self, text: str) -> tuple[str | None, str | None, bool]:
        match = DATE_RANGE_PATTERN.search(text)
        if not match:
            return None, None, False

        start_token = match.group("start")
        end_token = match.group("end")
        is_present = end_token.lower() in {"present", "current", "now"}

        return (
            self._parse_date_token(start_token),
            None if is_present else self._parse_date_token(end_token, is_end=True),
            is_present,
        )

    def _parse_date_token(self, token: str, is_end: bool = False) -> str | None:
        cleaned = token.replace(",", "").strip()
        if cleaned.lower() in {"present", "current", "now"}:
            return None

        if re.fullmatch(r"\d{1,2}/\d{4}", cleaned):
            month, year = cleaned.split("/")
            return f"{int(year):04d}-{int(month):02d}-01"

        if re.fullmatch(r"\d{4}", cleaned):
            month = 12 if is_end else 1
            return f"{int(cleaned):04d}-{month:02d}-01"

        month_text, year_text = cleaned.split()
        month_value = MONTH_LOOKUP.get(month_text[:4].lower().rstrip("."))
        if month_value is None:
            return None
        return f"{int(year_text):04d}-{month_value:02d}-01"

    def _summarize_description(self, lines: list[str]) -> tuple[str | None, str | None]:
        cleaned_lines = [
            self._strip_bullet(line) for line in lines if self._strip_bullet(line)
        ]
        if not cleaned_lines:
            return None, None

        summary = cleaned_lines[0][:180]
        description = "\n".join(cleaned_lines)
        return summary, description

    def _meaningful_lines(self, block: str) -> list[str]:
        return [
            self._clean_token(line)
            for line in block.splitlines()
            if self._clean_token(line)
        ]

    def _strip_bullet(self, line: str) -> str:
        return re.sub(r"^[\-*•]+\s*", "", line).strip()

    def _clean_token(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _contains_date_range(self, line: str) -> bool:
        return bool(DATE_RANGE_PATTERN.search(line))

    def _looks_like_company(self, value: str) -> bool:
        lowered = value.lower()
        return any(hint in lowered for hint in COMPANY_HINTS)

    def _normalize_linkedin_url(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            cleaned = f"https://{cleaned}"

        parsed = urlparse(cleaned)
        if "linkedin.com" not in parsed.netloc.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided URL is not a LinkedIn profile URL.",
            )
        if not parsed.path.startswith(("/in/", "/pub/")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide a LinkedIn public profile URL, such as linkedin.com/in/username.",
            )

        return parsed._replace(query="", fragment="").geturl().rstrip("/")

    def _guess_name_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        slug = parsed.path.rstrip("/").split("/")[-1]
        slug = re.sub(r"-?\d+$", "", slug)
        slug = slug.replace("-", " ").replace("_", " ").strip()
        return slug.title()

    def _extract_meta_content(self, html: str, property_name: str) -> str | None:
        pattern = re.compile(
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(property_name)}["\'][^>]+content=["\']([^"\']+)["\']',
            re.IGNORECASE,
        )
        match = pattern.search(html)
        return unescape(match.group(1)).strip() if match else None

    def _extract_title(self, html: str) -> str | None:
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return unescape(match.group(1)).strip() if match else None

    def _clean_linkedin_name(self, value: str | None) -> str:
        if not value:
            return ""
        cleaned = self._strip_linkedin_suffix(value)
        if any(
            token in cleaned.lower() for token in ("sign in", "log in", "join linkedin")
        ):
            return ""
        return cleaned

    def _strip_linkedin_suffix(self, value: str) -> str:
        return re.sub(r"\s*[|\-]\s*linkedin.*$", "", value, flags=re.IGNORECASE).strip()

    def _work_from_headline(self, headline: str) -> WorkExperience | None:
        if " at " not in headline.lower():
            return None
        position, company = re.split(
            r"\sat\s", headline, maxsplit=1, flags=re.IGNORECASE
        )
        return WorkExperience(
            position=position.strip(),
            companyName=company.strip(),
            summary=headline.strip(),
        )

    def _merge_profile_data(
        self,
        base: ImportedProfileData,
        incoming: ImportedProfileData,
    ) -> ImportedProfileData:
        for field_name in (
            "name",
            "email",
            "portfolioWebsite",
            "githubUrl",
            "linkedinUrl",
        ):
            current_value = getattr(base.personalInfo, field_name)
            incoming_value = getattr(incoming.personalInfo, field_name)
            if incoming_value and (not current_value or field_name == "linkedinUrl"):
                setattr(base.personalInfo, field_name, incoming_value)

        base.education = self._merge_model_lists(
            base.education,
            incoming.education,
            lambda item: (
                item.universityName.lower(),
                item.courseName.lower(),
                item.major.lower(),
                item.startDate or "",
            ),
        )
        base.workExperience = self._merge_model_lists(
            base.workExperience,
            incoming.workExperience,
            lambda item: (
                item.companyName.lower(),
                item.position.lower(),
                item.startDate or "",
            ),
        )
        base.projects = self._merge_model_lists(
            base.projects,
            incoming.projects,
            lambda item: (item.projectName.lower(), item.link or ""),
        )
        base.certifications = self._merge_model_lists(
            base.certifications,
            incoming.certifications,
            lambda item: (item.name.lower(), item.issuingOrganization.lower()),
        )
        base.volunteer = self._merge_model_lists(
            base.volunteer,
            incoming.volunteer,
            lambda item: (item.organizationName.lower(), item.role.lower()),
        )
        base.leadership = self._merge_model_lists(
            base.leadership,
            incoming.leadership,
            lambda item: (item.organization.lower(), item.title.lower()),
        )

        for category in base.skills.model_dump().keys():
            merged_values = self._unique_strings(
                getattr(base.skills, category) + getattr(incoming.skills, category)
            )
            setattr(base.skills, category, merged_values)

        return base

    def _merge_model_lists(self, existing: list, incoming: list, key_builder) -> list:
        seen = {key_builder(item) for item in existing}
        for item in incoming:
            item_key = key_builder(item)
            if item_key not in seen:
                existing.append(item)
                seen.add(item_key)
        return existing

    def _has_any_data(self, data: ImportedProfileData) -> bool:
        personal_info = data.personalInfo
        if any(
            [
                personal_info.name,
                personal_info.email,
                personal_info.portfolioWebsite,
                personal_info.githubUrl,
                personal_info.linkedinUrl,
            ]
        ):
            return True

        if any(
            [
                data.education,
                data.workExperience,
                data.projects,
                data.certifications,
                data.volunteer,
                data.leadership,
            ]
        ):
            return True

        return any(data.skills.model_dump().values())

    def _unique_strings(self, values: Iterable[str]) -> list[str]:
        unique_values: list[str] = []
        seen: set[str] = set()
        for value in values:
            cleaned_value = value.strip()
            if not cleaned_value:
                continue
            dedupe_key = cleaned_value.lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            unique_values.append(cleaned_value)
        return unique_values
