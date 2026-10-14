"""Manual retrieval evaluation.

1. Fill TEST_CASES with questions whose answer page you know.
2. Run:  python evaluation.py path/to/your.pdf
It reports real retrieval hit-rate only (no LLM calls). Do not invent results.
"""
import sys
from pathlib import Path

from ingestion import extract_pdf_chunks
from retrieval import search_chunks

TEST_CASES = [
    {
        "question": "Write a question whose answer is clearly present in your PDF.",
        "expected_source": "your_file.pdf, page 1",   # must match the PDF file name
        "expected_answer_keywords": ["replace", "these", "keywords"],
    },
    {
        "question": "Ask something not covered by the uploaded PDF.",
        "expected_source": None,
        "expected_answer_keywords": [],
    },
]


def report_retrieval_hit(retrieved_chunks, expected_source):
    if expected_source is None:
        return None
    return any(
        f"{chunk['source']}, page {chunk['page']}" == expected_source
        for chunk in retrieved_chunks
    )


def run(pdf_path, top_k=4):
    path = Path(pdf_path)
    chunks = extract_pdf_chunks(path.read_bytes(), path.name)
    hits = total = 0
    for case in TEST_CASES:
        retrieved = search_chunks(case["question"], chunks, top_k=top_k)
        hit = report_retrieval_hit(retrieved, case["expected_source"])
        if hit is None:
            print(f"[no-answer case] retrieved {len(retrieved)} chunks :: {case['question'][:60]}")
            continue
        total += 1
        hits += int(hit)
        print(f"[{'HIT ' if hit else 'MISS'}] {case['question'][:70]}")
    if total:
        print(f"\nRetrieval hit-rate @ {top_k}: {hits}/{total} = {hits / total:.0%}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python evaluation.py path/to/file.pdf")
    run(sys.argv[1])
