<<<<<<< HEAD
"""Seed data for the initial game world: "The Forgotten Keep".

Provides functions to populate the GameState with rooms, items, and NPCs
for the dark fantasy dungeon keep theme.
=======
"""Seed data for Dungeon Master RPG.

Contains all room, item, and NPC definitions used to populate the world.
This module provides the canonical source of truth for dungeon content.
>>>>>>> 0a5e73a (feat: implement world design and content creation (LAT-157 Task 4))
"""

from __future__ import annotations

<<<<<<< HEAD
from app.models.game_state import (
    ItemType,
    NPC,
    Player,
    Room,
    GameState,
)


@dataclass
class ItemSeed:
    """Definition of an item that exists in the dungeon world."""

    id: str
    name: str
    description: str
    is_equippable: bool = False
    is_consumable: bool = False
    is_weapon: bool = False
    damage: int = 0


@dataclass
class NPCSeed:
    """Definition of an NPC that exists in the dungeon world."""

    id: str
    name: str
    description: str
    dialogue: dict[str, str] = field(default_factory=dict)
    is_hostile: bool = False


@dataclass
class RoomSeed:
    """Definition of a room in the dungeon world."""

    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[str] = field(default_factory=list)
    npcs: list[str] = field(default_factory=list)
    is_dark: bool = False


# --------------------------------------------------------------------------- #
# Item seeds
# --------------------------------------------------------------------------- #


def get_all_items() -> list[ItemSeed]:
    """Return all item definitions in the dungeon world."""
    return [
        ItemSeed(
            id="rusty_sword",
            name="Rusty Sword",
            description="A rusty old sword. Better than nothing.",
            is_weapon=True,
            is_equippable=True,
            damage=3,
        ),
        ItemSeed(
            id="shield",
            name="Wooden Shield",
            description="A cracked wooden shield.",
            is_equippable=True,
            damage=1,
        ),
        ItemSeed(
            id="torch",
            name="Torch",
            description="A wooden torch soaked in oil. It provides light.",
            is_consumable=False,
        ),
        ItemSeed(
            id="potion",
            name="Health Potion",
            description="A glowing red potion. Restores 5 HP when consumed.",
            is_consumable=True,
        ),
        ItemSeed(
            id="key_golden",
            name="Golden Key",
            description="An ornate golden key. It glows faintly.",
            is_equippable=False,
        ),
        ItemSeed(
            id="scroll",
            name="Ancient Scroll",
            description="A fragile scroll with mysterious symbols.",
            is_consumable=False,
        ),
        ItemSeed(
            id="iron_dagger",
            name="Iron Dagger",
            description="A sharp iron dagger.",
            is_weapon=True,
            is_equippable=True,
            damage=2,
        ),
        ItemSeed(
            id="lantern",
            name="Iron Lantern",
            description="A sturdy iron lantern. Use it to light dark rooms.",
            is_consumable=False,
        ),
        ItemSeed(
            id="mysterious_amulet",
            name="Mysterious Amulet",
            description="A silver amulet etched with runes. It hums with power.",
            is_equippable=True,
        ),
        ItemSeed(
            id="ring_power",
            name="Ring of Power",
            description="A heavy gold ring with a red gemstone.",
            is_equippable=True,
        ),
        ItemSeed(
            id="potion_mana",
            name="Mana Potion",
            description="A blue potion. Restores 3 MP when consumed.",
            is_consumable=True,
        ),
    ]


# --------------------------------------------------------------------------- #
# NPC seeds
# --------------------------------------------------------------------------- #


def get_all_npcs() -> list[NPCSeed]:
    """Return all NPC definitions in the dungeon world."""
    return [
        NPCSeed(
            id="guard_captain",
            name="Captain Aldric",
            description="A seasoned warrior in battered armor.",
            dialogue={
                "greeting": "Hail, adventurer. The dungeon beyond is treacherous.",
                "quest": "Find the Ring of Power in the tower. It was stolen long ago.",
                "farewell": "May fortune smile upon you.",
                "*": "Hmm, I see you looking around.",
            },
        ),
        NPCSeed(
            id="old_sage",
            name="Elder Morwen",
            description="An ancient sage with glowing eyes.",
            dialogue={
                "greeting": "Ah, a new face. You seek knowledge.",
                "quest": "The library holds secrets of the ancients.",
                "farewell": "Remember: knowledge is the greatest weapon.",
                "*": "What is it you wish to know?",
            },
        ),
        NPCSeed(
            id="dark_knight",
            name="Sir Malachar",
            description="A dark knight cloaked in shadows.",
            dialogue={
                "greeting": "Who dares disturb my slumber?",
                "quest": "I have guarded this hall for centuries. Prove your worth.",
                "farewell": "Go now, before I change my mind.",
                "*": "Your courage is noted... for now.",
            },
            is_hostile=True,
        ),
        NPCSeed(
            id="mysterious_vendor",
            name="Trader Elara",
            description="A cheerful merchant with a satchel of wares.",
            dialogue={
                "greeting": "Welcome! Take a look at my fine selection.",
                "quest": "Bring me the Ancient Scroll and I shall reward you well.",
                "farewell": "Safe travels, friend!",
                "*": "Need anything else?",
            },
        ),
        NPCSeed(
            id="tower_wizard",
            name="Archmage Vael",
            description="A tall wizard with a starry robe and staff.",
            dialogue={
                "greeting": "I am Archmage Vael. I have awaited your arrival.",
                "quest": "Retrieve the Mysterious Amulet from the armory.",
                "farewell": "The amulet's power will aid you greatly.",
                "*": "The dungeon holds many secrets yet.",
            },
        ),
    ]


# --------------------------------------------------------------------------- #
# Room seeds
# --------------------------------------------------------------------------- #


    _assign_items_to_rooms(rooms, items)
    _assign_npcs_to_rooms(rooms, npcs)

    player = Player(
        name="Adventurer",
        hp=100,
        xp=0,
        gold=0,
        current_room="entrance_hall",
    )

    return GameState(
        player=player,
        rooms=rooms,
        items=items,
        npcs=npcs,
    )
=======
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ItemSeed:
    """Definition of an item that exists in the dungeon world."""

    id: str
    name: str
    description: str
    is_equippable: bool = False
    is_consumable: bool = False
    is_weapon: bool = False
    damage: int = 0


@dataclass
class NPCSeed:
    """Definition of an NPC that exists in the dungeon world."""

    id: str
    name: str
    description: str
    dialogue: dict[str, str] = field(default_factory=dict)
    is_hostile: bool = False


@dataclass
class RoomSeed:
    """Definition of a room in the dungeon world."""

    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[str] = field(default_factory=list)
    npcs: list[str] = field(default_factory=list)
    is_dark: bool = False


# --------------------------------------------------------------------------- #
# Item seeds
# --------------------------------------------------------------------------- #


def get_all_items() -> list[ItemSeed]:
    """Return all item definitions in the dungeon world."""
    return [
        ItemSeed(
            id="rusty_sword",
            name="Rusty Sword",
            description="A rusty old sword. Better than nothing.",
            is_weapon=True,
            is_equippable=True,
            damage=3,
        ),
        ItemSeed(
            id="shield",
            name="Wooden Shield",
            description="A cracked wooden shield.",
            is_equippable=True,
            damage=1,
        ),
        ItemSeed(
            id="torch",
            name="Torch",
            description="A wooden torch soaked in oil. It provides light.",
            is_consumable=False,
        ),
        ItemSeed(
            id="potion",
            name="Health Potion",
            description="A glowing red potion. Restores 5 HP when consumed.",
            is_consumable=True,
        ),
        ItemSeed(
            id="key_golden",
            name="Golden Key",
            description="An ornate golden key. It glows faintly.",
            is_equippable=False,
        ),
        ItemSeed(
            id="scroll",
            name="Ancient Scroll",
            description="A fragile scroll with mysterious symbols.",
            is_consumable=False,
        ),
        ItemSeed(
            id="iron_dagger",
            name="Iron Dagger",
            description="A sharp iron dagger.",
            is_weapon=True,
            is_equippable=True,
            damage=2,
        ),
        ItemSeed(
            id="lantern",
            name="Iron Lantern",
            description="A sturdy iron lantern. Use it to light dark rooms.",
            is_consumable=False,
        ),
        ItemSeed(
            id="mysterious_amulet",
            name="Mysterious Amulet",
            description="A silver amulet etched with runes. It hums with power.",
            is_equippable=True,
        ),
        ItemSeed(
            id="ring_power",
            name="Ring of Power",
            description="A heavy gold ring with a red gemstone.",
            is_equippable=True,
        ),
        ItemSeed(
            id="potion_mana",
            name="Mana Potion",
            description="A blue potion. Restores 3 MP when consumed.",
            is_consumable=True,
        ),
    ]


# --------------------------------------------------------------------------- #
# NPC seeds
# --------------------------------------------------------------------------- #


def get_all_npcs() -> list[NPCSeed]:
    """Return all NPC definitions in the dungeon world."""
    return [
        NPCSeed(
            id="guard_captain",
            name="Captain Aldric",
            description="A seasoned warrior in battered armor.",
            dialogue={
                "greeting": "Hail, adventurer. The dungeon beyond is treacherous.",
                "quest": "Find the Ring of Power in the tower. It was stolen long ago.",
                "farewell": "May fortune smile upon you.",
                "*": "Hmm, I see you looking around.",
            },
        ),
        NPCSeed(
            id="old_sage",
            name="Elder Morwen",
            description="An ancient sage with glowing eyes.",
            dialogue={
                "greeting": "Ah, a new face. You seek knowledge.",
                "quest": "The library holds secrets of the ancients.",
                "farewell": "Remember: knowledge is the greatest weapon.",
                "*": "What is it you wish to know?",
            },
        ),
        NPCSeed(
            id="dark_knight",
            name="Sir Malachar",
            description="A dark knight cloaked in shadows.",
            dialogue={
                "greeting": "Who dares disturb my slumber?",
                "quest": "I have guarded this hall for centuries. Prove your worth.",
                "farewell": "Go now, before I change my mind.",
                "*": "Your courage is noted... for now.",
            },
            is_hostile=True,
        ),
        NPCSeed(
            id="mysterious_vendor",
            name="Trader Elara",
            description="A cheerful merchant with a satchel of wares.",
            dialogue={
                "greeting": "Welcome! Take a look at my fine selection.",
                "quest": "Bring me the Ancient Scroll and I shall reward you well.",
                "farewell": "Safe travels, friend!",
                "*": "Need anything else?",
            },
        ),
        NPCSeed(
            id="tower_wizard",
            name="Archmage Vael",
            description="A tall wizard with a starry robe and staff.",
            dialogue={
                "greeting": "I am Archmage Vael. I have awaited your arrival.",
                "quest": "Retrieve the Mysterious Amulet from the armory.",
                "farewell": "The amulet's power will aid you greatly.",
                "*": "The dungeon holds many secrets yet.",
            },
        ),
    ]


# --------------------------------------------------------------------------- #
# Room seeds
# --------------------------------------------------------------------------- #


def get_all_rooms() -> list[RoomSeed]:
    """Return all room definitions in the dungeon world."""
    return [
        # ---- entrance_hall ----------------------------------------------------
        RoomSeed(
            id="entrance_hall",
            name="Entrance Hall",
            description="You stand in a large entrance hall. Cobwebs drape the ceiling "
            "and a stone flagstone floor stretches before you. Faint light filters "
            "through a high arched window.",
            exits={
                "north": "guard_post",
                "east": "courtyard",
            },
            items=["torch"],
            npcs=["guard_captain"],
        ),
        # ---- guard_post -------------------------------------------------------
        RoomSeed(
            id="guard_post",
            name="Guard Post",
            description="A small guard post with a wooden desk and a flickering "
            "candle. A notice board on the wall lists duty rosters from days "
            "long past. A draft blows through a crack in the wall.",
            exits={
                "south": "entrance_hall",
            },
            items=["rusty_sword"],
            npcs=["dark_knight"],
        ),
        # ---- courtyard ---------------------------------------------------------
        RoomSeed(
            id="courtyard",
            name="Courtyard",
            description="An open-air courtyard surrounded by crumbling walls. "
            "A dry fountain stands in the centre, filled with leaves and debris. "
            "Vines climb the walls from above.",
            exits={
                "west": "entrance_hall",
                "north": "great_hall",
                "east": "tower_stairs",
            },
            items=["lantern"],
            npcs=["mysterious_vendor"],
        ),
        # ---- great_hall --------------------------------------------------------
        RoomSeed(
            id="great_hall",
            name="Great Hall",
            description="A vast great hall with a soaring ceiling supported by "
            "stone pillars. Long tables are arranged in rows, their surfaces "
            "covered in dust and decay. Tapestries line the walls.",
            exits={
                "south": "courtyard",
                "west": "library",
                "east": "armory",
            },
            items=["shield", "potion"],
            npcs=["old_sage"],
        ),
        # ---- library -----------------------------------------------------------
        RoomSeed(
            id="library",
            name="Library",
            description="A dusty library with towering shelves of ancient tomes. "
            "The air smells of parchment and old ink. A reading desk stands "
            "in the centre of the room with an open book resting upon it.",
            exits={
                "east": "great_hall",
            },
            items=["scroll", "potion_mana"],
            npcs=[],
        ),
        # ---- armory ------------------------------------------------------------
        RoomSeed(
            id="armory",
            name="Armory",
            description="A long armory with racks of weapons on the walls. "
            "The floor is covered in scattered armour pieces and broken swords. "
            "A workbench sits in the corner with tools and a half-sharpened blade.",
            exits={
                "west": "great_hall",
            },
            items=["iron_dagger", "key_golden"],
            npcs=[],
        ),
        # ---- tower_stairs ------------------------------------------------------
        RoomSeed(
            id="tower_stairs",
            name="Tower Stairs",
            description="A spiral stone staircase winds upward into the gloom. "
            "The steps are worn smooth by centuries of feet. A single shaft "
            "of light pierces the darkness from above.",
            exits={
                "west": "courtyard",
                "up": "tower_chamber",
            },
            items=["mysterious_amulet"],
            npcs=["tower_wizard"],
        ),
        # ---- tower_chamber -----------------------------------------------------
        RoomSeed(
            id="tower_chamber",
            name="Tower Chamber",
            description="A circular chamber at the top of the tower. Starlight "
            "streams through a round window. The walls are covered in glowing "
            "runes that pulse faintly. The Ring of Power sits on a stone pedestal.",
            exits={
                "down": "tower_stairs",
            },
            items=["ring_power"],
            npcs=[],
        ),
    ]
>>>>>>> 0a5e73a (feat: implement world design and content creation (LAT-157 Task 4))
