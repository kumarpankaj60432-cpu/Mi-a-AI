"""Single place that reads the Gemini API key and builds the client."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PLACEHOLDERS = {"", "your_api_key_here", "paste_your_key_here", "changeme"}


def get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()


def get_api_key() -> str:
    key = (os.getenv("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
    if key.lower() in PLACEHOLDERS:
        raise ValueError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env, paste your own key, "
            "and restart the app."
        )
    return key


def has_api_key() -> bool:
    try:
        get_api_key()
        return True
    except ValueError:
        return False


def get_client():
    return genai.Client(api_key=get_api_key())


def redact(text: str) -> str:
    """Remove the key from any error text before showing it on screen."""
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    return text.replace(key, "***") if key else text


def _is_temporary(exc: Exception) -> bool:
    msg = str(exc).upper()
    return any(t in msg for t in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "DEADLINE"))


def generate_text(prompt: str, retries: int = 3) -> str:
    """Call Gemini, retrying temporary overload errors with increasing waits.

    If the main model stays busy, GEMINI_FALLBACK_MODELS (comma-separated) are tried in order.
    """
    import time

    client = get_client()  # keep a reference so the client is not closed early
    models = [get_model()]
    # Backups tried automatically if the main model stays overloaded (override in .env)
    fallbacks = os.getenv("GEMINI_FALLBACK_MODELS", "gemini-3.5-flash,gemini-3.5-flash-lite")
    for name in fallbacks.split(","):
        name = name.strip()
        if name and name not in models:
            models.append(name)

    last_exc = None
    for model in models:
        for attempt in range(retries):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return (getattr(response, "text", None) or "").strip()
            except Exception as exc:
                last_exc = exc
                if not _is_temporary(exc):
                    raise
                time.sleep(2 * (2 ** attempt))  # 2s, 4s, 8s, 16s
    raise last_exc


def explain_error(exc: Exception) -> str:
    """Short, human-friendly explanation for the most common API failures."""
    msg = str(exc).upper()
    if "503" in msg or "UNAVAILABLE" in msg:
        return "Google's Gemini servers are busy right now. Wait a minute and click again."
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return "You've hit the Gemini rate/quota limit. Wait a bit or check your usage in Google AI Studio."
    if "404" in msg or "NOT_FOUND" in msg:
        return "That model name isn't available. Update GEMINI_MODEL in .env (e.g. gemini-3.8-flash)."
    if "API KEY" in msg or "401" in msg or "403" in msg or "PERMISSION" in msg or "INVALID_ARGUMENT" in msg:
        return "The API key was rejected. Check GEMINI_API_KEY in .env and restart the app."
    return "The AI request failed. Details below."
