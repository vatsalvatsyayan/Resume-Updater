from google import genai
from fastapi import HTTPException

from core.config import settings

_MODEL_NAME = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Set GEMINI_API_KEY in .env."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text.

    Raises HTTPException(503) if the API key is missing,
    or HTTPException(502) if the Gemini call fails.
    """
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=_MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {exc}"
        ) from exc
