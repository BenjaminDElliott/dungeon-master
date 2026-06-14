<<<<<<< HEAD
"""Data models and persistence for Dungeon Master game state.

This module provides:
- Pydantic-compatible dataclasses for game entities (Player, Room, Item, NPC)
- SQLite database schema for persistence
- GameState manager with save/load/update operations
- Seed data for initial world content
"""

from app.models.game_state import Item, NPC, Player, Room, GameState
from app.models.database import GameDatabase, GameDatabaseError
from app.models.seeds import seed_initial_world

__all__ = [
    "Item",
    "NPC",
    "Player",
    "Room",
    "GameState",
    "GameDatabase",
    "GameDatabaseError",
    "seed_initial_world",
]
=======
"""Models package for Dungeon Master RPG."""
>>>>>>> 0a5e73a (feat: implement world design and content creation (LAT-157 Task 4))
