"""Tests for Dungeon Master SQLite database layer.

Verifies create, read, save, and load operations for game entities
using a temporary in-memory SQLite database.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.models.database import GameDatabase, GameDatabaseError
from app.models.game_state import (
    ItemType,
    NPC,
    Player,
    Room,
    GameState,
    Item,
)


@pytest.fixture
def db():
    """Create a GameDatabase backed by a temporary SQLite file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as f:
        db = GameDatabase(db_path=f.name)
        db.initialize()
        yield db
        db.close()


@pytest.fixture
def sample_items():
    """Provide sample Item instances."""
    return {
        "sword": Item(
            id="sword",
            name="Rusted Sword",
            description="A corroded blade",
            item_type=ItemType.WEAPON,
            value=15,
            effects={"attack": 5},
        ),
        "potion": Item(
            id="potion",
            name="Health Potion",
            description="Red liquid",
            item_type=ItemType.POTION,
            value=25,
            effects={"heal": 30},
        ),
    }


@pytest.fixture
def sample_npcs():
    """Provide sample NPC instances."""
    return {
        "guard": NPC(
            id="guard",
            name="Captain Aldric",
            description="A ghost in armor",
            location="courtyard",
            dialogue={"greeting": "Halt!"},
            quest_giver=True,
        ),
    }


@pytest.fixture
def sample_rooms():
    """Provide sample Room instances."""
    return {
        "entrance": Room(
            id="entrance",
            name="Entrance Hall",
            description="A crumbling hall.",
            connections={"north": "courtyard"},
        ),
        "courtyard": Room(
            id="courtyard",
            name="Courtyard",
            description="An open courtyard.",
            connections={"south": "entrance"},
        ),
    }


@pytest.fixture
def sample_player():
    """Provide a sample Player instance."""
    return Player(
        id="player-1",
        name="Hero",
        hp=100,
        xp=0,
        gold=10,
        inventory=["sword"],
        current_room="entrance",
    )


# --- Room CRUD ---


class TestRoomCRUD:
    """Tests for Room database operations."""

    def test_create_and_get_room(self, db, sample_rooms):
        """Create a room and retrieve it."""
        db.create_room(sample_rooms["entrance"])
        retrieved = db.get_room("entrance")
        assert retrieved is not None
        assert retrieved.name == "Entrance Hall"
        assert retrieved.connections["north"] == "courtyard"

    def test_get_nonexistent_room(self, db):
        """Getting a room that doesn't exist returns None."""
        result = db.get_room("nonexistent")
        assert result is None

    def test_list_rooms(self, db, sample_rooms):
        """Listing rooms returns all created rooms."""
        for room in sample_rooms.values():
            db.create_room(room)
        rooms = db.list_rooms()
        assert len(rooms) == 2

    def test_create_room_duplicate(self, db, sample_rooms):
        """Creating a room with the same ID replaces the existing one."""
        room = sample_rooms["entrance"]
        db.create_room(room)
        room.connections["east"] = "new_room"
        db.create_room(room)
        retrieved = db.get_room("entrance")
        assert "east" in retrieved.connections


# --- Item CRUD ---


class TestItemCRUD:
    """Tests for Item database operations."""

    def test_create_and_get_item(self, db, sample_items):
        """Create an item and retrieve it."""
        db.create_item(sample_items["sword"])
        retrieved = db.get_item("sword")
        assert retrieved is not None
        assert retrieved.name == "Rusted Sword"
        assert retrieved.item_type == ItemType.WEAPON

    def test_list_items(self, db, sample_items):
        """Listing items returns all created items."""
        for item in sample_items.values():
            db.create_item(item)
        items = db.list_items()
        assert len(items) == 2

    def test_get_nonexistent_item(self, db):
        """Getting an item that doesn't exist returns None."""
        result = db.get_item("nonexistent")
        assert result is None


# --- NPC CRUD ---


class TestNPCCRUD:
    """Tests for NPC database operations."""

    def test_create_and_get_npc(self, db, sample_npcs):
        """Create an NPC and retrieve it."""
        db.create_npc(sample_npcs["guard"])
        retrieved = db.get_npc("guard")
        assert retrieved is not None
        assert retrieved.name == "Captain Aldric"
        assert retrieved.quest_giver is True

    def test_list_npcs(self, db, sample_npcs):
        """Listing NPCs returns all created NPCs."""
        for npc in sample_npcs.values():
            db.create_npc(npc)
        npcs = db.list_npcs()
        assert len(npcs) == 1


# --- Player CRUD ---


class TestPlayerCRUD:
    """Tests for Player database operations."""

    def test_create_and_get_player(self, db, sample_player):
        """Create a player and retrieve it."""
        db.create_player(sample_player)
        retrieved = db.get_player("player-1")
        assert retrieved is not None
        assert retrieved.name == "Hero"
        assert retrieved.hp == 100
        assert retrieved.gold == 10

    def test_get_nonexistent_player(self, db):
        """Getting a player that doesn't exist returns None."""
        result = db.get_player("nonexistent")
        assert result is None


# --- Full Game State Save/Load ---


class TestGameStatePersistence:
    """Tests for full GameState save and load operations."""

    def test_save_and_load_game(self, db, sample_rooms, sample_items, sample_npcs, sample_player):
        """Save a full GameState and load it back."""
        # Build the state
        state = GameState()
        state.player = sample_player
        state.rooms = sample_rooms
        state.items = sample_items
        state.npcs = sample_npcs
        state.turn_count = 3

        # Save
        db.save_game(state)

        # Load
        loaded = db.load_game(state.game_id)
        assert loaded is not None
        assert loaded.game_id == state.game_id
        assert loaded.turn_count == state.turn_count
        assert loaded.player.name == state.player.name
        assert len(loaded.rooms) == len(state.rooms)
        assert len(loaded.items) == len(state.items)
        assert len(loaded.npcs) == len(state.npcs)

    def test_load_nonexistent_game(self, db):
        """Loading a game that doesn't exist returns None."""
        result = db.load_game("nonexistent-game-id")
        assert result is None

    def test_list_saved_games(self, db):
        """Listing saved games returns all saved game IDs."""
        state1 = GameState(game_id="game-1")
        state2 = GameState(game_id="game-2")
        db.save_game(state1)
        db.save_game(state2)

        games = db.list_saved_games()
        assert "game-1" in games
        assert "game-2" in games

    def test_delete_game(self, db):
        """Deleting a game removes it from storage."""
        state = GameState(game_id="to-delete")
        db.save_game(state)

        assert db.delete_game("to-delete") is True
        assert db.load_game("to-delete") is None

    def test_delete_nonexistent_game(self, db):
        """Deleting a nonexistent game returns False."""
        assert db.delete_game("nonexistent") is False

    def test_delete_all_games(self, db):
        """Deleting all games clears the storage."""
        for i in range(3):
            state = GameState(game_id=f"game-{i}")
            db.save_game(state)
        db.delete_all_games()
        assert len(db.list_saved_games()) == 0

    def test_save_load_preserves_item_in_room(self, db):
        """An item's presence in a room persists through save/load."""
        state = GameState()
        state.rooms["room_a"] = Room(
            id="room_a",
            name="Room A",
            connections={"north": "room_b"},
        )
        state.rooms["room_b"] = Room(
            id="room_b",
            name="Room B",
            connections={"south": "room_a"},
        )
        state.items["key"] = Item(id="key", name="Key")
        state.rooms["room_a"].items.append("key")
        state.player = Player(current_room="room_a")

        db.save_game(state)
        loaded = db.load_game(state.game_id)

        assert loaded.rooms["room_a"].items == ["key"]
        assert loaded.items["key"].name == "Key"

    def test_save_load_preserves_npc_in_room(self, db):
        """An NPC's presence in a room persists through save/load."""
        state = GameState()
        state.rooms["room_a"] = Room(
            id="room_a",
            name="Room A",
        )
        state.npcs["guard"] = NPC(
            id="guard",
            name="Guard",
            location="room_a",
        )
        state.rooms["room_a"].npcs.append("guard")
        state.player = Player(current_room="room_a")

        db.save_game(state)
        loaded = db.load_game(state.game_id)

        assert loaded.npcs["guard"].name == "Guard"
        assert loaded.rooms["room_a"].npcs == ["guard"]
