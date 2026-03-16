# Week 2 — Action Item Extractor

A FastAPI + SQLite application that extracts actionable items from freeform text. It supports both a heuristic (regex-based) extractor and an LLM-powered extractor using Ollama, and includes a minimal HTML frontend.

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI app, serves frontend, registers routers
│   ├── db.py                # SQLite database helpers (notes, action items)
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── notes.py         # /notes endpoints
│   │   └── action_items.py  # /action-items endpoints
│   └── services/
│       └── extract.py       # Heuristic + LLM extraction logic
├── frontend/
│   └── index.html           # Single-page HTML frontend
├── data/
│   └── app.db               # SQLite database (created at runtime)
└── tests/
    └── test_extract.py      # Unit tests for extraction functions
```

## Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- [Ollama](https://ollama.com/) running locally with the `llama3.1:8b` model (required only for the LLM extraction endpoint)

### Install Dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
poetry install --no-interaction
```

### Start Ollama (for LLM extraction)

```bash
ollama serve
ollama pull llama3.1:8b
```

## Running the Application

From the repository root:

```bash
source .venv/bin/activate
cd week2
uvicorn week2.app.main:app --reload --port 8000
```

- **Frontend:** http://127.0.0.1:8000/
- **API docs (Swagger):** http://127.0.0.1:8000/docs

The SQLite database (`week2/data/app.db`) is created automatically on first startup.

## API Endpoints

### Notes

| Method | Path             | Description               |
|--------|------------------|---------------------------|
| GET    | `/notes`         | List all notes            |
| POST   | `/notes`         | Create a new note         |
| GET    | `/notes/{id}`    | Get a single note by ID   |

### Action Items

| Method | Path                            | Description                                      |
|--------|---------------------------------|--------------------------------------------------|
| POST   | `/action-items/extract`         | Extract action items using heuristic rules        |
| POST   | `/action-items/extract-llm`     | Extract action items using Ollama LLM             |
| GET    | `/action-items`                 | List all action items (optional `?note_id=` filter) |
| POST   | `/action-items/{id}/done`       | Mark an action item as done/undone                |

### Example Requests

**Heuristic extraction:**

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "- [ ] Set up database\n- Write tests", "save_note": true}'
```

**LLM extraction (requires Ollama):**

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{"text": "We need to fix the login bug and update docs", "save_note": false}'
```

**List notes:**

```bash
curl http://127.0.0.1:8000/notes
```

### Request/Response Schemas

**ExtractRequest** (used by both extract endpoints):
```json
{ "text": "string (required)", "save_note": false }
```

**ExtractResponse:**
```json
{ "note_id": 1, "items": [{ "id": 1, "text": "Set up database" }] }
```

**NoteResponse:**
```json
{ "id": 1, "content": "...", "created_at": "2026-03-16 12:00:00" }
```

## Running Tests

From the repository root with the virtual environment activated:

```bash
PYTHONPATH=week2 pytest week2/tests/test_extract.py -q
```

The test suite covers both the heuristic extractor and the LLM extractor (LLM tests require Ollama to be running with `llama3.1:8b`).

## Tooling

- **Formatter:** `black` (line length 100)
- **Linter:** `ruff`

```bash
black week2/
ruff check week2/
```
