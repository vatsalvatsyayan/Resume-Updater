"""
Resume PDF builder that follows a clean template layout:
- Name + contact with horizontal rule under header
- Section headers in caps with underline
- Role/company with dates right-aligned on same line
- Consistent bullets and spacing
- Prefer 1 page; if overflow try smaller fonts/margins. Never use multiple pages.
- If content is light (lots of white space), spread it out; if heavy, squeeze to fit.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union

from .schemas.output_schema import TailoredResume

log = logging.getLogger(__name__)

PAGE_HEIGHT_MM = 297.0
PAGE_WIDTH_MM = 210.0
MARGIN_MM = 15.0
MARGIN_COMPACT_MM = 10.0
MIN_SECTION_BUFFER_MM = 14.0
MIN_SECTION_BUFFER_COMPACT_MM = 10.0

# Normal font sizes (pt)
FONT_NAME = 14
FONT_CONTACT = 9
FONT_SECTION = 10
FONT_BODY = 9
FONT_SMALL = 8
# Compact font sizes (squeeze to fit)
FONT_NAME_C = 12
FONT_CONTACT_C = 8
FONT_SECTION_C = 9
FONT_BODY_C = 8
FONT_SMALL_C = 7
# Spread font sizes (less content – larger to fill page)
FONT_NAME_S = 18
FONT_CONTACT_S = 11
FONT_SECTION_S = 12
FONT_BODY_S = 11
FONT_SMALL_S = 10


def _content_weight(resume: TailoredResume) -> float:
    """Estimate content volume from resume data. Used to pick spread vs normal vs compact."""
    n_edu = len(resume.education or [])
    n_work = len(resume.workExperience or [])
    n_proj = len(resume.projects or [])
    bullets = sum(len(w.bullets) for w in (resume.workExperience or []))
    bullets += sum(len(p.bullets) for p in (resume.projects or []))
    bullets += sum(len(v.bullets) for v in (resume.volunteer or []))
    bullets += sum(len(l.bullets) for l in (resume.leadership or []))
    for sec in resume.extraSections or []:
        bullets += len(sec.items or [])
    n_skills = len(resume.skills or [])
    n_certs = len(resume.certifications or [])
    n_vol = len(resume.volunteer or [])
    n_lead = len(resume.leadership or [])
    summary_weight = 2 if (resume.professionalSummary and len(resume.professionalSummary) > 50) else 0
    # Heuristic: entries and bullets dominate; skills/certs add a bit
    return (
        n_edu * 4 + n_work * 5 + n_proj * 4
        + bullets * 2.5
        + min(n_skills, 40) * 0.3
        + n_certs * 2 + n_vol * 3 + n_lead * 3
        + summary_weight
    )


def _content_based_layout(resume: TailoredResume) -> str:
    """Return 'spread' | 'normal' | 'compact' based on content weight."""
    w = _content_weight(resume)
    if w < 35:
        return "spread"
    if w > 75:
        return "compact"
    return "normal"


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


def _ensure_room(pdf, max_y: float, needed_mm: float) -> None:
    """If not enough room left on page, add a new page so content is not cut off."""
    if not _has_room(pdf, max_y, needed_mm):
        pdf.add_page()


def _need_room(pdf, max_y: float, needed_mm: float, opts: dict) -> bool:
    """If multi_page: add page when needed. Else: return False and set opts['truncated'] if no room."""
    if opts["multi_page"]:
        _ensure_room(pdf, max_y, needed_mm)
        return True
    if _has_room(pdf, max_y, needed_mm):
        return True
    opts["truncated"] = True
    return False


def _draw_hline(pdf, y: float, x_start: float, x_end: float, gray: int = 200) -> None:
    pdf.set_draw_color(gray, gray, gray)
    pdf.line(x_start, y, x_end, y)
    pdf.set_draw_color(0, 0, 0)


def _write_section_header(pdf, title: str, max_y: float, opts: dict) -> None:
    if not _need_room(pdf, max_y, 12, opts):
        return
    fs, fb = opts["font_section"], opts["font_body"]
    margin = opts["margin"]
    lh_h, lh = opts["lh_header"], opts["lh"]
    pdf.set_font("Helvetica", "B", fs)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, lh_h, _pdf_safe(title.upper()), new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    _draw_hline(pdf, y + 1, margin, PAGE_WIDTH_MM - margin, 180)
    pdf.set_y(y + lh)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", fb)


def _write_block_with_date(
    pdf,
    line1: str,
    line2: Optional[str],
    date_str: str,
    max_y: float,
    opts: dict,
) -> None:
    """Write block title (line1) with optional date right-aligned on same line, then line2 below."""
    if not _need_room(pdf, max_y, 10, opts):
        return
    margin = opts["margin"]
    fb, fsm = opts["font_body"], opts["font_small"]
    lh = opts["lh"]
    pdf.set_font("Helvetica", "B", fb)
    # Same line: line1 left, date right
    if date_str:
        w_left = PAGE_WIDTH_MM - margin * 2 - 38
        pdf.cell(w_left, lh, _pdf_safe(line1))
        pdf.set_font("Helvetica", "", fsm)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, lh, _pdf_safe(date_str), align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", fb)
    else:
        pdf.cell(0, lh, _pdf_safe(line1), new_x="LMARGIN", new_y="NEXT")
    if line2:
        pdf.set_font("Helvetica", "", fsm)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, lh, _pdf_safe(line2), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", fb)


def _write_bullet(pdf, text: str, opts: dict) -> None:
    margin = opts["margin"]
    lh = opts["lh"]
    pdf.set_x(margin + 5)
    pdf.multi_cell(0, lh, _pdf_safe("- " + text))


def build_pdf_template(
    resume: TailoredResume,
    output: Optional[Union[str, Path]] = None,
    *,
    margin: float = MARGIN_MM,
) -> Union[bytes, Path]:
    try:
        from fpdf import FPDF
    except ImportError as e:
        raise ImportError(
            "fpdf2 is required for PDF generation. Install with: pip install fpdf2"
        ) from e

    break_margin = 10  # used when multi_page=True
    min_buf = MIN_SECTION_BUFFER_MM
    min_buf_compact = MIN_SECTION_BUFFER_COMPACT_MM

    def make_opts(margin_use: float, font_name: int, font_contact: int, font_section: int, font_body: int, font_small: int, multi_page: bool, spacing_scale: float = 1.0) -> dict:
        return {
            "margin": margin_use,
            "font_name": font_name,
            "font_contact": font_contact,
            "font_section": font_section,
            "font_body": font_body,
            "font_small": font_small,
            "multi_page": multi_page,
            "truncated": False,
            "spacing_scale": spacing_scale,
            "lh": max(3.0, 4 * spacing_scale),       # line height for body/small
            "lh_header": max(4.0, 5 * spacing_scale), # section header cell height
        }

    def build_one(opts: dict) -> tuple[Any, bool, float]:
        margin_use = opts["margin"]
        scale = opts["spacing_scale"]
        max_y = PAGE_HEIGHT_MM - margin_use - (break_margin if opts["multi_page"] else 0)
        pdf = FPDF(unit="mm", format="A4")
        pdf.set_auto_page_break(auto=opts["multi_page"], margin=break_margin if opts["multi_page"] else 0)
        pdf.set_margins(margin_use, margin_use, margin_use)
        pdf.add_page()

        lh = opts["lh"]
        lh_header = opts["lh_header"]

        # Header
        pdf.set_font("Helvetica", "B", opts["font_name"])
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 6 * scale, _pdf_safe(resume.name or "Resume"), new_x="LMARGIN", new_y="NEXT")
        contact_parts = [p for p in [resume.email, resume.portfolioWebsite, resume.githubUrl, resume.linkedinUrl] if p]
        if contact_parts:
            pdf.set_font("Helvetica", "", opts["font_contact"])
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 5 * scale, _pdf_safe("  |  ".join(contact_parts)), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        y_after_header = pdf.get_y() + 2 * scale
        _draw_hline(pdf, y_after_header, margin_use, PAGE_WIDTH_MM - margin_use)
        pdf.set_y(y_after_header + 5 * scale)

        buf = min_buf if margin_use >= MARGIN_MM else min_buf_compact

        # Summary
        if resume.professionalSummary:
            if not _need_room(pdf, max_y, 22, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Summary", max_y, opts)
            pdf.set_font("Helvetica", "", opts["font_body"])
            safe = _pdf_safe(resume.professionalSummary)
            if len(safe) > 450:
                safe = safe[:447].rstrip() + "..."
            pdf.multi_cell(0, lh, safe)
            pdf.ln(3 * scale)

        # Education
        if resume.education:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Education", max_y, opts)
            for e in resume.education:
                if not _need_room(pdf, max_y, 18, opts):
                    break
                _write_block_with_date(
                    pdf,
                    f"{e.courseName}, {e.major}",
                    e.universityName,
                    _date_range(e.startDate, e.endDate, e.isPresent),
                    max_y,
                    opts,
                )
                if e.gpa:
                    pdf.set_font("Helvetica", "", opts["font_small"])
                    pdf.cell(0, lh, _pdf_safe(f"GPA: {e.gpa}"), new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", opts["font_body"])
                if e.highlight:
                    pdf.set_x(margin_use + 5)
                    pdf.set_font("Helvetica", "", opts["font_small"])
                    pdf.multi_cell(0, lh, _pdf_safe(e.highlight[:200] + ("..." if len(e.highlight) > 200 else "")))
                    pdf.set_font("Helvetica", "", opts["font_body"])
                pdf.ln(2 * scale)

        # Experience
        if resume.workExperience:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Experience", max_y, opts)
            for w in resume.workExperience:
                if not _need_room(pdf, max_y, 20, opts):
                    break
                date_str = _date_range(w.startDate, w.endDate, w.isPresent)
                sub = w.companyName + (f"  |  {w.location}" if w.location else "")
                _write_block_with_date(pdf, w.position, sub, date_str, max_y, opts)
                for b in w.bullets:
                    if not _need_room(pdf, max_y, 8, opts):
                        break
                    _write_bullet(pdf, b, opts)
                pdf.ln(1 * scale)

        # Projects
        if resume.projects:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Projects", max_y, opts)
            for p in resume.projects:
                if not _need_room(pdf, max_y, 20, opts):
                    break
                sub = p.link or (", ".join(p.techStack) if p.techStack else None)
                if p.link and p.techStack:
                    sub = f"{p.link}  |  {', '.join(p.techStack)}"
                _write_block_with_date(pdf, p.projectName, sub, "", max_y, opts)
                for b in p.bullets:
                    if not _need_room(pdf, max_y, 8, opts):
                        break
                    _write_bullet(pdf, b, opts)
                pdf.ln(1 * scale)

        # Skills
        if resume.skills:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Skills", max_y, opts)
            pdf.set_font("Helvetica", "", opts["font_body"])
            pdf.multi_cell(0, lh, _pdf_safe(", ".join(resume.skills)))
            pdf.ln(3 * scale)

        # Certifications
        if resume.certifications:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Certifications", max_y, opts)
            for c in resume.certifications:
                if not _need_room(pdf, max_y, 10, opts):
                    break
                pdf.set_font("Helvetica", "B", opts["font_body"])
                pdf.cell(0, lh, _pdf_safe(c.name), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", opts["font_small"])
                pdf.set_text_color(80, 80, 80)
                pdf.cell(0, lh, _pdf_safe(c.issuingOrganization), new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", opts["font_body"])
                pdf.ln(1 * scale)

        # Volunteer
        if resume.volunteer:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Volunteer", max_y, opts)
            for v in resume.volunteer:
                if not _need_room(pdf, max_y, 15, opts):
                    break
                _write_block_with_date(pdf, v.role, v.organizationName, "", max_y, opts)
                for b in v.bullets:
                    if not _need_room(pdf, max_y, 6, opts):
                        break
                    _write_bullet(pdf, b, opts)
                pdf.ln(1 * scale)

        # Leadership
        if resume.leadership:
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, "Leadership", max_y, opts)
            for l in resume.leadership:
                if not _need_room(pdf, max_y, 15, opts):
                    break
                _write_block_with_date(pdf, l.title, l.organization, "", max_y, opts)
                for b in l.bullets:
                    if not _need_room(pdf, max_y, 6, opts):
                        break
                    _write_bullet(pdf, b, opts)
                pdf.ln(1 * scale)

        # Extra sections
        for sec in resume.extraSections:
            if not sec.items:
                continue
            if not _need_room(pdf, max_y, buf, opts):
                return pdf, opts["truncated"], pdf.get_y()
            _write_section_header(pdf, sec.title, max_y, opts)
            for item in sec.items:
                if not _need_room(pdf, max_y, 6, opts):
                    break
                _write_bullet(pdf, item, opts)
            pdf.ln(1 * scale)

        return pdf, opts["truncated"], pdf.get_y()

    def output_pdf(pdf) -> Union[bytes, Path]:
        if output is not None:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            pdf.output(path)
            return path
        out = pdf.output()
        return bytes(out) if isinstance(out, bytearray) else out

    # Content-based layout: choose spread / normal / compact from resume data
    layout = _content_based_layout(resume)

    if layout == "spread":
        opts = make_opts(MARGIN_MM, FONT_NAME_S, FONT_CONTACT_S, FONT_SECTION_S, FONT_BODY_S, FONT_SMALL_S, multi_page=False, spacing_scale=1.55)
        pdf, _, _ = build_one(opts)
        return output_pdf(pdf)

    if layout == "normal":
        opts_normal = make_opts(MARGIN_MM, FONT_NAME, FONT_CONTACT, FONT_SECTION, FONT_BODY, FONT_SMALL, multi_page=False)
        pdf, truncated, _ = build_one(opts_normal)
        if not truncated:
            return output_pdf(pdf)
        # Overflow: fall back to compact
        opts_compact = make_opts(MARGIN_COMPACT_MM, FONT_NAME_C, FONT_CONTACT_C, FONT_SECTION_C, FONT_BODY_C, FONT_SMALL_C, multi_page=False, spacing_scale=0.95)
        pdf, truncated_compact, _ = build_one(opts_compact)
        if truncated_compact:
            log.warning(
                "Resume content exceeds one page even after re-formatting (reduced margins and fonts). "
                "Some content has been cut off to keep the resume to a single page."
            )
        return output_pdf(pdf)

    # layout == "compact"
    opts_compact = make_opts(MARGIN_COMPACT_MM, FONT_NAME_C, FONT_CONTACT_C, FONT_SECTION_C, FONT_BODY_C, FONT_SMALL_C, multi_page=False, spacing_scale=0.95)
    pdf, truncated_compact, _ = build_one(opts_compact)
    if truncated_compact:
        log.warning(
            "Resume content exceeds one page even after re-formatting (reduced margins and fonts). "
            "Some content has been cut off to keep the resume to a single page."
        )
    return output_pdf(pdf)

