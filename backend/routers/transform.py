"""Text transformation API endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.models.schemas import TransformRequest, TransformResponse
from backend.services.llm_service import LLMService, create_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["transform"])

_llm_service: LLMService | None = None


def _get_llm_service() -> LLMService:
    """Return a lazily initialized LLM service singleton.

    Returns:
        A configured LLMService instance.
    """
    global _llm_service  # noqa: PLW0603
    if _llm_service is None:
        _llm_service = create_llm_service()
    return _llm_service


@router.post("/transform", response_model=TransformResponse)
async def transform_text(request: TransformRequest) -> TransformResponse:
    """Transform input text into a leader's speaking style.

    Args:
        request: The transformation request with leader and text.

    Returns:
        The original and transformed text with metadata.

    Raises:
        HTTPException: If transformation fails.
    """
    try:
        service = _get_llm_service()
        transformed = service.transform_text(request.leader, request.text)
        language = service.get_language(request.leader)

        return TransformResponse(
            original_text=request.text,
            transformed_text=transformed,
            leader=request.leader,
            language=language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Transform failed for leader=%s", request.leader)
        raise HTTPException(status_code=500, detail="Text transformation failed") from exc
