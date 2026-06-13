"""Tests for the Dungeon Master engine module.

Tests cover:
- Command parser (RED/GREEN/REFACTOR/OBSERVE)
- Prompt engine
- Conversation history management
- Game loop integration
- LLM client with mock
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.engine.command_parser import (
    CommandParser,
    CommandType,
    ParsedCommand,
)
from app.engine.conversation import ConversationHistory, ConversationTurn
from app.engine.game_loop import GameLoop, GameState, GameResult
from app.engine.llm_client import LLMClient, LLMResponse
from app.engine.prompt_engine import PromptEngine


# ============================================================
# RED: Tests that verify expected behavior before implementation
# ============================================================


class TestCommandParser:
    """Tests for the command parser."""

    @pytest.fixture
    def parser(self):
        return CommandParser()

    def test_parse_look(self, parser):
        """RED: Parse 'look around' returns LOOK command."""
        result = parser.parse("look around")
        assert result.command_type == CommandType.LOOK
        assert result.confidence >= 0.9

    def test_parse_look_with_target(self, parser):
        """RED: Parse 'look at the sword' with target."""
        result = parser.parse("look at the sword")
        assert result.command_type == CommandType.LOOK
        assert result.target is not None

    def test_parse_move_north(self, parser):
        """RED: Parse 'go north' returns MOVE command."""
        result = parser.parse("go north")
        assert result.command_type == CommandType.MOVE
        assert result.target == "north"

    def test_parse_move_short_direction(self, parser):
        """RED: Parse 'go n' returns MOVE command with full direction."""
        result = parser.parse("go n")
        assert result.command_type == CommandType.MOVE
        assert result.target == "north"

    def test_parse_take(self, parser):
        """RED: Parse 'take sword' returns TAKE command."""
        result = parser.parse("take sword")
        assert result.command_type == CommandType.TAKE
        assert result.target == "sword"

    def test_parse_use(self, parser):
        """RED: Parse 'use potion' returns USE command."""
        result = parser.parse("use potion")
        assert result.command_type == CommandType.USE
        assert result.target == "potion"

    def test_parse_talk(self, parser):
        """RED: Parse 'talk to merchant' returns TALK command."""
        result = parser.parse("talk to merchant")
        assert result.command_type == CommandType.TALK
        assert result.target == "merchant"

    def test_parse_inventory(self, parser):
        """RED: Parse 'inventory' returns INVENTORY command."""
        result = parser.parse("inventory")
        assert result.command_type == CommandType.INVENTORY

    def test_parse_inventory_short(self, parser):
        """RED: Parse 'i' returns INVENTORY command."""
        result = parser.parse("i")
        assert result.command_type == CommandType.INVENTORY

    def test_parse_attack(self, parser):
        """RED: Parse 'attack goblin' returns ATTACK command."""
        result = parser.parse("attack goblin")
        assert result.command_type == CommandType.ATTACK
        assert result.target == "goblin"

    def test_parse_help(self, parser):
        """RED: Parse 'help' returns HELP command."""
        result = parser.parse("help")
        assert result.command_type == CommandType.HELP

    def test_parse_unknown_command(self, parser):
        """RED: Unknown input returns UNKNOWN command."""
        result = parser.parse("xyzzy")
        assert result.command_type == CommandType.UNKNOWN
        assert result.confidence < 0.5

    def test_parse_empty_input(self, parser):
        """RED: Empty input returns UNKNOWN with low confidence."""
        result = parser.parse("")
        assert result.command_type == CommandType.UNKNOWN
        assert result.confidence < 0.5

    def test_parse_fuzzy_move(self, parser):
        """RED: 'walk to the north door' maps to MOVE."""
        result = parser.parse("walk to the north door")
        assert result.command_type == CommandType.MOVE
        assert result.target == "north"

    def test_parse_varied_take_verbs(self, parser):
        """RED: 'pickup coin' and 'grab coin' both parse as TAKE."""
        for verb in ["pickup", "grab", "pick up", "get"]:
            result = parser.parse(f"{verb} coin")
            assert result.command_type == CommandType.TAKE, f"Failed for verb: {verb}"

    def test_get_command_help(self, parser):
        """GREEN: Help message lists all commands."""
        help_text = parser.get_command_help()
        assert "look" in help_text
        assert "go" in help_text
        assert "take" in help_text
        assert "use" in help_text
        assert "talk" in help_text
        assert "inventory" in help_text
        assert "attack" in help_text
        assert "help" in help_text


class TestPromptEngine:
    """Tests for the prompt engine."""

    @pytest.fixture
    def engine(self):
        return PromptEngine()

    def test_build_user_message(self, engine):
        """GREEN: User message contains player input."""
        msg = engine.build_user_message("look around")
        assert "look around" in msg

    def test_build_user_message_with_context(self, engine):
        """GREEN: User message includes world context."""
        msg = engine.build_user_message("look around", "You are in a tavern.")
        assert "You are in a tavern." in msg
        assert "look around" in msg

    def test_build_conversation_messages(self, engine):
        """GREEN: Messages include system prompt and history."""
        history = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "welcome"},
        ]
        messages = engine.build_conversation_messages(history, "go north")
        assert len(messages) == 4  # system + 2 history + new user
        assert messages[0]["role"] == "system"
        assert messages[3]["role"] == "user"

    def test_extract_status_from_response(self, engine):
        """RED: Extract status from response text."""
        response = (
            "You stand in the tavern.\n\n"
            "The barkeep looks at you.\n\n"
            "[HP: 80 | Gold: 15 | Loc: tavern]"
        )
        status = engine.extract_status_from_response(response)
        assert status is not None
        assert status["hp"] == 80
        assert status["gold"] == 15
        assert status["location"] == "tavern"

    def test_extract_status_missing(self, engine):
        """RED: Returns None when no status line found."""
        response = "You walk through the dark forest."
        status = engine.extract_status_from_response(response)
        assert status is None

    def test_player_welcome_message(self, engine):
        """GREEN: Welcome message is non-empty and relevant."""
        assert "Welcome" in engine.player_welcome
        assert "tavern" in engine.player_welcome


class TestConversationHistory:
    """Tests for conversation history management."""

    def test_add_turn(self):
        """GREEN: Adding a turn stores it."""
        conv = ConversationHistory()
        conv.add_turn("user", "hello")
        assert len(conv.turns) == 1
        assert conv.turns[0].role == "user"
        assert conv.turns[0].content == "hello"

    def test_total_tokens(self):
        """GREEN: Token count is estimated correctly."""
        conv = ConversationHistory()
        conv.add_turn("user", "a" * 40)  # ~10 tokens
        assert conv.total_tokens >= 10

    def test_message_list_format(self):
        """GREEN: Message list has correct role/content format."""
        conv = ConversationHistory(
            system_prompt="You are a DM",
        )
        conv.add_turn("user", "look")
        messages = conv.message_list
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_needs_summarization(self):
        """RED: Conversation exceeds threshold when long enough."""
        conv = ConversationHistory()
        # Add enough turns to exceed threshold
        for i in range(25):
            conv.add_turn("user", f"Turn {i}")
            conv.add_turn("assistant", f"Response {i}")
        assert conv.needs_summarization()

    def test_clear(self):
        """GREEN: Clear resets conversation."""
        conv = ConversationHistory()
        conv.add_turn("user", "hello")
        conv.clear()
        assert len(conv.turns) == 0
        assert not conv.summarized

    @pytest.mark.asyncio
    async def test_summarize_with_llm(self):
        """GREEN: Summarization replaces old turns."""
        conv = ConversationHistory()
        for i in range(6):
            conv.add_turn("user", f"Input {i}")
            conv.add_turn("assistant", f"Response {i}")

        mock_client = AsyncMock(spec=LLMClient)
        mock_client.chat = AsyncMock(return_value=LLMResponse(
            content="Summary of the adventure so far.",
        ))

        await conv.summarize_with_llm(mock_client)
        assert conv.summarized
        mock_client.chat.assert_called_once()


class TestGameState:
    """Tests for game state."""

    def test_initial_state(self):
        """GREEN: Default state is reasonable."""
        state = GameState()
        assert state.hp == 100
        assert state.gold == 0
        assert state.inventory == []

    def test_to_context_string(self):
        """GREEN: Context string contains all fields."""
        state = GameState(location="forest", hp=50, gold=10, inventory=["sword", "shield"])
        ctx = state.to_context_string()
        assert "forest" in ctx
        assert "50" in ctx
        assert "10" in ctx
        assert "sword" in ctx


class TestLLMClient:
    """Tests for the LLM client."""

    @pytest.mark.asyncio
    async def test_chat_returns_response(self):
        """GREEN: Chat returns LLMResponse with content."""
        with patch("app.engine.llm_client.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="You see a dragon."))]
            mock_response.model = "test-model"
            mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            client = LLMClient(api_base="http://localhost:8000/v1", model="test-model")
            result = await client.chat([{"role": "user", "content": "hello"}])

            assert result.content == "You see a dragon."
            assert result.model == "test-model"
            assert result.usage["prompt_tokens"] == 10

    @pytest.mark.asyncio
    async def test_chat_timeout(self):
        """RED: Timeout returns fallback content."""
        with patch("app.engine.llm_client.AsyncOpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            client = LLMClient(api_base="http://localhost:8000/v1", model="test")
            result = await client.chat([{"role": "user", "content": "hello"}])
            assert "contemplating" in (result.content or "").lower()

    @pytest.mark.asyncio
    async def test_chat_connection_error(self):
        """RED: Connection error returns fallback content."""
        with patch("app.engine.llm_client.AsyncOpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create = AsyncMock(
                side_effect=httpx.ConnectError("No connection")
            )
            client = LLMClient(api_base="http://localhost:8000/v1", model="test")
            result = await client.chat([{"role": "user", "content": "hello"}])
            assert "still and silent" in (result.content or "").lower()


class TestGameLoop:
    """Integration tests for the game loop."""

    @pytest.mark.asyncio
    async def test_start_new_game(self):
        """GREEN: Starting a game returns welcome message."""
        loop = GameLoop()
        result = loop.start_new_game()
        assert "Welcome" in result or "tavern" in result.lower()

    @pytest.mark.asyncio
    async def test_process_turn(self):
        """GREEN: Process turn returns GameResult with narrative."""
        with patch("app.engine.llm_client.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="You enter a dark room."))]
            mock_response.model = "test-model"
            mock_response.usage = None
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            loop = GameLoop()
            loop.start_new_game()
            result = await loop.process_turn("go north")

            assert isinstance(result, GameResult)
            assert "dark room" in result.narrative.lower()
            assert result.command is not None
            assert result.command.command_type == CommandType.MOVE

    @pytest.mark.asyncio
    async def test_process_turn_with_status(self):
        """GREEN: LLM response with status updates game state."""
        with patch("app.engine.llm_client.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(
                content="You found a treasure chest!\n\n[HP: 90 | Gold: 25 | Loc: treasure_room]"
            ))]
            mock_response.model = "test-model"
            mock_response.usage = None
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            loop = GameLoop()
            loop.start_new_game()
            result = await loop.process_turn("open chest")

            assert result.status is not None
            assert result.status["hp"] == 90
            assert result.status["gold"] == 25

    @pytest.mark.asyncio
    async def test_status_line(self):
        """GREEN: Status line contains current state."""
        loop = GameLoop()
        loop.start_new_game()
        status = loop.get_status_line()
        assert "HP:" in status
        assert "Gold:" in status
        assert "Loc:" in status


class TestCommandParserEdgeCases:
    """Edge case tests for command parser."""

    @pytest.fixture
    def parser(self):
        return CommandParser()

    def test_case_insensitive(self, parser):
        """GREEN: Commands are case-insensitive."""
        for case in ["LOOK", "Look", "look"]:
            result = parser.parse(case)
            assert result.command_type == CommandType.LOOK

    def test_whitespace_handling(self, parser):
        """GREEN: Extra whitespace is handled."""
        result = parser.parse("  go north  ")
        assert result.command_type == CommandType.MOVE
        assert result.target == "north"

    def test_direction_aliases(self, parser):
        """GREEN: All direction aliases work."""
        for short, full in [("n", "north"), ("sw", "southwest"), ("se", "southeast")]:
            result = parser.parse(f"go {short}")
            assert result.target == full, f"Direction alias {short} -> {full} failed"
