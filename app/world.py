"""World module for Dungeon Master RPG.

 Provides the World class that manages the game world including rooms,
 items, NPCs, player position, inventory, and game state.

 The dungeon is a medieval castle with eight interconnected rooms.
 Players explore, collect items, talk to NPCs, and find the Ring of Power.

    entrance_hall --(north)--> guard_post
         |
       (east)
         |
    courtyard --(north)--> great_hall --(west)--> library
         |                       |
       (east)                  (east)
         |                       |
    tower_stairs <--------- armory
         |
       (up)
         |
    tower_chamber
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.models.seeds import (
    get_all_items,
    get_all_npcs,
    get_all_rooms,
    ItemSeed,
    NPCSeed,
    RoomSeed,
)

logger = logging.getLogger(__name__)

# Canonical directions that the game understands.
DIRECTION_ALIASES: dict[str, str] = {
    # Abbreviations
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "u": "up",
    "d": "down",
    # Cardinal directions
    "north": "north",
    "south": "south",
    "east": "east",
    "west": "west",
    "up": "up",
    "down": "down",
    # Ordinal directions
    "northwest": "northwest",
    "northeast": "northeast",
    "southwest": "southwest",
    "southeast": "southeast",
    # Compound directions
    "north-northwest": "northwest",
    "north-northeast": "northeast",
    "south-southwest": "southwest",
    "south-southeast": "southeast",
    # Game-agnostic synonyms
    "forward": "north",
    "backward": "south",
    "left": "west",
    "right": "east",
}

# Reverse mapping for exit descriptions.
DIRECTION_REVERSE: dict[str, str] = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
    "northwest": "southeast",
    "northeast": "southwest",
    "southwest": "northeast",
    "southeast": "northwest",
}


# ========================================================================== #
# Data classes
# ========================================================================== #


@dataclass
class Room:
    """A location in the dungeon world."""

    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[str] = field(default_factory=list)
    npcs: list[str] = field(default_factory=list)
    is_dark: bool = False

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        return f"Room({self.id!r}, name={self.name!r})"


@dataclass
class Item:
    """A carryable item in the game world."""

    id: str
    name: str
    description: str
    is_equippable: bool = False
    is_consumable: bool = False
    is_weapon: bool = False
    damage: int = 0

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        return f"Item({self.id!r}, name={self.name!r})"


@dataclass
class NPC:
    """A non-player character that can be interacted with."""

    id: str
    name: str
    description: str
    dialogue: dict[str, str] = field(default_factory=dict)
    is_hostile: bool = False

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        return f"NPC({self.id!r}, name={self.name!r})"


@dataclass
class GameWorld:
    """Container for all world data — rooms, items, and NPCs."""

    rooms: dict[str, Room] = field(default_factory=dict)
    items: dict[str, Item] = field(default_factory=dict)
    npcs: dict[str, NPC] = field(default_factory=dict)


# ========================================================================== #
# World class — manages game state and player actions
# ========================================================================== #


class World:
    """Manages the game world state for a single player session.

    Supports movement between rooms, item manipulation, examination,
    and NPC interaction. The player starts in the entrance hall
    with an empty inventory.
    """

    def __init__(self, game_world: GameWorld) -> None:
        """Initialize the world from seed data.

        Args:
            game_world: A GameWorld with room, item, and NPC definitions.
        """
        self.rooms = game_world.rooms
        self.items = game_world.items
        self.npcs = game_world.npcs
        self.current_room: str = "entrance_hall"
        self.inventory: list[str] = []
        self._room_item_pools: dict[str, list[str]] = {}
        self._room_npc_pools: dict[str, list[str]] = {}
        self._init_room_pools()

    def _init_room_pools(self) -> None:
        """Store initial item and NPC pools for every room."""
        for room_id, room in self.rooms.items():
            self._room_item_pools[room_id] = list(room.items)
            self._room_npc_pools[room_id] = list(room.npcs)

    def _get_current_room(self) -> Room:
        """Get the Room object for the player's current location."""
        return self.rooms[self.current_room]

    # ---- Player actions ----------------------------------------------------

    def look(self) -> str:
        """Describe the current room in full detail.

        Returns a formatted string including the room name, description,
        available exits, visible items, and present NPCs.
        """
        room = self._get_current_room()
        lines: list[str] = [f"=== {room.name} ===", ""]
        lines.append(room.description)
        lines.append("")
        lines.extend(self.get_exits())
        visible_items = [
            self.items[i] for i in room.items if i in self.items
        ]
        if visible_items:
            names = ", ".join(item.name for item in visible_items)
            lines.append(f"You see: {names}")
        if room.npcs:
            npc_names = [
                self.npcs[n].name for n in room.npcs if n in self.npcs
            ]
            if npc_names:
                lines.append(f"Here: {', '.join(npc_names)}")
        if room.is_dark:
            lines.append("It is dark here.")
        return "\n".join(lines)

    def move(self, direction: str) -> str:
        """Move the player in the given direction.

        Parses the direction, validates the exit exists, updates
        the player position, and returns a description of the new room.
        """
        room = self._get_current_room()
        parsed = self.parse_direction(direction)
        if parsed is None:
            return "I don't understand that direction."
        if parsed not in room.exits:
            return f"You cannot go {parsed} from here."
        new_room_id = room.exits[parsed]
        if new_room_id not in self.rooms:
            logger.warning(
                "Exit '%s' from '%s' leads to unknown room '%s'",
                parsed, self.current_room, new_room_id,
            )
            return "There is no way in that direction."
        self.current_room = new_room_id
        new_room = self.rooms[new_room_id]
        lines: list[str] = []
        if new_room.is_dark:
            lines.append("It is dark. You feel your way forward.")
        lines.append(f"You {parsed} into the {new_room.name}.")
        lines.append("")
        lines.append(self.describe_room())
        return "\n".join(lines)

    def get_exits(self) -> list[str]:
        """Get a list of formatted exit descriptions for the current room."""
        room = self._get_current_room()
        if not room.exits:
            return ["There are no exits from here."]
        exit_lines: list[str] = []
        for direction in sorted(room.exits.keys()):
            target_id = room.exits[direction]
            target_room = self.rooms.get(target_id)
            target_name = target_room.name if target_room else "unknown"
            exit_lines.append(f"  - {direction}: {target_name}")
        return exit_lines

    def get_inventory(self) -> str:
        """Get a formatted string of the player's inventory."""
        if not self.inventory:
            return "You are not carrying anything."
        item_lines: list[str] = []
        for item_id in self.inventory:
            if item_id in self.items:
                item = self.items[item_id]
                item_lines.append(f"  - {item.name}: {item.description}")
        return "Your inventory:\n" + "\n".join(item_lines)

    def take(self, item_name: str) -> str:
        """Take an item from the current room into inventory."""
        room = self._get_current_room()
        item_id = self._find_item_by_name(item_name, room.items)
        if item_id is None:
            return f"There is no '{item_name}' here."
        if item_id not in self.items:
            return f"The '{self.items[item_id].name}' is already gone."
        self.inventory.append(item_id)
        self.items[item_id] = Item(
            id=item_id,
            name=self.items[item_id].name,
            description=self.items[item_id].description,
            is_equippable=self.items[item_id].is_equippable,
            is_consumable=self.items[item_id].is_consumable,
            is_weapon=self.items[item_id].is_weapon,
            damage=self.items[item_id].damage,
        )
        return f"You pick up the {self.items[item_id].name}."

    def drop(self, item_name: str) -> str:
        """Drop an item from inventory onto the current room floor."""
        item_id = self._find_item_in_inventory_by_name(item_name)
        if item_id is None:
            return f"You don't have '{item_name}'."
        room = self._get_current_room()
        if item_id not in room.items:
            room.items.append(item_id)
        self.inventory.remove(item_id)
        return f"You drop the {self.items[item_id].name}."

    def examine(self, target: str) -> str:
        """Examine a room, item, or NPC in detail."""
        target_lower = target.lower().strip()
        if target_lower == "room":
            return self.describe_room()
        room = self._get_current_room()
        item_id = self._find_item_by_name(target_lower, room.items)
        if item_id is not None and item_id in self.items:
            item = self.items[item_id]
            return f"{item.name} — {item.description}"
        if item_id is not None and item_id in self.inventory:
            item = self.items[item_id]
            return f"{item.name} — {item.description}"
        npc_id = self._find_npc_by_name(target_lower, room.npcs)
        if npc_id is not None and npc_id in self.npcs:
            npc = self.npcs[npc_id]
            return f"{npc.name} — {npc.description}"
        return f"There is no '{target}' here to examine."

    def talk(self, npc_name: str, message: str) -> str:
        """Initiate a conversation with an NPC."""
        room = self._get_current_room()
        npc_id = self._find_npc_by_name(npc_name, room.npcs)
        if npc_id is None:
            return f"There is no '{npc_name}' here to talk to."
        npc = self.npcs[npc_id]
        response = npc.dialogue.get(
            message.lower(),
            npc.dialogue.get("*", "Hmm..."),
        )
        return f"{npc.name}: {response}"

    def talk_to(self, npc_name: str) -> str:
        """Start a conversation with an NPC using their greeting."""
        room = self._get_current_room()
        npc_id = self._find_npc_by_name(npc_name, room.npcs)
        if npc_id is None:
            return f"There is no '{npc_name}' here."
        npc = self.npcs[npc_id]
        greeting = npc.dialogue.get("greeting", f"{npc.name} says something.")
        return f"{npc.name}: {greeting}"

    def describe_room(self) -> str:
        """Get the full description of the current room."""
        room = self._get_current_room()
        return f"You are in the {room.name}. {room.description}"

    def world_info(self) -> str:
        """Get a summary of the entire world structure."""
        lines: list[str] = ["=== Dungeon World ===", ""]
        for room_id, room in self.rooms.items():
            exits_str = (
                ", ".join(sorted(room.exits.keys())) if room.exits else "none"
            )
            lines.append(f"  {room.name} ({room_id})")
            lines.append(f"    Exits: {exits_str}")
            lines.append(f"    Items: {len(room.items)}")
            lines.append(f"    NPCs: {len(room.npcs)}")
            lines.append("")
        return "\n".join(lines)

    # ---- Direction parsing -------------------------------------------------

    def parse_direction(self, direction: str) -> Optional[str]:
        """Parse a direction string into a canonical direction."""
        parsed = direction.lower().strip()
        return DIRECTION_ALIASES.get(parsed)

    def is_command(self, text: str) -> bool:
        """Check if a text string is a game command.

        Recognized commands include directions, short aliases, and
        two-word commands like 'take <item>' and 'drop <item>'.
        """
        text = text.strip().lower()
        if text in DIRECTION_ALIASES:
            return True
        if text in (
            "look", "l", "examine", "e", "inventory", "i",
            "help", "h", "world", "w",
        ):
            return True
        parts = text.split(maxsplit=1)
        if parts[0] in ("take", "get", "grab"):
            return len(parts) > 1 and len(parts[1].strip()) > 0
        if parts[0] in ("drop", "throw"):
            return len(parts) > 1 and len(parts[1].strip()) > 0
        if parts[0] in ("talk", "speak", "say"):
            return len(parts) > 1 and len(parts[1].strip()) > 0
        return False

    # ---- Utility methods ---------------------------------------------------

    def help(self) -> str:
        """Display available game commands."""
        lines: list[str] = [
            "=== Commands ===",
            "  look / l       — Look around",
            "  move <dir>     — Move (north, south, east, west, up, down)",
            "  take <item>    — Pick up an item",
            "  drop <item>    — Drop an item",
            "  examine <obj>  — Examine something",
            "  talk <npc>     — Talk to an NPC",
            "  talk <npc> <m> — Speak to an NPC",
            "  inventory / i  — Check inventory",
            "  world / w      — World overview",
            "  help / h       — This help",
        ]
        return "\n".join(lines)

    def status(self) -> str:
        """Display the player's current status and location."""
        room = self._get_current_room()
        lines: list[str] = [
            f"Location: {room.name}",
            f"Exits: {', '.join(room.exits.keys()) if room.exits else 'none'}",
            f"Items carried: {len(self.inventory)}",
        ]
        if self.inventory:
            lines.append(f"Items: {', '.join(self.inventory)}")
        return "\n".join(lines)

    # ---- Internal helpers --------------------------------------------------

    def _find_item_by_name(self, name: str, item_ids: list[str]) -> Optional[str]:
        """Find an item ID by partial name match within a list of IDs."""
        name = name.lower().strip()
        for item_id in item_ids:
            if item_id in self.items:
                if name in self.items[item_id].name.lower():
                    return item_id
        return None

    def _find_item_in_inventory_by_name(self, name: str) -> Optional[str]:
        """Find an item ID by partial name in the player's inventory."""
        name = name.lower().strip()
        for item_id in self.inventory:
            if item_id in self.items:
                if name in self.items[item_id].name.lower():
                    return item_id
        return None

    def _find_npc_by_name(self, name: str, npc_ids: list[str]) -> Optional[str]:
        """Find an NPC ID by partial name match."""
        name = name.lower().strip()
        for npc_id in npc_ids:
            if npc_id in self.npcs:
                if name in self.npcs[npc_id].name.lower():
                    return npc_id
        return None


# ========================================================================== #
# Factory functions
# ========================================================================== #


def create_world() -> GameWorld:
    """Create and return a fully initialized GameWorld from seed data."""
    seed_rooms = get_all_rooms()
    seed_items = get_all_items()
    seed_npcs = get_all_npcs()
    rooms = {r.id: Room(
        id=r.id, name=r.name, description=r.description,
        exits=r.exits, items=r.items, npcs=r.npcs, is_dark=r.is_dark,
    ) for r in seed_rooms}
    items = {i.id: Item(
        id=i.id, name=i.name, description=i.description,
        is_equippable=i.is_equippable, is_consumable=i.is_consumable,
        is_weapon=i.is_weapon, damage=i.damage,
    ) for i in seed_items}
    npcs = {n.id: NPC(
        id=n.id, name=n.name, description=n.description,
        dialogue=n.dialogue, is_hostile=n.is_hostile,
    ) for n in seed_npcs}
    return GameWorld(rooms=rooms, items=items, npcs=npcs)


def create_new_game() -> World:
    """Create a new game instance starting at the entrance hall.

    Returns:
        A World instance with the player at the entrance hall,
        ready for gameplay with an empty inventory.
    """
    game_world = create_world()
    return World(game_world)
