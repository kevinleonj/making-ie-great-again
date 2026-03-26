# Handoff

## Last Change: TTS Backend Switch + Frontend Bug Fixes

### What Changed
**TTS Backend (mlx-audio to fal.ai F5-TTS):**
- **Replaced** `backend/services/tts_service.py`: Rewrote from mlx-audio local inference to fal.ai F5-TTS cloud API. Uses `fal_client.subscribe()` for voice cloning, downloads generated audio via httpx, saves as WAV. Mock mode preserved exactly as before.
- **Updated** `backend/config.py`: Replaced `tts_model_id` with `fal_key` (from FAL_KEY env var) and `fal_tts_model` (from FAL_TTS_MODEL env var, default "fal-ai/f5-tts").
- **Created** `scripts/upload_ref_audio.py`: One-time script to upload `data/trump_30s.wav` and `data/maduro_30s.wav` to fal CDN storage, saves URLs to `data/fal_audio_urls.json`.
- **Updated** `pyproject.toml`: Replaced `mlx-audio` and `librosa` TTS extras with `fal-client>=0.5.0`.
- **Updated** `tests/unit/test_tts_service.py`: Changed constructor calls from `model_id` to `fal_key`/`fal_tts_model` params. All mock tests pass without changes to logic.

**Frontend Bug Fixes (`frontend/components/audio_player.py`):**
- **Fixed** "Unknown control: Audio" error: Removed `page.overlay.append(audio)` since flet_audio 0.80.5 Audio is a Service that auto-registers via the page service registry.
- **Fixed** async play/pause handler: Assigned `on_play_pause` directly to `play_pause_button.on_click` after definition instead of wrapping in a lambda (which masked the async nature from Flet's coroutine detection).
- **Fixed** download button: Changed `on_download` to `async def` and replaced deprecated `page.launch_url()` with `await UrlLauncher().launch_url()`.

**Documentation:**
- **Updated** `CLAUDE.md`, `README.md`: Replaced mlx-audio/Qwen3-TTS references with fal.ai/F5-TTS.
- **Updated** `frontend/pages/architecture.py`: Changed pipeline step and tech stack from mlx-audio to fal.ai F5-TTS.

### Files NOT Modified (as constrained)
- `backend/models/schemas.py`
- `backend/routers/tts.py`
- `backend/routers/transform.py`
- `backend/services/llm_service.py`
- `backend/prompts/*`

### Lint/Test Status
- Ruff check and format: pass
- Unit tests: pass (mock mode, no fal.ai calls)

### What's Next
1. Run `scripts/upload_ref_audio.py` with a valid FAL_KEY to upload reference audio and generate `data/fal_audio_urls.json`.
2. Update `.env` with `FAL_KEY=your-key` (the `.env.example` needs manual update: remove `TTS_MODEL_ID`, add `FAL_KEY=` and `FAL_TTS_MODEL=fal-ai/f5-tts`).
3. Reinstall dependencies: `pip install -e ".[tts]"` to get `fal-client` instead of `mlx-audio`.
4. Test live TTS generation with both servers running.

### Blockers
- `.env.example` could not be updated programmatically due to dotfile permission restrictions. Must be updated manually.
- `data/fal_audio_urls.json` does not exist yet. Must run upload script with valid FAL_KEY before live TTS works.
- User must set `FAL_KEY` in `.env`.
