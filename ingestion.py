import pymupdf


def _split_long(text: str, max_chars: int):
    """Hard-split a single very long line so no chunk wildly exceeds max_chars."""
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


def extract_pdf_chunks(pdf_bytes: bytes, filename: str, max_chars: int = 1200):
    """Extract text page-by-page and split it while preserving source metadata."""
    chunks = []
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    try:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text:
                continue

            pieces = []
            for line in (p.strip() for p in text.split("\n") if p.strip()):
                pieces.extend(_split_long(line, max_chars) if len(line) > max_chars else [line])

            current = ""
            for piece in pieces:
                if current and len(current) + len(piece) + 1 > max_chars:
                    chunks.append({"text": current, "source": filename, "page": page_number})
                    current = piece
                else:
                    current = f"{current}\n{piece}".strip()

            if current:
                chunks.append({"text": current, "source": filename, "page": page_number})
    finally:
        doc.close()

    return chunks
