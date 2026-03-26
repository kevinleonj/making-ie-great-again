"""Tests for Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    ErrorResponse,
    TransformRequest,
    TransformResponse,
    TTSRequest,
    TTSResponse,
)


def test_transform_request_valid() -> None:
    """Valid transform request is accepted."""
    req = TransformRequest(leader="trump", text="Hello world")
    assert req.leader == "trump"
    assert req.text == "Hello world"


def test_transform_request_invalid_leader() -> None:
    """Invalid leader value is rejected."""
    with pytest.raises(ValidationError):
        TransformRequest(leader="obama", text="Hello")


def test_transform_request_empty_text() -> None:
    """Empty text is rejected."""
    with pytest.raises(ValidationError):
        TransformRequest(leader="trump", text="")


def test_transform_request_text_too_long() -> None:
    """Text exceeding max length is rejected."""
    with pytest.raises(ValidationError):
        TransformRequest(leader="trump", text="x" * 501)


def test_transform_response() -> None:
    """Transform response model works correctly."""
    resp = TransformResponse(
        original_text="Hi",
        transformed_text="Tremendous hi",
        leader="trump",
        language="en",
    )
    assert resp.transformed_text == "Tremendous hi"


def test_tts_request_valid() -> None:
    """Valid TTS request is accepted."""
    req = TTSRequest(leader="maduro", text="Hola mundo")
    assert req.leader == "maduro"


def test_tts_response() -> None:
    """TTS response model works correctly."""
    resp = TTSResponse(audio_url="/api/audio/test.wav", duration_seconds=3.5, sample_rate=24000)
    assert resp.duration_seconds == 3.5


def test_error_response() -> None:
    """Error response model works correctly."""
    resp = ErrorResponse(error="Not found", detail="Resource missing")
    assert resp.error == "Not found"
