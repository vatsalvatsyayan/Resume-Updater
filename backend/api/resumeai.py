# backend/services/resume_ai.py
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
from dateutil import parser as dtparser


STOPWORDS = {
    "the","and","a","an","to","of","in","for","on","with","as","at","by","from","is","are",
    "this","that","it","be","or","was","were","will","would","should","can","could","may"
}

ACTION_VERBS = [
    "Built", "Designed", "Implemented", "Optimized", "Automated", "Led", "Developed",
    "Improved", "Accelerated", "Reduced", "Delivered", "Owned", "Streamlined"
]


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    parts = [p.strip() for p in text.split() if p.strip()]
    return [p for p in parts if p not in STOPWORDS and len(p) > 2]


def extract_keywords(job_description: str, top_k: int = 35) -> List[str]:
    toks = _tokenize(job_description)
    freq: Dict[str, int] = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, _ in ranked[:top_k]]


def score_text(text: str, keywords: List[str]) -> int:
    t = " " + (text or "").lower() + " "
    score = 0
    for kw in keywords:
        if kw in t:
            score += 2
    return score


def _parse_date_safe(s: str | None) -> float:
    """
    Returns a sortable timestamp (bigger => more recent).
    Supports 'Sept 2023', '2023-09-01', etc.
    If missing, returns 0.
    """
    if not s:
        return 0.0
    try:
        dt = dtparser.parse(s, fuzzy=True, default=dtparser.parse("2000-01-01"))
        return dt.timestamp()
    except Exception:
        return 0.0


def sort_experience_latest_first(work_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key_fn(x: Dict[str, Any]) -> Tuple[float, float]:
        # Prefer "isPresent" as most recent
        is_present = 1 if x.get("isPresent") else 0
        end_ts = _parse_date_safe(x.get("endDate"))
        start_ts = _parse_date_safe(x.get("startDate"))
        # Present first, then most recent end date, then most recent start date
        return (is_present, end_ts, start_ts)

    return sorted(work_experience or [], key=key_fn, reverse=True)


def _split_into_clauses(raw: str) -> List[str]:
    """
    Users may paste paragraphs or dotted bullets.
    We normalize into clean clauses.
    """
    if not raw:
        return []
    text = raw.replace("•", ". ")
    text = re.sub(r"\s+", " ", text).strip()
    # split by sentence-like boundaries
    parts = re.split(r"(?<=[.?!])\s+", text)
    out = []
    for p in parts:
        p = p.strip(" -•\t\r\n")
        if len(p) < 6:
            continue
        out.append(p)
    return out[:12]


def rewrite_to_star_bullets(raw: str, keywords: List[str], max_bullets: int = 3) -> List[str]:
    """
    Turn raw paragraph into STAR-like bullets:
    - Start with action verb
    - Include skill/keyword if relevant
    - Include measurable impact if present
    """
    clauses = _split_into_clauses(raw)
    bullets: List[str] = []

    for i, c in enumerate(clauses):
        c_low = c.lower()

        # Try to inject a relevant keyword (only if it appears naturally)
        matched = [kw for kw in keywords if kw in c_low][:2]

        verb = ACTION_VERBS[i % len(ACTION_VERBS)]
        # Light cleanup
        c2 = c[0].lower() + c[1:] if len(c) > 1 else c
        c2 = re.sub(r"\b(i|we)\b", "", c2, flags=re.I)
        c2 = re.sub(r"\s+", " ", c2).strip()

        # STAR-ish framing
        # Situation/Task implied; focus on Action + Result
        suffix = ""
        if matched:
            suffix = f" (aligned with {', '.join(matched)})"

        bullet = f"{verb} {c2}"
        bullet = bullet.rstrip(".") + f".{suffix}"

        bullets.append(bullet)

        if len(bullets) >= max_bullets:
            break

    # fallback if empty
    if not bullets and raw:
        bullets = [f"Delivered impact in a fast-paced environment aligned with role priorities."]

    return bullets


def build_resume_json(profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Output is ordered to match a normal resume:
    Summary -> Education -> Experience -> Projects -> Skills -> (optional extras)
    """
    keywords = extract_keywords(job_description)

    personal = profile.get("personalInfo") or {}
    education = profile.get("education") or []
    work = sort_experience_latest_first(profile.get("workExperience") or [])
    projects = profile.get("projects") or []
    skills = profile.get("skills") or {}
    certs = profile.get("certifications") or []
    leadership = profile.get("leadership") or []
    volunteer = profile.get("volunteer") or []

    # Summary (use existing text if available, otherwise generate a clean one)
    base_summary = (work[0].get("summary") if work else None) or ""
    if not base_summary:
        headline_bits = []
        if skills.get("programmingLanguages"):
            headline_bits.append(", ".join(skills["programmingLanguages"][:3]))
        if skills.get("databases"):
            headline_bits.append(", ".join(skills["databases"][:2]))
        headline = " • ".join([b for b in headline_bits if b]) or "Software / Data professional"
        base_summary = f"{headline} with a track record of shipping reliable solutions and communicating clearly with cross-functional teams."

    summary = base_summary.strip()

    # Experience selection + rewriting
    exp_out = []
    for w in work:
        combined_text = " ".join([w.get("summary") or "", w.get("description") or ""]).strip()
        s = score_text(combined_text, keywords)
        exp_out.append({
            "companyName": w.get("companyName"),
            "position": w.get("position"),
            "location": w.get("location"),
            "startDate": w.get("startDate"),
            "endDate": w.get("endDate"),
            "isPresent": bool(w.get("isPresent")),
            "score": s,
            "bullets": rewrite_to_star_bullets(w.get("description") or w.get("summary") or "", keywords, max_bullets=3),
        })

    # Sort experiences by relevance score but keep recency as tie-breaker (already sorted by recency earlier)
    exp_out = sorted(exp_out, key=lambda x: x["score"], reverse=True)[:4]
    # Then re-sort those selected experiences by latest-first for “normal resume feel”
    # (We can’t reuse original objects easily; so we use date parse again)
    exp_out = sorted(
        exp_out,
        key=lambda x: (1 if x["isPresent"] else 0, _parse_date_safe(x.get("endDate")), _parse_date_safe(x.get("startDate"))),
        reverse=True
    )

    # Projects rewriting + ranking
    proj_out = []
    for p in projects:
        combined_text = " ".join([p.get("summary") or "", p.get("description") or "", " ".join(p.get("techStack") or [])]).strip()
        s = score_text(combined_text, keywords)
        proj_out.append({
            "projectName": p.get("projectName"),
            "link": p.get("link"),
            "techStack": p.get("techStack") or [],
            "score": s,
            "bullets": rewrite_to_star_bullets(p.get("description") or p.get("summary") or "", keywords, max_bullets=2),
        })
    proj_out = sorted(proj_out, key=lambda x: x["score"], reverse=True)[:3]

    # Skills (keep concise for 1 page)
    skills_out = {
        "programmingLanguages": (skills.get("programmingLanguages") or [])[:8],
        "frameworks": (skills.get("frameworks") or [])[:8],
        "databases": (skills.get("databases") or [])[:8],
        "tools": (skills.get("tools") or [])[:10] if isinstance(skills.get("tools"), list) else [],
    }

    resume = {
        "header": {
            "name": personal.get("name"),
            "email": personal.get("email"),
            "location": personal.get("location"),  # optional if your form has it
            "linkedin": personal.get("linkedinUrl"),
            "github": personal.get("githubUrl"),
            "portfolio": personal.get("portfolioWebsite"),
        },
        "sections": [
            {"title": "SUMMARY", "content": {"paragraph": summary}},
            {"title": "EDUCATION", "content": {"items": education}},
            {"title": "EXPERIENCE", "content": {"items": exp_out}},
            {"title": "PROJECTS", "content": {"items": proj_out}},
            {"title": "SKILLS", "content": skills_out},
        ],
    }

    # Optional sections (only if present; PDF renderer will include only if space permits)
    if certs:
        resume["sections"].append({"title": "CERTIFICATIONS", "content": {"items": certs[:5]}})
    if leadership:
        resume["sections"].append({"title": "LEADERSHIP", "content": {"items": leadership[:2]}})
    if volunteer:
        resume["sections"].append({"title": "VOLUNTEER", "content": {"items": volunteer[:2]}})

    return resume