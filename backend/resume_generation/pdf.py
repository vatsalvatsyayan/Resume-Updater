"""
Build a PDF from a TailoredResume using fpdf2 (pure Python, no system deps).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .schemas.output_schema import TailoredResume


def _pdf_safe(text: str) -> str:
    """Replace Unicode characters unsupported by Helvetica."""
    if not text:
        return text
    return (
        text.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


_PAGE_HEIGHT_MM = 297.0
_MIN_SECTION_BUFFER_MM = 12.0


class PDFBuilder:
    """Generates a one-page resume PDF from TailoredResume."""

    def __init__(
        self,
        font_size_body: int = 9,
        font_size_title: int = 16,
        font_size_section: int = 11,
        margin: float = 12.0,
        line_height: float = 1.2,
    ) -> None:
        self.font_size_body = font_size_body
        self.font_size_title = font_size_title
        self.font_size_section = font_size_section
        self.margin = margin
        self.line_height = line_height
        self._max_y = _PAGE_HEIGHT_MM - margin

    def build(
        self,
        resume: TailoredResume,
        output: Optional[Union[str, Path]] = None,
    ) -> Union[bytes, Path]:
        try:
            from fpdf import FPDF
        except ImportError as e:
            raise ImportError(
                "fpdf2 is required for PDF generation. Install with: pip install fpdf2"
            ) from e

        pdf = FPDF(unit="mm", format="A4")
        pdf.set_auto_page_break(auto=False)
        pdf.set_margins(self.margin, self.margin, self.margin)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", self.font_size_title)
        pdf.cell(0, 6, _pdf_safe(resume.name or "Resume"), new_x="LMARGIN", new_y="NEXT")

        contact_parts = [
            p
            for p in [
                resume.email,
                resume.portfolioWebsite,
                resume.githubUrl,
                resume.linkedinUrl,
            ]
            if p
        ]
        if contact_parts:
            pdf.set_font("Helvetica", "", self.font_size_body - 1)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(
                0,
                5,
                _pdf_safe(" | ".join(contact_parts)),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

        if resume.professionalSummary and self._has_room(pdf, 25):
            self._section(pdf, "Summary")
            pdf.set_font("Helvetica", "", self.font_size_body)
            self._multiline_truncate(pdf, _pdf_safe(resume.professionalSummary), max_lines=3)
            pdf.ln(2)

        if resume.education and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Education")
            for e in resume.education:
                if not self._has_room(pdf, 18):
                    break
                self._block_title(
                    pdf,
                    _pdf_safe(f"{e.courseName}, {e.major}"),
                    _pdf_safe(e.universityName) if e.universityName else None,
                )
                date_str = self._date_range(e.startDate, e.endDate, e.isPresent)
                if date_str:
                    pdf.set_font("Helvetica", "", self.font_size_body - 1)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(0, 4, _pdf_safe(date_str), new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)
                if e.gpa:
                    pdf.cell(0, 4, _pdf_safe(f"GPA: {e.gpa}"), new_x="LMARGIN", new_y="NEXT")
                if getattr(e, "highlight", None):
                    pdf.set_font("Helvetica", "", self.font_size_body - 1)
                    self._multiline_truncate(pdf, _pdf_safe(e.highlight), max_lines=1)
                pdf.set_font("Helvetica", "", self.font_size_body)
                pdf.ln(1)

        if resume.workExperience and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Experience")
            for w in resume.workExperience:
                if not self._has_room(pdf, 20):
                    break
                self._block_title(
                    pdf,
                    _pdf_safe(w.position),
                    _pdf_safe(w.companyName) if w.companyName else None,
                )
                date_str = self._date_range(w.startDate, w.endDate, w.isPresent)
                if date_str:
                    pdf.set_font("Helvetica", "", self.font_size_body - 1)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(
                        0,
                        4,
                        _pdf_safe(date_str + (f" | {w.location}" if w.location else "")),
                        new_x="LMARGIN",
                        new_y="NEXT",
                    )
                    pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", self.font_size_body)
                for b in w.bullets:
                    if not self._has_room(pdf, 8):
                        break
                    self._bullet(pdf, _pdf_safe(b))
                pdf.ln(1)

        if resume.projects and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Projects")
            for p in resume.projects:
                if not self._has_room(pdf, 20):
                    break
                sub = p.link or (", ".join(p.techStack) if p.techStack else None)
                self._block_title(
                    pdf,
                    _pdf_safe(p.projectName),
                    _pdf_safe(sub) if sub else None,
                )
                if p.techStack and p.link:
                    pdf.set_font("Helvetica", "", self.font_size_body - 1)
                    pdf.cell(0, 4, _pdf_safe(", ".join(p.techStack)), new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", self.font_size_body)
                for b in p.bullets:
                    if not self._has_room(pdf, 8):
                        break
                    self._bullet(pdf, _pdf_safe(b))
                pdf.ln(1)

        if resume.skills and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Skills")
            pdf.set_font("Helvetica", "", self.font_size_body)
            self._multiline_truncate(pdf, _pdf_safe(", ".join(resume.skills)), max_lines=2)
            pdf.ln(2)

        if resume.certifications and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Certifications")
            for c in resume.certifications:
                if not self._has_room(pdf, 10):
                    break
                pdf.set_font("Helvetica", "B", self.font_size_body)
                pdf.cell(0, 4, _pdf_safe(c.name), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", self.font_size_body - 1)
                pdf.cell(0, 4, _pdf_safe(c.issuingOrganization), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", self.font_size_body)
                pdf.ln(1)

        if resume.volunteer and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Volunteer")
            for v in resume.volunteer:
                if not self._has_room(pdf, 15):
                    break
                self._block_title(
                    pdf,
                    _pdf_safe(v.role),
                    _pdf_safe(v.organizationName) if v.organizationName else None,
                )
                for b in v.bullets:
                    if not self._has_room(pdf, 6):
                        break
                    self._bullet(pdf, _pdf_safe(b))
                pdf.ln(1)

        if resume.leadership and self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
            self._section(pdf, "Leadership")
            for l in resume.leadership:
                if not self._has_room(pdf, 15):
                    break
                self._block_title(
                    pdf,
                    _pdf_safe(l.title),
                    _pdf_safe(l.organization) if l.organization else None,
                )
                for b in l.bullets:
                    if not self._has_room(pdf, 6):
                        break
                    self._bullet(pdf, _pdf_safe(b))
                pdf.ln(1)

        for sec in resume.extraSections:
            if not sec.items or not self._has_room(pdf, _MIN_SECTION_BUFFER_MM):
                continue
            self._section(pdf, _pdf_safe(sec.title))
            for item in sec.items:
                if not self._has_room(pdf, 6):
                    break
                self._bullet(pdf, _pdf_safe(item))
            pdf.ln(1)

        if output is not None:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            pdf.output(path)
            return path

        pdf_raw = pdf.output()

        if isinstance(pdf_raw, bytearray):
            return bytes(pdf_raw)
        if isinstance(pdf_raw, bytes):
            return pdf_raw
        return pdf_raw.encode("latin-1")

    def _has_room(self, pdf, needed_mm: float) -> bool:
        return (pdf.get_y() + needed_mm) <= self._max_y

    def _section(self, pdf, title: str) -> None:
        pdf.set_font("Helvetica", "B", self.font_size_section)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 6, _pdf_safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", self.font_size_body)

    def _block_title(self, pdf, line1: str, line2: Optional[str]) -> None:
        pdf.set_font("Helvetica", "B", self.font_size_body)
        pdf.cell(0, 4, _pdf_safe(line1), new_x="LMARGIN", new_y="NEXT")
        if line2:
            pdf.set_font("Helvetica", "", self.font_size_body - 1)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 4, _pdf_safe(line2), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", self.font_size_body)

    def _bullet(self, pdf, text: str) -> None:
        pdf.set_x(self.margin + 4)
        self._multiline(pdf, "- " + text, indent=4)

    def _multiline(self, pdf, text: str, indent: float = 0) -> None:
        if indent:
            pdf.set_x(self.margin + indent)
        pdf.multi_cell(0, 4, _pdf_safe(text or ""))

    def _multiline_truncate(self, pdf, text: str, max_lines: int = 2, indent: float = 0) -> None:
        if not text:
            return
        safe = _pdf_safe(text)
        max_chars = max(80, max_lines * 50)
        if len(safe) > max_chars:
            safe = safe[: max_chars - 3].rstrip() + "..."
        if indent:
            pdf.set_x(self.margin + indent)
        pdf.multi_cell(0, 4, safe)

    def _date_range(self, start: Optional[str], end: Optional[str], is_present: bool) -> str:
        if not start:
            return ""
        if is_present or not end:
            return f"{start} - Present"
        return f"{start} - {end}"


def build_pdf(
    resume: TailoredResume,
    output: Optional[Union[str, Path]] = None,
    *,
    margin: float = 12.0,
    font_size_body: int = 9,
    font_size_title: int = 16,
    font_size_section: int = 11,
) -> Union[bytes, Path]:
    builder = PDFBuilder(
        font_size_body=font_size_body,
        font_size_title=font_size_title,
        font_size_section=font_size_section,
        margin=margin,
    )
    return builder.build(resume, output=output)