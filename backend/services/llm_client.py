from google import genai
from fastapi import HTTPException

from core.config import settings


def _get_client() -> genai.Client:
    api_key = settings.effective_google_api_key
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env."
        )
    return genai.Client(api_key=api_key)


def generate(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text.

    Raises HTTPException(503) if the API key is missing,
    or HTTPException(502) if the Gemini call fails.
    """
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=settings.RESUME_LLM_MODEL,
            contents=prompt,
        )
        if not response.text or not str(response.text).strip():
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response. Try again or adjust your input.",
            )
        return str(response.text).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {exc}"
        ) from exc
