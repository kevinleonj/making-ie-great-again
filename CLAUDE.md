# MakingIEGreatAgain

## Architecture
- **Frontend**: Flet 0.80.5 (Python, runs as web app on port 8550)
- **Backend**: FastAPI (Python, runs on port 8000)
- **Communication**: HTTP (httpx client in frontend calling backend REST API)
- **TTS Engine**: fal.ai Qwen3-TTS 1.7B (cloud API, two-step: clone-voice + text-to-speech)
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

## Flet 0.80.x Rules
- ALWAYS read source in .venv before using any Flet API, never guess signatures
- Use ft.Alignment.CENTER not ft.alignment.center
- Use ft.Padding.all() not ft.padding.all()
- Use ft.BorderRadius.only() not ft.border_radius.only()
- Use ft.Margin.only() not ft.margin.only()
- Controls are mutable. To update UI: change .value, then call .update()
- Never rebuild entire page on keystroke. Mutate specific controls.
- flet_audio 0.80.5 Audio is a Service (auto-registers), do NOT add to page.overlay
- TextButton uses content= (StrOrControl), NOT text=
- IconButton uses icon=, icon_color=, icon_size=, NOT content=

## Coding Standards
- Python 3.11+, type annotations on every function
- pathlib.Path for all file operations, never os.path
- logging module, never print()
- Pydantic v2 for all data models
- Config from environment variables via python-dotenv, never hardcoded
- Max 300 lines per file
- One concern per file
- Google-style docstrings on every public function and class
