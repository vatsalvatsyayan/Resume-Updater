"""Company research service.

Discovers a company's About page via DuckDuckGo search, scrapes its visible
text, and uses Gemini to produce a structured summary (mission, values,
products, recent highlights).

All failures are caught and surfaced as None so callers can degrade gracefully
and still generate a cover letter without company research.

# TODO: Add caching keyed by normalized company name (lowercase + stripped) to
#       avoid repeat DuckDuckGo searches + scrape + Gemini calls for the same
#       company across requests. A TTL of 24 hours is reasonable. Viable
#       options: in-memory dict (simple, lost on restart) or a MongoDB
#       collection with a createdAt TTL index (persistent, shared across
#       workers).
"""

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from services import llm_client

_MAX_SCRAPED_CHARS = 3000


def _find_about_url(company_name: str) -> str | None:
    """Search DuckDuckGo for the company's About page and return the best URL.

    Prefers URLs that contain 'about' in the path; falls back to the first
    search result if none do. Returns None if the search itself fails.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                f"{company_name} official about us",
                max_results=5,
            ))
        for r in results:
            url = r.get("href", "")
            if "about" in url.lower():
                return url
        return results[0].get("href") if results else None
    except Exception:
        return None


def _scrape_page(url: str) -> str | None:
    """Fetch a URL and return cleaned visible text, capped at _MAX_SCRAPED_CHARS.

    Strips script, style, nav, header, and footer tags before extracting text.
    Returns None if the request fails or the page yields no usable text.
    """
    try:
        response = httpx.get(
            url,
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:_MAX_SCRAPED_CHARS] if text else None
    except Exception:
        return None


def _summarize(company_name: str, raw_text: str) -> str:
    """Call Gemini to extract structured company info from scraped About page text."""
    prompt = f"""You are a research assistant helping a job applicant learn about a company before writing a cover letter.

Below is text scraped from {company_name}'s About page. Extract and summarize the following in 1-3 bullet points per section (skip any section where information is not present in the text):

- Mission / purpose
- Core values or culture
- Key products or services
- Recent highlights or initiatives

Keep each bullet to one concise sentence. Only include information explicitly present in the text — do not invent or assume anything.

## Scraped Text
{raw_text}

## Output Format
Return plain text with labeled sections:
Mission: ...
Values: ...
Products/Services: ...
Recent Highlights: ...
"""
    return llm_client.generate(prompt)


def research(company_name: str) -> str | None:
    """Discover and summarize a company's About page.

    Orchestrates URL discovery → scraping → Gemini summarization.
    Returns a structured plain-text summary on success, or None if any step
    fails. Callers must handle None gracefully (skip the research section in
    the cover letter prompt).
    """
    url = _find_about_url(company_name)
    if not url:
        return None

    raw_text = _scrape_page(url)
    if not raw_text:
        return None

    try:
        return _summarize(company_name, raw_text)
    except Exception:
        return None
