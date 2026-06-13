"""LLM API client for Dungeon Master.

Handles communication with OpenRouter and local Llama servers
using the OpenAI-compatible API format.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx
from openai import AsyncOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

# Default timeout: 60 seconds for generation, 10 seconds for connection
_DEFAULT_TIMEOUT = 60.0
_CONNECTION_TIMEOUT = 10.0


@dataclass
class LLMResponse:
    """Response from an LLM API call.

    Attributes:
        content: The generated text content.
        model: The model that generated the response.
        usage: Token usage statistics if available.
        error: Error message if the call failed.
    """

    content: Optional[str] = None
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class LLMClient:
    """Client for LLM API calls (OpenRouter or local server).

    Uses the OpenAI-compatible API format, which works with both
    OpenRouter and local servers like vLLM and llama.cpp.

    Attributes:
        api_base: The API base URL.
        model: The model name to use.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        client: The AsyncOpenAI client instance.
    """

    def __init__(
        self,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ) -> None:
        settings = get_settings()

        self.api_base = api_base or settings.llm_api_base
        self.model = model or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens

        # Determine if using OpenRouter or local server
        is_openrouter = "openrouter" in self.api_base

        if is_openrouter:
            self.client = AsyncOpenAI(
                base_url=self.api_base,
                api_key=api_key or settings.model_dump().get("llm_api_key", ""),
            )
        else:
            self.client = AsyncOpenAI(
                base_url=self.api_base,
                api_key=api_key or settings.model_dump().get("llm_api_key", "not-needed"),
            )

    async def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Send a chat completion request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Override max tokens (uses default if None).
            temperature: Override temperature (uses default if None).

        Returns:
            LLMResponse with the generated content or error.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[dict(m) for m in messages],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                timeout=httpx.Timeout(
                    connect=_CONNECTION_TIMEOUT,
                    read=_DEFAULT_TIMEOUT,
                    write=_DEFAULT_TIMEOUT,
                    pool=_CONNECTION_TIMEOUT,
                ),
            )

            # Extract the first choice's content
            if response.choices:
                choice = response.choices[0]
                return LLMResponse(
                    content=choice.message.content,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                )

            return LLMResponse(
                content="",
                error="No choices returned from LLM",
            )

        except httpx.TimeoutException:
            logger.warning("LLM call timed out for model %s", self.model)
            return LLMResponse(
                content="The dungeon master is contemplating your fate... please wait.",
                error="timeout",
            )
        except httpx.ConnectError:
            logger.warning("LLM connection failed for %s", self.api_base)
            return LLMResponse(
                content="The air is still and silent. No response comes from the ether.",
                error="connection",
            )
        except Exception as e:
            logger.error("LLM call failed: %s", str(e))
            return LLMResponse(
                content="Something has gone wrong in the realm...",
                error=str(e),
            )

    async def chat_with_fallback(
        self,
        messages: list[dict[str, str]],
        fallback_content: str = "The dungeon master murmurs something unintelligible.",
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send a chat request with graceful fallback on error.

        Args:
            messages: List of message dicts.
            fallback_content: Content to return if LLM is unreachable.
            max_tokens: Override max tokens.

        Returns:
            LLMResponse, using fallback content on any error.
        """
        response = await self.chat(messages, max_tokens=max_tokens)
        if response.error and not response.content:
            response.content = fallback_content
            response.error = None
        return response
