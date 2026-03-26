"""Tests for the LLM service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.services.llm_service import LLMService


def test_transform_text_trump() -> None:
    """Transform text calls Claude API with Trump system prompt."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Believe me, this is tremendous")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    service = LLMService(api_key="test-key", model="test-model")
    service._client = mock_client

    result = service.transform_text("trump", "This is good")

    assert result == "Believe me, this is tremendous"
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert "trump" in call_kwargs["system"].lower()


def test_transform_text_maduro() -> None:
    """Transform text calls Claude API with Maduro system prompt."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Compatriotas, vamos a vencer")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    service = LLMService(api_key="test-key", model="test-model")
    service._client = mock_client

    result = service.transform_text("maduro", "We will win")

    assert result == "Compatriotas, vamos a vencer"
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert "spanish" in call_kwargs["system"].lower()


def test_transform_text_unknown_leader() -> None:
    """Unknown leader raises ValueError."""
    service = LLMService(api_key="test-key", model="test-model")
    with pytest.raises(ValueError, match="Unknown leader"):
        service.transform_text("obama", "Hello")


def test_get_language() -> None:
    """Language codes are correct for each leader."""
    service = LLMService(api_key="test-key", model="test-model")
    assert service.get_language("trump") == "en"
    assert service.get_language("maduro") == "es"


def test_get_language_unknown_defaults_to_en() -> None:
    """Unknown leader defaults to English language code."""
    service = LLMService(api_key="test-key", model="test-model")
    assert service.get_language("unknown") == "en"
