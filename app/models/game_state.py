"""Pydantic-compatible dataclasses for Dungeon Master game entities.

Defines the core domain model: Player, Room, Item, NPC, and GameState.
All models support JSON serialization for save/load roundtrips.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class Direction(str, Enum):
    """Valid movement directions."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"


class ItemType(str, Enum):
    """Types of items in the game."""

    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    KEY = "key"
    QUEST = "quest"
    MISC = "misc"


@dataclass
class Item:
    """A game item that can be carried by a player.

    Attributes:
        id: Unique identifier for this item.
        name: Display name of the item.
        description: Flavour text describing the item.
        item_type: Categorical type of the item.
        value: Gold value of the item.
        effects: Dictionary of stat modifications when used/equipped.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    item_type: ItemType = ItemType.MISC
    value: int = 0
    effects: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for database storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Item:
        """Deserialize from dictionary."""
        if "item_type" in data:
            data["item_type"] = ItemType(data["item_type"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_row(cls, row: tuple) -> Item:
        """Deserialize from a database row (id, name, description, type, value, effects_json)."""
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            item_type=ItemType(row[3]) if row[3] else ItemType.MISC,
            value=row[4] or 0,
            effects=json.loads(row[5]) if row[5] else {},
        )


@dataclass
class NPC:
    """A non-player character the player can interact with.

    Attributes:
        id: Unique identifier for this NPC.
        name: Display name of the NPC.
        description: Flavour text describing the NPC's appearance.
        location: Room ID where this NPC is currently located.
        dialogue: Pre-written dialogue lines keyed by topic/intent.
        quest_giver: Whether this NPC offers quests.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    location: str = ""
    dialogue: Dict[str, str] = field(default_factory=dict)
    quest_giver: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for database storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NPC:
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_row(cls, row: tuple) -> NPC:
        """Deserialize from a database row."""
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            location=row[3] or "",
            dialogue=json.loads(row[4]) if row[4] else {},
            quest_giver=bool(row[5]),
        )


@dataclass
class Room:
    """A room/location in the game world.

    Attributes:
        id: Unique identifier for this room.
        name: Display name of the room.
        description: Atmospheric description shown to the player.
        connections: Dictionary mapping directions to destination room IDs.
        items: List of item IDs present in this room.
        npcs: List of NPC IDs present in this room.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    connections: Dict[str, str] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for database storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Room:
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_row(cls, row: tuple) -> Room:
        """Deserialize from a database row (id, name, description, connections_json, items_json, npcs_json)."""
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            connections=json.loads(row[3]) if row[3] else {},
            items=json.loads(row[4]) if row[4] else [],
            npcs=json.loads(row[5]) if row[5] else [],
        )


@dataclass
class Player:
    """The player character.

    Attributes:
        id: Unique identifier (player name/identifier).
        name: Display name of the player character.
        hp: Current hit points (max 100).
        xp: Experience points earned.
        gold: Amount of gold carried.
        inventory: List of item IDs the player is carrying.
        current_room: Room ID where the player is currently located.
        created_at: Timestamp when the player was created.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    hp: int = 100
    xp: int = 0
    gold: int = 0
    inventory: List[str] = field(default_factory=list)
    current_room: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for database storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Player:
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_row(cls, row: tuple) -> Player:
        """Deserialize from a database row."""
        return cls(
            id=row[0],
            name=row[1],
            hp=row[2] or 100,
            xp=row[3] or 0,
            gold=row[4] or 0,
            inventory=json.loads(row[5]) if row[5] else [],
            current_room=row[6] or "",
            created_at=row[7] or datetime.now(timezone.utc).isoformat(),
        )


@dataclass
class GameState:
    """Complete game state encompassing player, world, and metadata.

    This is the top-level object serialized for save/load operations.
    It contains the player's current state and a snapshot of the world.

    Attributes:
        player: The player character.
        rooms: Dictionary of all rooms in the world keyed by room ID.
        items: Dictionary of all items keyed by item ID.
        npcs: Dictionary of all NPCs keyed by NPC ID.
        game_id: Unique identifier for this game session.
        turn_count: Number of turns taken in this session.
        saved_at: Timestamp when this state was saved.
    """

    player: Player = field(default_factory=Player)
    rooms: Dict[str, Room] = field(default_factory=dict)
    items: Dict[str, Item] = field(default_factory=dict)
    npcs: Dict[str, NPC] = field(default_factory=dict)
    game_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_count: int = 0
    saved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the entire game state to a dictionary."""
        return {
            "player": self.player.to_dict(),
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "items": {k: v.to_dict() for k, v in self.items.items()},
            "npcs": {k: v.to_dict() for k, v in self.npcs.items()},
            "game_id": self.game_id,
            "turn_count": self.turn_count,
            "saved_at": self.saved_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GameState:
        """Deserialize from dictionary."""
        return cls(
            player=Player.from_dict(data["player"]),
            rooms={k: Room.from_dict(v) for k, v in data.get("rooms", {}).items()},
            items={k: Item.from_dict(v) for k, v in data.get("items", {}).items()},
            npcs={k: NPC.from_dict(v) for k, v in data.get("npcs", {}).items()},
            game_id=data.get("game_id", str(uuid.uuid4())),
            turn_count=data.get("turn_count", 0),
            saved_at=data.get("saved_at", datetime.now(timezone.utc).isoformat()),
        )

    def advance_turn(self) -> None:
        """Advance the turn counter."""
        self.turn_count += 1

    def move_player(self, direction: str, destination_room_id: str) -> bool:
        """Move the player to a connected room.

        Args:
            direction: Direction string (north, south, etc.).
            destination_room_id: Target room ID.

        Returns:
            True if the move was valid, False otherwise.
        """
        current_room = self.rooms.get(self.player.current_room)
        if current_room is None:
            return False

        valid_directions = {d.value for d in Direction}
        if direction not in valid_directions:
            return False

        if direction not in current_room.connections:
            return False

        if current_room.connections[direction] != destination_room_id:
            return False

        self.player.current_room = destination_room_id
        self.advance_turn()
        return True

    def take_item(self, item_id: str) -> bool:
        """Pick up an item from the current room.

        Args:
            item_id: ID of the item to pick up.

        Returns:
            True if the item was successfully picked up.
        """
        room = self.rooms.get(self.player.current_room)
        if room is None or item_id not in room.items:
            return False

        if item_id not in self.items:
            return False

        room.items.remove(item_id)
        if item_id not in self.player.inventory:
            self.player.inventory.append(item_id)
        self.advance_turn()
        return True

    def drop_item(self, item_id: str) -> bool:
        """Drop an item from the player's inventory into the current room.

        Args:
            item_id: ID of the item to drop.

        Returns:
            True if the item was successfully dropped.
        """
        if item_id not in self.player.inventory:
            return False

        player_item = self.items.get(item_id)
        if player_item is None:
            return False

        self.player.inventory.remove(item_id)
        room = self.rooms.get(self.player.current_room)
        if room is not None and item_id not in room.items:
            room.items.append(item_id)
        self.advance_turn()
        return True
