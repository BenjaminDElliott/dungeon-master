"""Tests for Dungeon Master game state models.

Verifies Player, Room, Item, NPC serialization, GameState operations
(move, take, drop items), and save/load roundtrips.
"""

import json
import uuid
from datetime import datetime, timezone

import pytest

from app.models.game_state import (
    Direction,
    GameState,
    ItemType,
    Item,
    NPC,
    Player,
    Room,
)


# --- Item Tests ---


class TestItem:
    """Tests for the Item dataclass."""

    def test_create_item_defaults(self):
        """An item can be created with default values."""
        item = Item()
        assert item.id is not None
        assert item.name == ""
        assert item.description == ""
        assert item.item_type == ItemType.MISC
        assert item.value == 0
        assert item.effects == {}

    def test_create_item_with_values(self):
        """An item can be created with all fields set."""
        item = Item(
            name="Rusted Sword",
            description="A corroded blade",
            item_type=ItemType.WEAPON,
            value=15,
            effects={"attack": 5},
        )
        assert item.name == "Rusted Sword"
        assert item.item_type == ItemType.WEAPON
        assert item.value == 15
        assert item.effects == {"attack": 5}

    def test_item_serialization_roundtrip(self):
        """An item serializes and deserializes correctly."""
        original = Item(
            name="Health Potion",
            description="Red liquid",
            item_type=ItemType.POTION,
            value=25,
            effects={"heal": 30},
        )
        data = original.to_dict()
        restored = Item.from_dict(data)
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.item_type == original.item_type
        assert restored.value == original.value
        assert restored.effects == original.effects

    def test_item_from_row(self):
        """An item deserializes from a database row."""
        row = (
            "item-1",
            "Test Item",
            "A test item",
            "weapon",
            10,
            json.dumps({"attack": 3}),
        )
        item = Item.from_row(row)
        assert item.id == "item-1"
        assert item.name == "Test Item"
        assert item.item_type == ItemType.WEAPON
        assert item.value == 10
        assert item.effects == {"attack": 3}

    def test_item_from_row_null_effects(self):
        """An item handles null effects in a database row."""
        row = ("item-2", "Test", "Desc", "misc", 0, None)
        item = Item.from_row(row)
        assert item.effects == {}


# --- NPC Tests ---


class TestNPC:
    """Tests for the NPC dataclass."""

    def test_create_npc_defaults(self):
        """An NPC can be created with default values."""
        npc = NPC()
        assert npc.name == ""
        assert npc.dialogue == {}
        assert npc.quest_giver is False

    def test_create_npc_with_dialogue(self):
        """An NPC can have dialogue lines."""
        npc = NPC(
            name="Guard",
            dialogue={
                "greeting": "Halt!",
                "farewell": "Go in peace.",
            },
            quest_giver=True,
        )
        assert npc.dialogue["greeting"] == "Halt!"
        assert npc.quest_giver is True

    def test_npc_serialization_roundtrip(self):
        """An NPC serializes and deserializes correctly."""
        original = NPC(
            name="Merchant",
            dialogue={"greet": "Welcome!"},
        )
        data = original.to_dict()
        restored = NPC.from_dict(data)
        assert restored.name == original.name
        assert restored.dialogue == original.dialogue


# --- Room Tests ---


class TestRoom:
    """Tests for the Room dataclass."""

    def test_create_room_defaults(self):
        """A room can be created with default values."""
        room = Room(name="Test Room")
        assert room.name == "Test Room"
        assert room.connections == {}
        assert room.items == []
        assert room.npcs == []

    def test_create_room_with_connections(self):
        """A room can define connections to other rooms."""
        room = Room(
            name="Entrance",
            connections={"north": "hall", "east": "room2"},
        )
        assert room.connections["north"] == "hall"
        assert room.connections["east"] == "room2"

    def test_room_serialization_roundtrip(self):
        """A room serializes and deserializes correctly."""
        original = Room(
            name="Hall",
            connections={"north": "room2", "south": "room1"},
            items=["sword", "shield"],
            npcs=["npc1"],
        )
        data = original.to_dict()
        restored = Room.from_dict(data)
        assert restored.name == original.name
        assert restored.connections == original.connections
        assert restored.items == original.items
        assert restored.npcs == original.npcs


# --- Player Tests ---


class TestPlayer:
    """Tests for the Player dataclass."""

    def test_create_player_defaults(self):
        """A player can be created with default stats."""
        player = Player(name="Hero")
        assert player.name == "Hero"
        assert player.hp == 100
        assert player.xp == 0
        assert player.gold == 0
        assert player.inventory == []

    def test_player_serialization_roundtrip(self):
        """A player serializes and deserializes correctly."""
        original = Player(
            name="Hero",
            hp=80,
            xp=150,
            gold=50,
            inventory=["sword", "potion"],
            current_room="entrance",
        )
        data = original.to_dict()
        restored = Player.from_dict(data)
        assert restored.name == original.name
        assert restored.hp == original.hp
        assert restored.xp == original.xp
        assert restored.gold == original.gold
        assert restored.inventory == original.inventory
        assert restored.current_room == original.current_room


# --- GameState Tests ---


class TestGameState:
    """Tests for the GameState dataclass."""

    def setup_method(self):
        """Create a minimal GameState for testing."""
        self.state = GameState()
        # Create rooms with connections
        self.state.rooms["room_a"] = Room(
            id="room_a",
            name="Room A",
            description="A plain room.",
            connections={"north": "room_b"},
        )
        self.state.rooms["room_b"] = Room(
            id="room_b",
            name="Room B",
            description="A northern room.",
            connections={"south": "room_a"},
        )
        # Create a player
        self.state.player = Player(
            name="Hero",
            current_room="room_a",
        )
        # Create an item in Room A
        self.state.items["potion"] = Item(
            id="potion",
            name="Health Potion",
            item_type=ItemType.POTION,
            effects={"heal": 30},
        )
        self.state.rooms["room_a"].items.append("potion")

    def test_initial_state(self):
        """A new GameState starts with defaults."""
        state = GameState()
        assert state.turn_count == 0
        assert state.player.hp == 100
        assert state.rooms == {}

    def test_move_player_valid(self):
        """A valid move advances the player."""
        result = self.state.move_player("north", "room_b")
        assert result is True
        assert self.state.player.current_room == "room_b"
        assert self.state.turn_count == 1

    def test_move_player_invalid_direction(self):
        """Moving north when there's no northern connection fails."""
        result = self.state.move_player("north", "room_b")
        assert result is True

        result = self.state.move_player("south", "room_a")
        assert result is True

        result = self.state.move_player("east", "room_b")  # no east from room_b
        assert result is False

    def test_move_player_wrong_destination(self):
        """Moving north to the wrong destination room fails."""
        result = self.state.move_player("north", "room_z")
        assert result is False
        assert self.state.player.current_room == "room_a"

    def test_move_player_no_room(self):
        """Moving when the player is in a non-existent room fails."""
        self.state.player.current_room = "nonexistent"
        result = self.state.move_player("north", "room_b")
        assert result is False

    def test_take_item_from_room(self):
        """The player can pick up an item from the current room."""
        result = self.state.take_item("potion")
        assert result is True
        assert "potion" in self.state.player.inventory
        assert "potion" not in self.state.rooms["room_a"].items
        assert self.state.turn_count == 1

    def test_take_item_not_in_current_room(self):
        """The player cannot pick up an item from another room."""
        # Remove potion from room_a so it only exists in room_b
        self.state.rooms["room_a"].items.remove("potion")
        # Add potion to room_b instead
        self.state.rooms["room_b"].items.append("potion")
        result = self.state.take_item("potion")  # player is in room_a
        assert result is False
        assert "potion" not in self.state.player.inventory

    def test_drop_item_to_room(self):
        """The player can drop an item into the current room."""
        self.state.take_item("potion")
        result = self.state.drop_item("potion")
        assert result is True
        assert "potion" not in self.state.player.inventory
        assert "potion" in self.state.rooms["room_a"].items

    def test_drop_item_not_in_inventory(self):
        """Dropping an item not in inventory fails."""
        result = self.state.drop_item("missing_item")
        assert result is False

    def test_gamestate_serialization_roundtrip(self):
        """The full GameState serializes and deserializes correctly."""
        original_data = self.state.to_dict()
        restored = GameState.from_dict(original_data)

        assert restored.game_id == self.state.game_id
        assert restored.turn_count == self.state.turn_count
        assert restored.player.name == self.state.player.name
        assert restored.player.current_room == self.state.player.current_room

        assert len(restored.rooms) == len(self.state.rooms)
        for room_id, room in self.state.rooms.items():
            assert room_id in restored.rooms
            assert restored.rooms[room_id].name == room.name

        assert len(restored.items) == len(self.state.items)
        for item_id, item in self.state.items.items():
            assert item_id in restored.items
            assert restored.items[item_id].name == item.name

    def test_turn_count_advances_on_move(self):
        """Each valid move increments the turn counter."""
        self.state.move_player("north", "room_b")
        self.state.move_player("south", "room_a")
        assert self.state.turn_count == 2

    def test_game_id_is_uuid(self):
        """A GameState gets a valid UUID as its game_id."""
        state = GameState()
        assert uuid.UUID(state.game_id) is not None


# --- Save/Load Roundtrip Tests ---


class TestSaveLoadRoundtrip:
    """Integration tests for full game state save/load cycles."""

    def test_save_and_load_preserves_all_data(self):
        """Save a GameState and load it back - all data preserved."""
        original = GameState()
        original.rooms["r1"] = Room(id="r1", name="Hall", connections={"north": "r2"})
        original.rooms["r2"] = Room(id="r2", name="Bedroom", connections={"south": "r1"})
        original.items["sword"] = Item(id="sword", name="Sword", item_type=ItemType.WEAPON, effects={"attack": 10})
        original.items["potion"] = Item(id="potion", name="Potion", item_type=ItemType.POTION, effects={"heal": 50})
        original.npcs["guard"] = NPC(id="guard", name="Guard", dialogue={"greet": "Halt!"}, location="r1")
        original.rooms["r1"].npcs.append("guard")
        original.player = Player(name="Hero", hp=75, xp=200, gold=30, current_room="r1", inventory=["sword"])
        original.turn_count = 5
        original.advance_turn()

        data = original.to_dict()
        restored = GameState.from_dict(data)

        assert restored.player.name == original.player.name
        assert restored.player.hp == original.player.hp
        assert restored.player.xp == original.player.xp
        assert restored.player.gold == original.player.gold
        assert restored.player.inventory == original.player.inventory
        assert restored.player.current_room == original.player.current_room
        assert restored.turn_count == original.turn_count
        assert len(restored.rooms) == len(original.rooms)
        assert len(restored.items) == len(original.items)
        assert len(restored.npcs) == len(original.npcs)

    def test_save_load_with_item_transfer(self):
        """Move an item from room to player, save, load, verify."""
        state = GameState()
        state.rooms["start"] = Room(id="start", name="Start")
        state.items["key"] = Item(id="key", name="Key")
        state.rooms["start"].items.append("key")
        state.player = Player(current_room="start")

        # Take the key
        assert state.take_item("key") is True
        assert "key" in state.player.inventory

        # Save and reload
        data = state.to_dict()
        loaded = GameState.from_dict(data)

        assert "key" in loaded.player.inventory
        assert "key" not in loaded.rooms["start"].items
