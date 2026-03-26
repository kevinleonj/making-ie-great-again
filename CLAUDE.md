# MakingIEGreatAgain

## Architecture
- **Frontend**: Flet 0.80.5 (Python, runs as web app on port 8550)
- **Backend**: FastAPI (Python, runs on port 8000)
- **Communication**: HTTP (httpx client in frontend calling backend REST API)
- **TTS Engine**: mlx-audio with Qwen3-TTS (local Apple Silicon inference)
- **LLM**: Claude API via anthropic Python SDK

## Commands
```
make install          # Install all deps + playwright browsers
make lint             # ruff check + format check
make format           # Auto-fix formatting
make typecheck        # mypy strict mode
make test-unit        # Unit tests only
make test-integration # Integration tests (needs backend running)
make test-e2e         # Playwright E2E (needs both frontend + backend running)
make frontend         # Start Flet frontend
make backend          # Start FastAPI backend
```

## Coding Standards
- Python 3.11+, type annotations on every function
- pathlib.Path for all file operations, never os.path
- logging module, never print()
- Pydantic v2 for all data models
- Config from environment variables via python-dotenv, never hardcoded
- Max 300 lines per file
- One concern per file
- Google-style docstrings on every public function and class
