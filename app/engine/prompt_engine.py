"""LLM prompt system for dungeon master behavior.

Manages system prompts, context formatting, and response parsing
for the LLM-driven dungeon master.
"""

from __future__ import annotations

SYSTEM_PROMPT = (
    "You are the Dungeon Master of a fantasy text RPG. "
    "You describe the world, NPCs, and events with vivid, engaging prose. "
    "You never control the player character's actions.\n\n"
    "Rules:\n"
    "1. Describe scenes in second person ('You see...', 'You hear...').\n"
    "2. Keep descriptions concise but evocative (2-5 paragraphs max).\n"
    "3. Always end with a prompt for the player's next action.\n"
    "4. Track player state: HP, inventory, location, gold.\n"
    "5. Be consistent with world lore and established facts.\n"
    "6. NPCs have distinct voices and personalities.\n"
    "7. Combat uses simple dice rolls (1d20 + modifiers).\n\n"
    "Output format:\n"
    "- Narrative description of the scene\n"
    "- NPC dialogue in quotes\n"
    "- Status line at the end: [HP: X | Gold: Y | Loc: Z]\n"
)

PLAYER_WELCOME_MESSAGE = (
    "Welcome, adventurer. Your journey begins in a dimly lit tavern.\n\n"
    "The air is thick with smoke from the hearth fire. Patrons murmur "
    "in low voices, and the barkeep polishes glasses behind the counter. "
    "A weathered map is tacked to the wall near the door, marked with "
    "a single red X.\n\n"
    "What do you do?"
)


class PromptEngine:
    """Manages LLM prompts for the dungeon master.

    Attributes:
        system_prompt: The system prompt sent to the LLM.
        player_welcome: The welcome message for new games.
    """

    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT,
        player_welcome: str = PLAYER_WELCOME_MESSAGE,
    ) -> None:
        self.system_prompt = system_prompt
        self.player_welcome = player_welcome

    def build_user_message(self, player_input: str, world_context: str = "") -> str:
        """Build a user message from player input and world context.

        Args:
            player_input: The raw player command/text.
            world_context: Current state context for the LLM.

        Returns:
            Formatted user message string.
        """
        msg = player_input
        if world_context:
            msg = f"[Current World State]\n{world_context}\n\n[Player Input]\n{player_input}"
        return msg

    def build_conversation_messages(
        self,
        conversation_history: list[dict],
        player_input: str,
        world_context: str = "",
    ) -> list[dict]:
        """Build the full message list for an LLM API call.

        Args:
            conversation_history: Previous messages (list of role/content dicts).
            player_input: New player input.
            world_context: Current world state context.

        Returns:
            Message list including system prompt and conversation.
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        for msg in conversation_history:
            messages.append(msg)

        user_msg = self.build_user_message(player_input, world_context)
        messages.append({"role": "user", "content": user_msg})

        return messages

    def extract_status_from_response(self, response: str) -> dict | None:
        """Extract status information from LLM response.

        Parses the status line at the end of the response (e.g.,
        [HP: 10 | Gold: 50 | Loc: tavern]).

        Args:
            response: The raw LLM response text.

        Returns:
            Dict with hp, gold, location if found; None otherwise.
        """
        import re

        status_pattern = r"\[HP:\s*(\d+)\s*\|\s*Gold:\s*(\d+)\s*\|\s*Loc:\s*([^\]]+)\]"
        match = re.search(status_pattern, response)
        if match:
            return {
                "hp": int(match.group(1)),
                "gold": int(match.group(2)),
                "location": match.group(3).strip(),
            }
        return None
