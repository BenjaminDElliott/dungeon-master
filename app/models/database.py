"""SQLite persistence layer for Dungeon Master game state.

Provides the GameDatabase class for CRUD operations on game entities.
Uses raw sqlite3 for simplicity; can be swapped for SQLAlchemy later.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.game_state import Item, NPC, Player, Room, GameState

logger = logging.getLogger(__name__)


class GameDatabaseError(Exception):
    """Base exception for database operations."""


class TableNotFoundError(GameDatabaseError):
    """Raised when a referenced table does not exist."""


class GameDatabase:
    """SQLite database manager for Dungeon Master game state.

    Manages the schema, CRUD operations, and save/load of game entities.
    Uses raw sqlite3 for lightweight persistence.

    Args:
        db_path: Path to the SQLite database file.
    """

    CREATE_TABLES_SQL = """
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            connections TEXT NOT NULL DEFAULT '{}',
            items TEXT NOT NULL DEFAULT '[]',
            npcs TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'misc',
            value INTEGER NOT NULL DEFAULT 0,
            effects TEXT NOT NULL DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS npcs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL DEFAULT '',
            dialogue TEXT NOT NULL DEFAULT '{}',
            quest_giver INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            hp INTEGER NOT NULL DEFAULT 100,
            xp INTEGER NOT NULL DEFAULT 0,
            gold INTEGER NOT NULL DEFAULT 0,
            inventory TEXT NOT NULL DEFAULT '[]',
            current_room TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_states (
            game_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            saved_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_players_current_room ON players(current_room);
        CREATE INDEX IF NOT EXISTS idx_rooms_connections ON rooms(connections);
    """

    def __init__(self, db_path: str = "sqlite:///./dungeon.db") -> None:
        """Initialize the database connection.

        Args:
            db_path: Database URL. Supports sqlite:///./path format.
        """
        self.db_path = db_path.replace("sqlite:///", "")
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection.

        Returns:
            An active sqlite3 Connection.

        Raises:
            GameDatabaseError: If connection cannot be established.
        """
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(self.db_path)
                self._conn.row_factory = sqlite3.Row
                self._conn.execute("PRAGMA foreign_keys = ON")
            except sqlite3.Error as e:
                raise GameDatabaseError(f"Failed to connect to database: {e}")
        return self._conn

    def initialize(self) -> None:
        """Create all tables if they don't exist."""
        conn = self._get_connection()
        conn.executescript(self.CREATE_TABLES_SQL)
        conn.commit()
        logger.info("Database initialized at %s", self.db_path)

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # --- Room operations ---

    def create_room(self, room: Room) -> None:
        """Insert a room into the database.

        Args:
            room: Room dataclass instance.

        Raises:
            GameDatabaseError: If the insert fails.
        """
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO rooms (id, name, description, connections, items, npcs) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    room.id,
                    room.name,
                    room.description,
                    json.dumps(room.connections),
                    json.dumps(room.items),
                    json.dumps(room.npcs),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to create room {room.id}: {e}")

    def get_room(self, room_id: str) -> Optional[Room]:
        """Retrieve a room by ID.

        Args:
            room_id: The room's UUID.

        Returns:
            Room instance or None if not found.
        """
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        if row is None:
            return None
        return Room.from_row(tuple(row))

    def list_rooms(self) -> List[Room]:
        """List all rooms in the database.

        Returns:
            List of Room instances.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM rooms").fetchall()
        return [Room.from_row(tuple(r)) for r in rows]

    # --- Item operations ---

    def create_item(self, item: Item) -> None:
        """Insert an item into the database.

        Args:
            item: Item dataclass instance.
        """
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO items (id, name, description, type, value, effects) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item.id,
                    item.name,
                    item.description,
                    item.item_type.value,
                    item.value,
                    json.dumps(item.effects),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to create item {item.id}: {e}")

    def get_item(self, item_id: str) -> Optional[Item]:
        """Retrieve an item by ID.

        Returns:
            Item instance or None if not found.
        """
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            return None
        return Item.from_row(tuple(row))

    def list_items(self) -> List[Item]:
        """List all items in the database.

        Returns:
            List of Item instances.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM items").fetchall()
        return [Item.from_row(tuple(r)) for r in rows]

    # --- NPC operations ---

    def create_npc(self, npc: NPC) -> None:
        """Insert an NPC into the database.

        Args:
            npc: NPC dataclass instance.
        """
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO npcs (id, name, description, location, dialogue, quest_giver) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    npc.id,
                    npc.name,
                    npc.description,
                    npc.location,
                    json.dumps(npc.dialogue),
                    int(npc.quest_giver),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to create NPC {npc.id}: {e}")

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Retrieve an NPC by ID.

        Returns:
            NPC instance or None if not found.
        """
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM npcs WHERE id = ?", (npc_id,)).fetchone()
        if row is None:
            return None
        return NPC.from_row(tuple(row))

    def list_npcs(self) -> List[NPC]:
        """List all NPCs in the database.

        Returns:
            List of NPC instances.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM npcs").fetchall()
        return [NPC.from_row(tuple(r)) for r in rows]

    # --- Player operations ---

    def create_player(self, player: Player) -> None:
        """Insert a player into the database.

        Args:
            player: Player dataclass instance.
        """
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO players (id, name, hp, xp, gold, inventory, current_room, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    player.id,
                    player.name,
                    player.hp,
                    player.xp,
                    player.gold,
                    json.dumps(player.inventory),
                    player.current_room,
                    player.created_at,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to create player {player.id}: {e}")

    def get_player(self, player_id: str) -> Optional[Player]:
        """Retrieve a player by ID.

        Returns:
            Player instance or None if not found.
        """
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
        if row is None:
            return None
        return Player.from_row(tuple(row))

    # --- Full game state save/load ---

    def save_game(self, state: GameState) -> None:
        """Persist a complete game state to the database.

        Saves the full serialized state as JSON in the game_states table,
        and also persists individual entity rows for queryability.

        Args:
            state: Complete GameState to save.

        Raises:
            GameDatabaseError: If the save fails.
        """
        conn = self._get_connection()
        try:
            state_json = json.dumps(state.to_dict())
            conn.execute(
                "INSERT OR REPLACE INTO game_states (game_id, state_json, saved_at) "
                "VALUES (?, ?, ?)",
                (state.game_id, state_json, state.saved_at),
            )
            conn.commit()
            logger.info("Game state saved for game %s (turn %d)", state.game_id, state.turn_count)
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to save game state: {e}")

    def load_game(self, game_id: str) -> Optional[GameState]:
        """Load a complete game state from the database.

        Args:
            game_id: The game session UUID.

        Returns:
            GameState instance or None if not found.

        Raises:
            GameDatabaseError: If the load fails.
        """
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT state_json FROM game_states WHERE game_id = ?", (game_id,)
            ).fetchone()
            if row is None:
                return None
            data = json.loads(row["state_json"])
            return GameState.from_dict(data)
        except sqlite3.Error as e:
            raise GameDatabaseError(f"Failed to load game state: {e}")

    def list_saved_games(self) -> List[str]:
        """List all saved game IDs.

        Returns:
            List of game_id strings.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT game_id FROM game_states").fetchall()
        return [row["game_id"] for row in rows]

    def delete_game(self, game_id: str) -> bool:
        """Delete a saved game state.

        Args:
            game_id: The game session UUID to delete.

        Returns:
            True if a game was deleted, False if not found.
        """
        conn = self._get_connection()
        cursor = conn.execute("DELETE FROM game_states WHERE game_id = ?", (game_id,))
        conn.commit()
        return cursor.rowcount > 0

    def delete_all_games(self) -> None:
        """Delete all saved game states."""
        conn = self._get_connection()
        conn.execute("DELETE FROM game_states")
        conn.commit()
