import re
from collections import Counter

STOP_WORDS = {
    "what", "is", "the", "a", "an", "of", "in", "to", "and", "how", "does", "do",
    "explain", "tell", "me", "about", "for", "with", "from", "this", "that", "are",
    "was", "were", "can", "you", "why", "which", "when", "where", "who", "give",
    "describe", "define", "please", "between", "difference", "on", "it", "its", "be",
}


def _stem(word: str) -> str:
    """Very light stemmer so 'effects' matches 'effect', 'causing' matches 'cause'."""
    for suffix in ("ing", "ed", "es", "s", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            if suffix == "s" and word.endswith("ss"):
                continue
            return word[: -len(suffix)]
    return word


def _tokens(text: str):
    return [_stem(w) for w in re.findall(r"\w+", text.lower())]


def search_chunks(question, chunks, top_k=4):
    """Keyword baseline with light stemming. Upgrade to embeddings for semantic retrieval."""
    terms = {
        _stem(w)
        for w in re.findall(r"\w+", question.lower())
        if len(w) > 1 and w not in STOP_WORDS
    }
    if not terms:
        return []

    scored = []
    for chunk in chunks:
        counts = Counter(_tokens(chunk["text"]))
        overlap = sum(1 for t in terms if t in counts)
        if overlap == 0:
            continue
        frequency = sum(counts[t] for t in terms)
        score = overlap + 0.05 * min(frequency, 20)
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
