"""Game loop for Dungeon Master.

Orchestrates the main game loop: player input -> parse -> execute ->
LLM generate response -> return.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.engine.command_parser import CommandParser, ParsedCommand
from app.engine.conversation import ConversationHistory
from app.engine.llm_client import LLMClient
from app.engine.prompt_engine import PromptEngine

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """Current state of the game for context passing.

    Attributes:
        location: Current room/location name.
        hp: Current hit points.
        gold: Current gold amount.
        inventory: List of item names in inventory.
    """

    location: str = "tavern"
    hp: int = 100
    gold: int = 0
    inventory: list[str] = field(default_factory=list)

    def to_context_string(self) -> str:
        """Convert state to a string for LLM context.

        Returns:
            Formatted state string for the LLM.
        """
        items = ", ".join(self.inventory) if self.inventory else "nothing"
        return (
            f"Location: {self.location}\n"
            f"HP: {self.hp}\n"
            f"Gold: {self.gold}\n"
            f"Inventory: [{items}]"
        )


@dataclass
class GameResult:
    """Result of a single game turn.

    Attributes:
        narrative: The LLM's narrative response.
        status: Extracted game state changes (if any).
        command: The parsed command that was executed.
    """

    narrative: str
    status: Optional[dict] = None
    command: Optional[ParsedCommand] = None


class GameLoop:
    """Main game loop orchestrator.

    Manages the conversation and game state, handling the cycle of
    player input -> parsing -> LLM response -> state update.

    Attributes:
        llm_client: The LLM API client.
        prompt_engine: The prompt engine.
        command_parser: The command parser.
        conversation: The conversation history.
        game_state: Current game state.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        prompt_engine: Optional[PromptEngine] = None,
        command_parser: Optional[CommandParser] = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.prompt_engine = prompt_engine or PromptEngine()
        self.command_parser = command_parser or CommandParser()
        self.conversation = ConversationHistory()
        self.game_state = GameState()

    def start_new_game(self) -> str:
        """Start a new game session.

        Returns:
            The welcome narrative message.
        """
        self.conversation = ConversationHistory(
            system_prompt=self.prompt_engine.system_prompt,
        )
        self.game_state = GameState()
        return self.prompt_engine.player_welcome

    async def process_turn(self, player_input: str) -> GameResult:
        """Process a single game turn.

        Args:
            player_input: Raw player input text.

        Returns:
            GameResult with narrative, status, and command info.
        """
        # Parse the command
        parsed = self.command_parser.parse(player_input)

        # Build world context
        world_context = self.game_state.to_context_string()

        # Build conversation messages
        messages = self.prompt_engine.build_conversation_messages(
            conversation_history=self.conversation.message_list,
            player_input=player_input,
            world_context=world_context,
        )

        # Check if summarization is needed
        if self.conversation.needs_summarization():
            await self.conversation.summarize_with_llm(self.llm_client)
            messages = self.conversation.message_list

        # Call LLM
        response = await self.llm_client.chat(messages)

        # Add turn to conversation
        if response.content:
            self.conversation.add_turn("user", player_input)
            self.conversation.add_turn("assistant", response.content)

        # Try to extract status updates from response
        status = self.prompt_engine.extract_status_from_response(response.content or "")
        if status:
            self._apply_status_update(status)

        return GameResult(
            narrative=response.content or "",
            status=status,
            command=parsed,
        )

    def _apply_status_update(self, status: dict) -> None:
        """Apply status update to game state.

        Args:
            status: Dict with hp, gold, location keys.
        """
        if "hp" in status:
            self.game_state.hp = status["hp"]
        if "gold" in status:
            self.game_state.gold = status["gold"]
        if "location" in status:
            self.game_state.location = status["location"]

    def get_current_state(self) -> GameState:
        """Get a copy of the current game state.

        Returns:
            Current GameState.
        """
        return GameState(
            location=self.game_state.location,
            hp=self.game_state.hp,
            gold=self.game_state.gold,
            inventory=list(self.game_state.inventory),
        )

    def get_status_line(self) -> str:
        """Get a formatted status line for the player.

        Returns:
            Formatted status string.
        """
        items = ", ".join(self.game_state.inventory) if self.game_state.inventory else "empty"
        return f"[HP: {self.game_state.hp} | Gold: {self.game_state.gold} | Loc: {self.game_state.location} | Inv: {items}]"
