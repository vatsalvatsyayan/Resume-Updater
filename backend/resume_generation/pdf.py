from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .schemas.output_schema import TailoredResume

PAGE_HEIGHT_MM = 297.0
MIN_SECTION_BUFFER_MM = 12.0


def _pdf_safe(text: str) -> str:
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


def _date_range(start: Optional[str], end: Optional[str], is_present: bool) -> str:
    if not start:
        return ""
    if is_present or not end:
        return f"{start} - Present"
    return f"{start} - {end}"


def _has_room(pdf, max_y: float, needed_mm: float) -> bool:
    return (pdf.get_y() + needed_mm) <= max_y


def _write_section(pdf, title: str, font_size_section: int, font_size_body: int) -> None:
    pdf.set_font("Helvetica", "B", font_size_section)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, _pdf_safe(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", font_size_body)


def _write_block_title(pdf, line1: str, line2: Optional[str], font_size_body: int) -> None:
    pdf.set_font("Helvetica", "B", font_size_body)
    pdf.cell(0, 4, _pdf_safe(line1), new_x="LMARGIN", new_y="NEXT")
    if line2:
        pdf.set_font("Helvetica", "", font_size_body - 1)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 4, _pdf_safe(line2), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", font_size_body)


def _write_bullet(pdf, text: str, margin: float) -> None:
    pdf.set_x(margin + 4)
    pdf.multi_cell(0, 4, _pdf_safe("- " + text))


def _write_multiline_truncate(pdf, text: str, max_lines: int, margin: float, indent: float = 0) -> None:
    if not text:
        return
    safe = _pdf_safe(text)
    max_chars = max(80, max_lines * 50)
    if len(safe) > max_chars:
        safe = safe[: max_chars - 3].rstrip() + "..."
    if indent:
        pdf.set_x(margin + indent)
    pdf.multi_cell(0, 4, safe)


def build_pdf(
    resume: TailoredResume,
    output: Optional[Union[str, Path]] = None,
    *,
    margin: float = 12.0,
    font_size_body: int = 9,
    font_size_title: int = 16,
    font_size_section: int = 11,
) -> Union[bytes, Path]:
    try:
        from fpdf import FPDF
    except ImportError as e:
        raise ImportError(
            "fpdf2 is required for PDF generation. Install with: pip install fpdf2"
        ) from e

    max_y = PAGE_HEIGHT_MM - margin
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(margin, margin, margin)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", font_size_title)
    pdf.cell(0, 6, _pdf_safe(resume.name or "Resume"), new_x="LMARGIN", new_y="NEXT")
    contact_parts = [p for p in [resume.email, resume.portfolioWebsite, resume.githubUrl, resume.linkedinUrl] if p]
    if contact_parts:
        pdf.set_font("Helvetica", "", font_size_body - 1)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 5, _pdf_safe(" | ".join(contact_parts)), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    if resume.professionalSummary and _has_room(pdf, max_y, 25):
        _write_section(pdf, "Summary", font_size_section, font_size_body)
        pdf.set_font("Helvetica", "", font_size_body)
        _write_multiline_truncate(pdf, resume.professionalSummary, 3, margin)
        pdf.ln(2)

    if resume.education and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Education", font_size_section, font_size_body)
        for e in resume.education:
            if not _has_room(pdf, max_y, 18):
                break
            _write_block_title(pdf, f"{e.courseName}, {e.major}", e.universityName, font_size_body)
            date_str = _date_range(e.startDate, e.endDate, e.isPresent)
            if date_str:
                pdf.set_font("Helvetica", "", font_size_body - 1)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 4, _pdf_safe(date_str), new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            if e.gpa:
                pdf.cell(0, 4, _pdf_safe(f"GPA: {e.gpa}"), new_x="LMARGIN", new_y="NEXT")
            if e.highlight:
                pdf.set_font("Helvetica", "", font_size_body - 1)
                _write_multiline_truncate(pdf, e.highlight, 1, margin)
            pdf.set_font("Helvetica", "", font_size_body)
            pdf.ln(1)

    if resume.workExperience and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Experience", font_size_section, font_size_body)
        for w in resume.workExperience:
            if not _has_room(pdf, max_y, 20):
                break
            _write_block_title(pdf, w.position, w.companyName, font_size_body)
            date_str = _date_range(w.startDate, w.endDate, w.isPresent)
            if date_str:
                pdf.set_font("Helvetica", "", font_size_body - 1)
                pdf.set_text_color(100, 100, 100)
                line = date_str + (f" | {w.location}" if w.location else "")
                pdf.cell(0, 4, _pdf_safe(line), new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", font_size_body)
            for b in w.bullets:
                if not _has_room(pdf, max_y, 8):
                    break
                _write_bullet(pdf, b, margin)
            pdf.ln(1)

    if resume.projects and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Projects", font_size_section, font_size_body)
        for p in resume.projects:
            if not _has_room(pdf, max_y, 20):
                break
            sub = p.link or ", ".join(p.techStack) if p.techStack else None
            _write_block_title(pdf, p.projectName, sub, font_size_body)
            if p.techStack and p.link:
                pdf.set_font("Helvetica", "", font_size_body - 1)
                pdf.cell(0, 4, _pdf_safe(", ".join(p.techStack)), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", font_size_body)
            for b in p.bullets:
                if not _has_room(pdf, max_y, 8):
                    break
                _write_bullet(pdf, b, margin)
            pdf.ln(1)

    if resume.skills and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Skills", font_size_section, font_size_body)
        pdf.set_font("Helvetica", "", font_size_body)
        _write_multiline_truncate(pdf, ", ".join(resume.skills), 2, margin)
        pdf.ln(2)

    if resume.certifications and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Certifications", font_size_section, font_size_body)
        for c in resume.certifications:
            if not _has_room(pdf, max_y, 10):
                break
            pdf.set_font("Helvetica", "B", font_size_body)
            pdf.cell(0, 4, _pdf_safe(c.name), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", font_size_body - 1)
            pdf.cell(0, 4, _pdf_safe(c.issuingOrganization), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", font_size_body)
            pdf.ln(1)

    if resume.volunteer and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Volunteer", font_size_section, font_size_body)
        for v in resume.volunteer:
            if not _has_room(pdf, max_y, 15):
                break
            _write_block_title(pdf, v.role, v.organizationName, font_size_body)
            for b in v.bullets:
                if not _has_room(pdf, max_y, 6):
                    break
                _write_bullet(pdf, b, margin)
            pdf.ln(1)

    if resume.leadership and _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
        _write_section(pdf, "Leadership", font_size_section, font_size_body)
        for l in resume.leadership:
            if not _has_room(pdf, max_y, 15):
                break
            _write_block_title(pdf, l.title, l.organization, font_size_body)
            for b in l.bullets:
                if not _has_room(pdf, max_y, 6):
                    break
                _write_bullet(pdf, b, margin)
            pdf.ln(1)

    for sec in resume.extraSections:
        if not sec.items or not _has_room(pdf, max_y, MIN_SECTION_BUFFER_MM):
            continue
        _write_section(pdf, sec.title, font_size_section, font_size_body)
        for item in sec.items:
            if not _has_room(pdf, max_y, 6):
                break
            _write_bullet(pdf, item, margin)
        pdf.ln(1)

    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(path)
        return path
    return pdf.output()
