"""Run:  python check_key.py   -- verifies your .env and API key work."""
from config import generate_text, get_model, get_api_key, redact

try:
    key = get_api_key()
    print(f"Key found: {key[:4]}...{key[-3:]} ({len(key)} chars), model: {get_model()}")
    reply = generate_text("Reply with the single word: OK")
    print("API call succeeded ->", reply)
except Exception as exc:
    print("FAILED:", redact(str(exc)))
    print("\nCommon causes: wrong/revoked key, no quota, wrong GEMINI_MODEL, no internet.")
