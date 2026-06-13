"""Conversation history management for Dungeon Master.

Maintains conversation context with automatic summarization
of old turns to stay within token limits.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.engine.llm_client import LLMClient

logger = logging.getLogger(__name__)

# Maximum total tokens in conversation history (conservative limit)
MAX_CONVERSATION_TOKENS = 8192

# Number of recent turns to keep before summarizing
TURN_SUMMARIZE_THRESHOLD = 10

# Token budget for summarized history (vs fresh turns)
SUMMARIZED_TOKEN_BUDGET = 2048


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation.

    Attributes:
        role: The speaker role ('user' or 'assistant').
        content: The message content.
        tokens: Approximate token count.
    """

    role: str
    content: str
    tokens: int = 0


@dataclass
class ConversationHistory:
    """Manages conversation history with summarization.

    Attributes:
        turns: List of conversation turns.
        system_prompt: The system prompt for the conversation.
        summarized: Flag indicating if history has been summarized.
    """

    system_prompt: str = ""
    turns: list[ConversationTurn] = field(default_factory=list)
    summarized: bool = False

    def add_turn(self, role: str, content: str) -> None:
        """Add a turn to the conversation history.

        Args:
            role: 'user' or 'assistant'.
            content: The message content.
        """
        # Simple token estimation: ~4 chars per token
        estimated_tokens = max(1, len(content) // 4)
        self.turns.append(ConversationTurn(
            role=role,
            content=content,
            tokens=estimated_tokens,
        ))
        self.summarized = False

    @property
    def total_tokens(self) -> int:
        """Get total estimated token count of conversation."""
        return sum(t.tokens for t in self.turns)

    @property
    def message_list(self) -> list[dict[str, str]]:
        """Get conversation as a list of API-ready messages.

        Returns:
            List of dicts with 'role' and 'content' keys.
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for turn in self.turns:
            messages.append({
                "role": turn.role,
                "content": turn.content,
            })

        return messages

    def to_api_messages(self) -> list[dict[str, str]]:
        """Alias for message_list for compatibility."""
        return self.message_list

    def needs_summarization(self) -> bool:
        """Check if the conversation needs summarization.

        Returns:
            True if the conversation exceeds token limits or turn count.
        """
        return (
            self.total_tokens > MAX_CONVERSATION_TOKENS
            or len(self.turns) > TURN_SUMMARIZE_THRESHOLD * 2
        )

    async def summarize_with_llm(
        self,
        llm_client: LLMClient,
    ) -> None:
        """Summarize old conversation turns using the LLM.

        The oldest 2/3 of turns are summarized into a single
        narrative summary that replaces them. The newest 1/3
        of turns are preserved verbatim.

        Args:
            llm_client: The LLM client to use for summarization.
        """
        if len(self.turns) < 3:
            logger.debug("Not enough turns to summarize")
            return

        # Keep the newest 1/3, summarize the rest
        preserve_count = max(1, len(self.turns) // 3)
        to_summarize = self.turns[:len(self.turns) - preserve_count]
        preserved = self.turns[len(self.turns) - preserve_count:]

        summary_text = await self._create_summary(llm_client, to_summarize)

        # Replace old turns with summary turn
        self.turns = preserved
        self.turns.insert(0, ConversationTurn(
            role="system",
            content=f"[Previous conversation summary]\n{summary_text}",
            tokens=len(summary_text) // 4,
        ))
        self.summarized = True
        logger.info("Conversation summarized: %d turns reduced to %d",
                     len(to_summarize), len(self.turns))

    async def _create_summary(
        self,
        llm_client: LLMClient,
        turns: list[ConversationTurn],
    ) -> str:
        """Create a narrative summary of conversation turns.

        Args:
            llm_client: The LLM client for summarization.
            turns: Turns to summarize.

        Returns:
            Narrative summary string.
        """
        # Build a readable transcript
        transcript_parts = []
        for turn in turns:
            speaker = "Player" if turn.role == "user" else "Dungeon Master"
            transcript_parts.append(f"{speaker}: {turn.content}")

        transcript = "\n\n".join(transcript_parts)
        prompt = (
            "Summarize the following RPG conversation. Focus on:\n"
            "- Key events and discoveries\n"
            "- Changes in player state or location\n"
            "- Important NPC interactions\n"
            "- Notable items acquired or used\n\n"
            "Keep the summary under 300 words. Write it as an ongoing "
            "narrative, not a list.\n\n"
            f"Conversation:\n{transcript}"
        )

        response = await llm_client.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )

        return response.content or "Conversation history was summarized."

    def clear(self) -> None:
        """Clear all conversation history."""
        self.turns.clear()
        self.summarized = False
