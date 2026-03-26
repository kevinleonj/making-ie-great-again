# MakingIEGreatAgain

Voice cloning demo powered by Flet, FastAPI, Claude API, and fal.ai F5-TTS.

## Architecture

```
+-------------------+       HTTP        +-------------------+
|                   | ----------------> |                   |
|   Flet Frontend   |                   |  FastAPI Backend   |
|   (port 8550)     | <---------------- |  (port 8000)       |
|                   |   JSON + Audio    |                   |
+-------------------+                   +--------+----------+
        |                                        |
        |  User Flow:                            |  Services:
        |                                        |
        |  1. Enter text                         +-------> Claude API
        |  2. Select a leader                    |         (text transformation)
        |  3. Click "Transform"                  |
        |  4. Review transformed text            +-------> fal.ai F5-TTS
        |  5. Generate voice audio               |         (cloud voice cloning)
        |  6. Play cloned audio                  |
        |                                        v
        |                               +-------------------+
        +-----------------------------> |   Audio Output    |
               Playback                 |   (WAV files)     |
                                        +-------------------+
```

**Data flow:** User enters text and selects a political leader. The backend sends the text to the Claude API, which rewrites it in the leader's speaking style using a custom metaprompt. The rewritten text is then passed to the fal.ai F5-TTS cloud API, which generates speech using a pre-uploaded reference audio clip of the leader's voice. The frontend streams the resulting WAV file for playback.

## Prerequisites

- Python 3.11 or later
- A fal.ai API key for F5-TTS voice cloning
- An Anthropic API key with access to Claude

## Setup

1. Clone the repository and navigate to the project directory:

```bash
cd making-ie-great-again
```

2. Copy the environment template and set your API key:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-... and FAL_KEY=...
```

3. Place reference audio files (WAV format) for each leader in the `data/` directory, then upload them to fal CDN:

```bash
FAL_KEY=your-key python scripts/upload_ref_audio.py
```

This creates `data/fal_audio_urls.json` with the CDN URLs used by the TTS service.

4. Install all dependencies:

```bash
make install
```

This installs the project in editable mode with dev, TTS, and audio extras, and downloads the Playwright Chromium browser for E2E tests.

## Running

Start the backend and frontend in **separate terminals**:

```bash
# Terminal 1
make backend

# Terminal 2
make frontend
```

Or launch both at once (they run as background processes):

```bash
scripts/run_all.sh
```

The frontend will be available at `http://localhost:8550` and the backend API at `http://localhost:8000`.

## Testing

| Command                | Description                                      |
|------------------------|--------------------------------------------------|
| `make test-unit`       | Run unit tests (no servers required)             |
| `make test-integration`| Run integration tests (backend must be running)  |
| `make test-e2e`        | Run Playwright E2E tests (both servers required) |
| `make lint`            | Run ruff linter and format checker               |
| `make typecheck`       | Run mypy in strict mode                          |
| `make format`          | Auto fix formatting and lint issues              |

Integration and E2E tests skip gracefully when servers are not running.

## Project Structure

```
making-ie-great-again/
  backend/                 # FastAPI application
    config.py              # Environment and app configuration
    main.py                # FastAPI app factory and startup
    models/
      schemas.py           # Pydantic request/response models
    prompts/
      trump_metaprompt.py  # Trump style transformation prompt
      maduro_metaprompt.py # Maduro style transformation prompt
    routers/
      transform.py         # Text transformation endpoints
      tts.py               # TTS generation and audio serving endpoints
    services/
      llm_service.py       # Claude API integration
      tts_service.py       # fal.ai F5-TTS integration
  frontend/                # Flet web application
    config.py              # Frontend configuration
    main.py                # Flet app entry point
    api_client.py          # HTTP client for backend communication
    router.py              # Page routing
    theme.py               # Visual theme and styling
    components/            # Reusable UI components
      audio_player.py      # Audio playback widget
      leader_card.py       # Leader selection card
      nav_bar.py           # Navigation bar
      page_header.py       # Page header
      text_input_panel.py  # Text input and transform panel
    pages/                 # Application pages
      home.py              # Main page with leader selection and TTS
      bio_trump.py         # Trump biography page
      bio_maduro.py        # Maduro biography page
      architecture.py      # Architecture explanation page
  tests/                   # Test suite
    unit/                  # Unit tests (no external dependencies)
    integration/           # API integration tests (needs backend)
    e2e/                   # Playwright browser tests (needs both servers)
  scripts/                 # Shell scripts for running services
  data/                    # Reference audio files (user provided)
  pyproject.toml           # Project metadata, dependencies, tool config
  Makefile                 # Common development commands
  CLAUDE.md                # AI assistant project context
  HANDOFF.md               # Development state and next steps
```
