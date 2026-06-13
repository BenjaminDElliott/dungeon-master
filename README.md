# Dungeon Master — LLM Text RPG

A browser-based, single-player text RPG where an LLM acts as the dungeon master.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Database:** SQLite
- **LLM Provider:** OpenRouter
- **Frontend:** Browser (to be built in later tasks)

## Quick Start

### Prerequisites

- Python 3.11 or later
- pip (Python package installer)

### Setup

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Copy and edit the environment file
cp .env.example .env
# Edit .env to add your OPENROUTER_API_KEY

# 4. Run the development server
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`. Visit `/docs` for the auto-generated API documentation.

### Running Tests

```bash
pytest tests/ -v
```

### Framework Decision: FastAPI

FastAPI was chosen over Flask because:

1. **Native WebSocket support** — essential for real-time LLM streaming to the browser
2. **Pydantic validation** — built-in request/response schemas
3. **Auto-generated API docs** — `/docs` endpoint out of the box
4. **Async-first** — matches the LLM API usage pattern perfectly
5. **Type inference** — better IDE/LSP support

## Project Structure

```
.
├── app/
│   ├── __init__.py      # Package marker
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Pydantic Settings
│   └── logging_setup.py # Logging configuration
├── tests/
│   ├── __init__.py
│   └── test_app.py      # Smoke tests
├── pyproject.toml       # Dependencies & tool config
├── .env.example         # Environment variables template
├── .gitignore
└── README.md
```

## Development

- **Lint:** `ruff check .`
- **Format:** `ruff format .`
- **Test:** `pytest tests/ -v`

## License

Private — LatentSpaceLabs
