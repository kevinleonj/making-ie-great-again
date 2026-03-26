"""Pydantic request/response models for the API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TransformRequest(BaseModel):
    """Request body for text transformation."""

    leader: Literal["trump", "maduro"]
    text: str = Field(..., min_length=1, max_length=500)


class TransformResponse(BaseModel):
    """Response body for text transformation."""

    original_text: str
    transformed_text: str
    leader: str
    language: str


class TTSRequest(BaseModel):
    """Request body for TTS generation."""

    leader: Literal["trump", "maduro"]
    text: str = Field(..., min_length=1, max_length=500)


class TTSResponse(BaseModel):
    """Response body for TTS generation."""

    audio_url: str
    duration_seconds: float
    sample_rate: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
