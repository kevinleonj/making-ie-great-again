"""Claude API client for text style transformation."""

from __future__ import annotations

import logging

from anthropic import Anthropic

from backend.config import get_settings
from backend.prompts.maduro_metaprompt import MADURO_SYSTEM_PROMPT
from backend.prompts.trump_metaprompt import TRUMP_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_PROMPTS: dict[str, str] = {
    "trump": TRUMP_SYSTEM_PROMPT,
    "maduro": MADURO_SYSTEM_PROMPT,
}

_LANGUAGES: dict[str, str] = {
    "trump": "en",
    "maduro": "es",
}


class LLMService:
    """Handles text transformation via the Claude API.

    Args:
        api_key: Anthropic API key.
        model: Model ID to use.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def transform_text(self, leader: str, text: str) -> str:
        """Transform text into the specified leader's speaking style.

        Args:
            leader: "trump" or "maduro".
            text: Input text to transform.

        Returns:
            Transformed text in the leader's style.

        Raises:
            ValueError: If leader is not recognized.
            anthropic.APIError: If the API call fails.
        """
        system_prompt = _PROMPTS.get(leader)
        if system_prompt is None:
            msg = f"Unknown leader: {leader}"
            raise ValueError(msg)

        logger.info("Transforming text for %s (%d chars)", leader, len(text))

        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": text}],
        )

        result = message.content[0].text
        logger.info("Transformation complete (%d chars)", len(result))
        return result

    def get_language(self, leader: str) -> str:
        """Get the output language code for a leader.

        Args:
            leader: "trump" or "maduro".

        Returns:
            Language code ("en" or "es").
        """
        return _LANGUAGES.get(leader, "en")


def create_llm_service() -> LLMService:
    """Factory function to create an LLMService from settings.

    Returns:
        A configured LLMService instance.
    """
    settings = get_settings()
    return LLMService(
        api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
    )
