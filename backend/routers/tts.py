"""TTS generation API endpoints."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.models.schemas import TTSRequest, TTSResponse
from backend.services.tts_service import get_tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tts"])


@router.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest) -> TTSResponse:
    """Generate speech audio from text in a leader's cloned voice.

    Args:
        request: TTS request with leader and text.

    Returns:
        Audio URL and metadata.
    """
    try:
        service = get_tts_service()
        result = await asyncio.to_thread(service.generate, request.leader, request.text)
        audio_url = f"/api/audio/{result.filename}"

        return TTSResponse(
            audio_url=audio_url,
            duration_seconds=result.duration_seconds,
            sample_rate=result.sample_rate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("TTS generation failed for leader=%s", request.leader)
        raise HTTPException(status_code=500, detail="TTS generation failed") from exc


@router.get("/audio/{filename}")
async def get_audio(filename: str) -> FileResponse:
    """Serve a generated audio file.

    Args:
        filename: The WAV filename to serve.

    Returns:
        The audio file as a streaming response.
    """
    service = get_tts_service()
    try:
        file_path = service.resolve_audio_path(filename)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Access denied") from exc

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=filename,
    )
