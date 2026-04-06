"""Company research service.

Uses Gemini Deep Research to produce a structured summary of a company
(mission, values, products, recent highlights) suitable for tailoring
cover letters.

All failures are caught and surfaced as None so callers can degrade
gracefully and still generate a cover letter without company research.

# TODO: Add caching keyed by normalized company name (lowercase + stripped)
#       to avoid repeat Deep Research calls for the same company across
#       requests. A TTL of 24 hours is reasonable. Viable options:
#       in-memory dict (simple, lost on restart) or a MongoDB collection
#       with a createdAt TTL index (persistent, shared across workers).
"""

import time

from google import genai

from core.config import settings

_AGENT = "deep-research-pro-preview-12-2025"
_POLL_INTERVAL_SECONDS = 10
_MAX_WAIT_SECONDS = 300  # 5-minute ceiling


def _deep_research(company_name: str, role: str | None = None) -> str | None:
    """Run a Gemini Deep Research interaction for the given company and role.

    When a role is provided, the Products/Services and Recent Highlights
    sections are focused on areas relevant to that role.

    Returns a structured plain-text summary on success, or None on failure.
    """
    if not settings.GEMINI_API_KEY:
        return None

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    role_context = (
        f' A candidate is applying for the role of "{role}" at this company.'
        " For the Products/Services and Recent Highlights sections, prioritize"
        f" information most relevant to a {role} role."
    ) if role else ""

    prompt = f"""Research the company "{company_name}" from publicly available sources.{role_context}

Format the output as plain text with exactly these labeled sections
(skip any section where no information is found):

Mission: 1-3 concise bullet points on the company's mission or purpose.
Values: 1-3 concise bullet points on core values or culture.
Products/Services related to role {role}: 1-3 concise bullet points on key products or services most relevant to the role above.
Recent Highlights related to role {role}: 1-3 concise bullet points on recent news, initiatives, or milestones most relevant to the role above.

Only include information that is explicitly supported by your sources.
Do not invent or assume anything."""

    try:
        interaction = client.interactions.create(
            input=prompt,
            agent=_AGENT,
            background=True,
        )
    except Exception:
        return None

    elapsed = 0
    while elapsed < _MAX_WAIT_SECONDS:
        try:
            interaction = client.interactions.get(interaction.id)
        except Exception:
            return None

        if interaction.status == "completed":
            outputs = interaction.outputs
            if outputs:
                return outputs[-1].text
            return None
        elif interaction.status == "failed":
            return None

        time.sleep(_POLL_INTERVAL_SECONDS)
        elapsed += _POLL_INTERVAL_SECONDS

    return None  # timed out


def research(company_name: str, role: str | None = None) -> str | None:
    """Return a structured plain-text summary of the company via Deep Research.

    When role is provided, Products/Services and Recent Highlights are focused
    on areas most relevant to that role.

    Returns None if the API key is missing, the interaction fails, or the
    request times out. Callers must handle None gracefully.
    """
    try:
        return _deep_research(company_name, role=role)
    except Exception:
        return None
