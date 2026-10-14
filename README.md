# StudyMate AI — Track D starter

A beginner-friendly Streamlit prototype for a source-grounded AI tutor.

## Features in this starter
- Upload and extract text from a PDF while preserving page numbers.
- Search relevant passages using a simple keyword baseline.
- Ask questions with an LLM tutor and view retrieved source passages.
- Generate topic-based MCQ quizzes.
- Store quiz attempts and a basic per-topic mastery estimate in SQLite.

## Requirements
- Python 3.10+
- An internet connection for Gemini API calls
- A Gemini API key with model access and available quota

## Windows setup (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in a text editor and replace the placeholder with your API key.
Never upload `.env` or share the key in screenshots.

Run:

```powershell
streamlit run app.py
```

## Important limitations
- Keyword search is not semantic retrieval. Replace it with embeddings + FAISS when the core app works.
- Text extraction does not OCR scanned pages.
- This version handles PDFs only; slide and video ingestion are follow-up tasks.
- Model-generated citations and answer keys require validation against the original material.
- The mastery estimate is a simple heuristic, not a validated educational measurement model.
- SQLite data is local to this machine and prototype; it is not a multi-user production database.

## Suggested next steps
1. Build a labelled test set with known answers and page references.
2. Validate citations and quiz answer keys.
3. Add semantic retrieval using embeddings.
4. Add PPTX extraction and timestamped lecture transcripts.
5. Add quiz history and question deduplication.
6. Report real evaluation metrics; do not invent benchmark results.

## Setup note
Make sure the hidden files are named `.env.example` and `.gitignore` (with the leading dot).
Copy `.env.example` to `.env` and paste your own key there. Never commit `.env`.

## Evaluate retrieval
Edit `TEST_CASES` in `evaluation.py`, then run: `python evaluation.py your.pdf`
