"""Normalize dates from resume-import LLM output for HTML date inputs (YYYY-MM-DD).

This is best-effort: resumes and LLMs emit inconsistent formats. We normalize common
cases; exotic calendars or ambiguous strings may still fail and stay blank in the UI.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.profile_import import ImportedProfileData

_PRESENT_EXACT = frozenset(
    {
        "present",
        "current",
        "now",
        "ongoing",
        "today",
        "tbd",
    }
)

_MONTH_NAME_TO_NUM: dict[str, int] = {
    **{
        n: i
        for i, n in enumerate(
            (
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ),
            start=1,
        )
    },
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

# strptime formats common on resumes (US + EU order tried; ambiguous dates may mis-parse)
_STRPTIME_FORMATS = (
    "%Y-%m-%d",
    "%b %Y",
    "%B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%d %B %Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%m.%d.%Y",
    "%Y.%m.%d",
    "%d-%b-%Y",
    "%d-%B-%Y",
    "%d-%m-%Y",
    "%m-%Y",
    "%m/%Y",
)


def is_present_like(value: object) -> bool:
    """True if the value clearly means an ongoing role (not e.g. 'representative')."""
    if value is None:
        return False
    s = str(value).strip().lower()
    if not s:
        return False
    if s in _PRESENT_EXACT:
        return True
    if re.fullmatch(r"(present|current|now|ongoing)", s):
        return True
    if re.search(r"(?i)(^|\s)(present|now)(\s|$)", s):
        return True
    if re.search(r"(?i)\bto\s+present\b", s):
        return True
    if re.search(r"(?i)[\-–—]\s*present\b", s):
        return True
    return False


def coerce_date_scalar(value: object) -> str | None:
    """Ensure JSON numbers become strings before parsing (LLMs often emit years as ints)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value != int(value):
            return str(value).strip()
        y = int(value)
        if 1900 <= y <= 2100:
            return str(y)
        return str(value).strip()
    if isinstance(value, str):
        s = value.strip()
        return s or None
    return str(value).strip()


def try_split_range(value: object) -> tuple[str | None, str | None]:
    """If the LLM put a full range in one field, return (start, end) pieces."""
    raw = coerce_date_scalar(value)
    if not raw:
        return None, None
    s = raw.strip()

    # Two calendar years only: 2020–2022 / 2020-2022 (avoid splitting ISO dates)
    m = re.fullmatch(r"(\d{4})\s*[\u2013\u2014\-]\s*(\d{4})", s)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        if 1900 <= y1 <= 2100 and 1900 <= y2 <= 2100:
            return m.group(1), m.group(2)

    parts_to = re.split(r"\s+to\s+", s, maxsplit=1, flags=re.I)
    if len(parts_to) == 2 and parts_to[0].strip() and parts_to[1].strip():
        return parts_to[0].strip(), parts_to[1].strip()

    # Split on natural range separators (multi-char first to avoid breaking "Jan 2020")
    for sep in (" – ", " — ", " - ", "\u2013", "\u2014"):
        if sep in s:
            parts = [p.strip() for p in s.split(sep, 1)]
            if len(parts) == 2 and parts[0] and parts[1]:
                return parts[0], parts[1]

    # Last resort: single ASCII hyphen between non-ISO fragments (e.g. Jan 2020-Jun 2022)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return None, None
    if s.count("-") == 1 and not re.match(r"^\d{4}-\d{2}", s):
        parts = [p.strip() for p in s.split("-", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]

    return None, None


def unwrap_range_fields(start_raw: object, end_raw: object) -> tuple[object, object]:
    """If only one side is filled but it contains a range, split into start/end."""
    start_s = coerce_date_scalar(start_raw)
    end_s = coerce_date_scalar(end_raw)
    if end_s:
        return start_raw, end_raw
    left, right = try_split_range(start_raw)
    if left and right:
        return left, right
    if not start_s:
        left, right = try_split_range(end_raw)
        if left and right:
            return left, right
    return start_raw, end_raw


def normalize_import_date(value: object) -> str | None:
    """Best-effort single date -> YYYY-MM-DD. Returns None if empty or unparsable."""
    raw = coerce_date_scalar(value)
    if raw is None:
        return None
    if is_present_like(raw):
        return None

    s = raw.strip()

    # YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s

    # YYYY-MM -> first of month
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12 and 1900 <= y <= 2100:
            return f"{y:04d}-{mo:02d}-01"

    # Year only
    if re.fullmatch(r"\d{4}", s):
        y = int(s)
        if 1900 <= y <= 2100:
            return f"{y:04d}-01-01"

    # MM/YYYY or M/YYYY (interpret as month in known year)
    m = re.fullmatch(r"(\d{1,2})[\/\-](\d{4})", s)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12 and 1900 <= y <= 2100:
            return f"{y:04d}-{mo:02d}-01"

    # YYYY/MM or YYYY/MM/DD
    m = re.fullmatch(r"(\d{4})[\/\.\-](\d{1,2})(?:[\/\.\-](\d{1,2}))?", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        day = int(m.group(3)) if m.group(3) else 1
        if 1 <= mo <= 12 and 1 <= day <= 31 and 1900 <= y <= 2100:
            return f"{y:04d}-{mo:02d}-{day:02d}"

    # Month name + year: Jan 2020, January 2020
    m = re.match(
        r"(?i)^(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+(\d{4})$",
        s,
    )
    if m:
        month_key = m.group(1).lower()[:3]
        month_num = _MONTH_NAME_TO_NUM.get(month_key)
        y = int(m.group(2))
        if month_num and 1900 <= y <= 2100:
            return f"{y:04d}-{month_num:02d}-01"

    for fmt in _STRPTIME_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def finalize_range_dates(
    start_raw: object,
    end_raw: object,
    is_present_flag: bool,
) -> tuple[str | None, str | None, bool]:
    """Normalize start/end; detect Present end and set isPresent."""
    sr, er = unwrap_range_fields(start_raw, end_raw)
    present = bool(is_present_flag) or is_present_like(er)
    start = normalize_import_date(sr)

    if present:
        return start, None, True

    end = normalize_import_date(er)
    return start, end, False


def normalize_imported_profile(data: ImportedProfileData) -> ImportedProfileData:
    """Normalize all date fields to YYYY-MM-DD so the frontend date inputs can display them."""
    education = []
    for e in data.education:
        s, en, pr = finalize_range_dates(e.startDate, e.endDate, e.isPresent)
        education.append(e.model_copy(update={"startDate": s, "endDate": en, "isPresent": pr}))

    work_xp = []
    for w in data.workExperience:
        s, en, pr = finalize_range_dates(w.startDate, w.endDate, w.isPresent)
        work_xp.append(w.model_copy(update={"startDate": s, "endDate": en, "isPresent": pr}))

    volunteer = []
    for v in data.volunteer:
        s, en, pr = finalize_range_dates(v.startDate, v.endDate, v.isPresent)
        volunteer.append(v.model_copy(update={"startDate": s, "endDate": en, "isPresent": pr}))

    leadership = []
    for le in data.leadership:
        s, en, pr = finalize_range_dates(le.startDate, le.endDate, le.isPresent)
        leadership.append(le.model_copy(update={"startDate": s, "endDate": en, "isPresent": pr}))

    certs = []
    for c in data.certifications:
        certs.append(
            c.model_copy(
                update={
                    "issueDate": normalize_import_date(c.issueDate),
                    "expiryDate": normalize_import_date(c.expiryDate),
                }
            )
        )

    return data.model_copy(
        update={
            "education": education,
            "workExperience": work_xp,
            "volunteer": volunteer,
            "leadership": leadership,
            "certifications": certs,
        }
    )
