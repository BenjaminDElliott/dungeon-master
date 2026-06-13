"""Command parser for Dungeon Master.

Parses natural language commands into structured game actions.
Supports 6+ command types with fuzzy matching for common variations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CommandType(Enum):
    """Supported game command types."""

    LOOK = "look"
    MOVE = "move"
    TAKE = "take"
    USE = "use"
    TALK = "talk"
    INVENTORY = "inventory"
    ATTACK = "attack"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """Result of parsing a player input.

    Attributes:
        command_type: The recognized command type.
        target: The target of the command (item, NPC, direction).
        extra: Additional parsed details.
        confidence: Confidence score 0.0-1.0.
        raw_input: The original input string.
    """

    command_type: CommandType
    target: Optional[str] = None
    extra: dict = field(default_factory=dict)
    confidence: float = 1.0
    raw_input: str = ""


class CommandParser:
    """Parses natural language commands into structured actions.

    Supports commands: look, go/move [direction], take/pickup [item],
    use [item], talk/say [to NPC] [message], inventory, attack [target],
    help.
    """

    # Direction mappings for movement commands
    DIRECTION_MAP: dict[str, str] = {
        # Cardinal directions
        "north": "north", "n": "north", "up": "north",
        "south": "south", "s": "south", "down": "south",
        "east": "east", "e": "east",
        "west": "west", "w": "west",
        # Diagonal
        "northwest": "northwest", "nw": "northwest",
        "northeast": "northeast", "ne": "northeast",
        "southwest": "southwest", "sw": "southwest",
        "southeast": "southeast", "se": "southeast",
    }

    def parse(self, raw_input: str) -> ParsedCommand:
        """Parse a player input string into a structured command.

        Args:
            raw_input: Raw player input text.

        Returns:
            ParsedCommand with structured action.
        """
        text = raw_input.strip().lower()
        if not text:
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                raw_input=raw_input,
                confidence=0.4,
            )

        # Check command patterns in priority order
        parsers = [
            self._parse_look,
            self._parse_move,
            self._parse_take,
            self._parse_use,
            self._parse_talk,
            self._parse_inventory,
            self._parse_attack,
            self._parse_help,
        ]

        for parser in parsers:
            result = parser(text)
            if result is not None:
                return result

        # Check if input looks like it could be an action
        if any(word in text for word in ["go", "walk", "travel", "head"]):
            direction = self._extract_direction(text)
            if direction:
                return ParsedCommand(
                    command_type=CommandType.MOVE,
                    target=direction,
                    raw_input=raw_input,
                    confidence=0.8,
                )

        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            target=self._extract_target(text),
            raw_input=raw_input,
            confidence=0.3,
        )

    def _parse_look(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(look|observe|examine|inspect|check|view)\b", text):
            target = self._extract_target(text)
            return ParsedCommand(
                command_type=CommandType.LOOK,
                target=target,
                raw_input=text,
                confidence=0.95,
            )
        return None

    def _parse_move(self, text: str) -> ParsedCommand | None:
        match = re.match(
            r"^(go|move|walk|head|run|travel|enter|leave)\b", text
        )
        if not match:
            return None
        direction = self._extract_direction(text)
        if direction:
            return ParsedCommand(
                command_type=CommandType.MOVE,
                target=direction,
                raw_input=text,
                confidence=0.95,
            )
        return None

    def _parse_take(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(take|pickup|grab|pick up|get)\b", text):
            target = self._extract_target(text)
            if target:
                return ParsedCommand(
                    command_type=CommandType.TAKE,
                    target=target,
                    raw_input=text,
                    confidence=0.9,
                )
            return ParsedCommand(
                command_type=CommandType.TAKE,
                raw_input=text,
                confidence=0.7,
            )
        return None

    def _parse_use(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(use|apply|drink|eat|wear|read)\b", text):
            target = self._extract_target(text)
            if target:
                return ParsedCommand(
                    command_type=CommandType.USE,
                    target=target,
                    raw_input=text,
                    confidence=0.9,
                )
            return ParsedCommand(
                command_type=CommandType.USE,
                raw_input=text,
                confidence=0.6,
            )
        return None

    def _parse_talk(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(talk|say|speak|ask|whisper)\b", text):
            target = self._extract_target(text)
            if target:
                return ParsedCommand(
                    command_type=CommandType.TALK,
                    target=target,
                    raw_input=text,
                    confidence=0.9,
                )
            return ParsedCommand(
                command_type=CommandType.TALK,
                raw_input=text,
                confidence=0.7,
            )
        return None

    def _parse_inventory(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(inventory|inv|i($|\s)|backpack|bags|check inventory)", text):
            return ParsedCommand(
                command_type=CommandType.INVENTORY,
                raw_input=text,
                confidence=0.95,
            )
        return None

    def _parse_attack(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(attack|hit|strike|slash|stab|kill)\b", text):
            target = self._extract_target(text)
            if target:
                return ParsedCommand(
                    command_type=CommandType.ATTACK,
                    target=target,
                    raw_input=text,
                    confidence=0.9,
                )
            return ParsedCommand(
                command_type=CommandType.ATTACK,
                raw_input=text,
                confidence=0.7,
            )
        return None

    def _parse_help(self, text: str) -> ParsedCommand | None:
        if re.match(r"^(help|commands|list|what can i|what can I)\b", text):
            return ParsedCommand(
                command_type=CommandType.HELP,
                raw_input=text,
                confidence=0.95,
            )
        return None

    def _extract_direction(self, text: str) -> Optional[str]:
        """Extract direction from text using DIRECTION_MAP."""
        words = text.split()
        for word in words:
            if word in self.DIRECTION_MAP:
                return self.DIRECTION_MAP[word]
        return None

    def _extract_target(self, text: str) -> Optional[str]:
        """Extract a target (item/NPC) from text, removing the command verb."""
        # Remove common command prefixes and get the rest
        prefixes = [
            r"^(look|observe|examine|inspect|check|view|go|move|walk|head|run|travel|enter|take|pickup|grab|pick up|get|use|apply|drink|eat|wear|read|talk|say|speak|ask|whisper|attack|hit|strike|slash|stab|kill)\b\s*",
        ]
        for prefix in prefixes:
            cleaned = re.sub(prefix, "", text, flags=re.IGNORECASE).strip()
            if cleaned:
                # Strip common preposition prefixes like "to", "at", "the"
                cleaned = re.sub(r"^(to|at|the|a|an)\s+", "", cleaned, flags=re.IGNORECASE).strip()
                if cleaned:
                    return cleaned
        return None

    def get_command_help(self) -> str:
        """Return a help message listing all supported commands."""
        return (
            "Available commands:\n"
            "  look [target]        - Examine your surroundings or an object\n"
            "  go [direction]       - Move to an adjacent room\n"
            "  take [item]          - Pick up an item\n"
            "  use [item]           - Use an item\n"
            "  talk [to npc] [msg]  - Speak with an NPC\n"
            "  inventory            - Check your inventory\n"
            "  attack [target]      - Attack an NPC or object\n"
            "  help                 - Show this help message"
        )
