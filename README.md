# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Project Overview

This repository contains coursework organized by week. The main application is the **Action Item Extractor** (Week 2), which turns free-form meeting notes into a checklist of action items.

### Action Item Extractor (Week 2)

- **Purpose:** Extract actionable tasks from unstructured text (meeting notes, bullet lists, etc.).
- **Stack:** FastAPI, SQLite, Pydantic, Ollama (LLM).
- **Features:**
  - **Heuristic extraction:** Pattern-based extraction for bullets (`-`, `*`, `•`), checkboxes (`- [ ]`), numbered lists, and keywords (`todo:`, `action:`, `next:`).
  - **LLM extraction:** Uses [Ollama](https://ollama.ai) for intelligent extraction from natural language.
  - Notes and action items persist in SQLite; items can be marked done/undone.
  - Simple web UI for paste, extract, and manage.

---

## Repo Setup

These steps work with Python 3.12.

1. **Install Anaconda**
   - Download and install: [Anaconda Individual Edition](https://www.anaconda.com/download)
   - Open a new terminal so `conda` is on your `PATH`.

2. **Create and activate a Conda environment (Python 3.12)**
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. **Install project dependencies with Poetry** (inside the activated Conda env)
   ```bash
   poetry install --no-interaction
   ```

---

## How to Run the Application

From the repository root with the Conda environment activated:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Then open:

- **Web UI:** http://127.0.0.1:8000/
- **Interactive API docs:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Optional: LLM Extraction

For LLM-based extraction (`/action-items/extract-llm`):

1. Install and run [Ollama](https://ollama.ai).
2. Pull a model, e.g.: `ollama pull llama3.1:8b`
3. The app uses this model automatically; if the LLM fails, it falls back to heuristic extraction.

### Environment Variables

| Variable      | Description                                      | Default                |
|---------------|--------------------------------------------------|------------------------|
| `APP_DB_PATH` | Path to SQLite database file                     | `week2/data/app.db`    |
| `APP_DEBUG`   | Enable debug mode (`1`, `true`, or `yes`)        | `false`                |

---

## API Endpoints and Functionality

### Root & Static

| Method | Path   | Description                          |
|--------|--------|--------------------------------------|
| GET    | `/`    | Serves the frontend `index.html`     |
| GET    | `/static/*` | Static assets for the frontend  |

### Notes (`/notes`)

| Method | Path        | Description                |
|--------|-------------|----------------------------|
| GET    | `/notes`    | List all notes             |
| POST   | `/notes`    | Create a note              |
| GET    | `/notes/{note_id}` | Get a note by ID   |

**Create note request body:**
```json
{
  "content": "Meeting notes text..."
}
```

### Action Items (`/action-items`)

| Method | Path                           | Description                                      |
|--------|--------------------------------|--------------------------------------------------|
| POST   | `/action-items/extract`        | Extract action items via heuristics              |
| POST   | `/action-items/extract-llm`    | Extract action items via LLM (Ollama)            |
| GET    | `/action-items`                | List all action items (optional: `?note_id=`)    |
| POST   | `/action-items/{id}/done`      | Mark an action item done or undone               |

**Extract request body:**
```json
{
  "text": "Notes with action items...",
  "save_note": false
}
```

**Mark done request body:**
```json
{
  "done": true
}
```

**Extract response:**
```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "Write tests" }
  ]
}
```

---

## Running the Test Suite

From the repository root:

```bash
poetry run pytest week2/tests -v
```

Or with the Poetry/Conda env active:

```bash
pytest week2/tests -v
```

### Test Coverage

- **`week2/tests/test_extract.py`** – Unit tests for action item extraction:
  - Heuristic extraction (bullets, checkboxes, numbered lists)
  - LLM extraction (mocked) for bullet lists, keyword-prefixed items, numbered lists
  - Empty input handling
  - Fallback to heuristics on LLM errors or malformed JSON

Tests use `unittest.mock.patch` to mock Ollama calls, so no running Ollama instance is needed for tests.
