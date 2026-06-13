"""Seed data for the initial game world: "The Forgotten Keep".

Provides functions to populate the GameState with rooms, items, and NPCs
for the dark fantasy dungeon keep theme.
"""

from __future__ import annotations

from app.models.game_state import (
    ItemType,
    NPC,
    Player,
    Room,
    GameState,
)


def _create_rooms() -> dict[str, Room]:
    """Create interconnected rooms for The Forgotten Keep."""
    rooms: dict[str, Room] = {}

    # Room 1: Entrance Hall
    entrance = Room(
        id="entrance_hall",
        name="Entrance Hall",
        description=(
            "You stand in a crumbling entrance hall. Moss creeps along the "
            "stone walls, and a broken chandelier hangs from the ceiling. "
            "A heavy oak door leads north, and a narrow passage descends "
            "to the east. The air smells of damp earth and old iron."
        ),
        connections={
            "north": "courtyard",
            "east": "guard_post",
        },
    )
    rooms["entrance_hall"] = entrance

    # Room 2: Courtyard
    courtyard = Room(
        id="courtyard",
        name="Abandoned Courtyard",
        description=(
            "An open courtyard surrounded by crumbling keep walls. "
            "A dry stone fountain sits at the center, filled with leaves. "
            "A wrought-iron gate to the south leads back to the entrance. "
            "Arched doorways lead north to the great hall and east to the armory."
        ),
        connections={
            "south": "entrance_hall",
            "north": "great_hall",
            "east": "armory",
        },
    )
    rooms["courtyard"] = courtyard

    # Room 3: Guard Post
    guard_post = Room(
        id="guard_post",
        name="Old Guard Post",
        description=(
            "A small guard post with a rotted wooden bench. "
            "Rust spikes line the walls where lanterns once hung. "
            "A passage to the west leads back to the entrance hall."
        ),
        connections={
            "west": "entrance_hall",
        },
    )
    rooms["guard_post"] = guard_post

    # Room 4: Great Hall
    great_hall = Room(
        id="great_hall",
        name="The Great Hall",
        description=(
            "A vast hall that once hosted feasts for hundreds. "
            "Long tables are now splintered and covered in dust. "
            "A massive fireplace dominates the far wall. "
            "Doors lead south to the courtyard, west to the library, "
            "and up a flight of stairs to the eastern tower."
        ),
        connections={
            "south": "courtyard",
            "west": "library",
            "up": "tower_stairs",
        },
    )
    rooms["great_hall"] = great_hall

    # Room 5: Armory
    armory = Room(
        id="armory",
        name="The Armory",
        description=(
            "Rows of empty weapon racks line the walls. "
            "A single rusted sword hangs on a peg, and a broken shield "
            "sits on the floor. The air is cold and metallic."
        ),
        connections={
            "west": "courtyard",
        },
    )
    rooms["armory"] = armory

    # Room 6: Library
    library = Room(
        id="library",
        name="The Library",
        description=(
            "Tall bookshelves stretch from floor to ceiling, many collapsed. "
            "Dried ink and crumbling parchment litter the floor. "
            "A desk sits in the center with a leather-bound journal open upon it."
        ),
        connections={
            "east": "great_hall",
        },
    )
    rooms["library"] = library

    # Room 7: Tower Stairs
    tower_stairs = Room(
        id="tower_stairs",
        name="Tower Staircase",
        description=(
            "A spiraling stone staircase winds upward into shadow. "
            "Torch sconces line the wall, most extinguished. "
            "The stairs continue up to the tower chamber."
        ),
        connections={
            "down": "great_hall",
            "up": "tower_chamber",
        },
    )
    rooms["tower_stairs"] = tower_stairs

    # Room 8: Tower Chamber
    tower_chamber = Room(
        id="tower_chamber",
        name="Tower Chamber",
        description=(
            "A circular chamber at the top of the tower. "
            "A narrow window looks out over the dark landscape. "
            "A brass compass sits on a pedestal in the center of the room, "
            "its needle spinning slowly."
        ),
        connections={
            "down": "tower_stairs",
        },
    )
    rooms["tower_chamber"] = tower_chamber

    return rooms


def _create_items() -> dict[str, "Item"]:
    """Create items scattered throughout the keep."""
    from app.models.game_state import Item

    items: dict[str, Item] = {}

    items["rusted_sword"] = Item(
        id="rusted_sword",
        name="Rusted Sword",
        description="A once-fine blade, now corroded by time. Still sharp enough to cut.",
        item_type=ItemType.WEAPON,
        value=15,
        effects={"attack": 5},
    )

    items["health_potion"] = Item(
        id="health_potion",
        name="Health Potion",
        description="A small vial of ruby-red liquid that pulses faintly.",
        item_type=ItemType.POTION,
        value=25,
        effects={"heal": 30},
    )

    items["old_key"] = Item(
        id="old_key",
        name="Iron Key",
        description="A heavy iron key covered in verdigris. Its purpose is unknown.",
        item_type=ItemType.KEY,
        value=10,
        effects={},
    )

    items["shield_broken"] = Item(
        id="shield_broken",
        name="Broken Shield",
        description="A wooden shield with a cracked surface. Still provides some protection.",
        item_type=ItemType.ARMOR,
        value=8,
        effects={"defense": 2},
    )

    items["leather_journal"] = Item(
        id="leather_journal",
        name="Leather Journal",
        description="A weathered journal with cryptic entries about the keep's history.",
        item_type=ItemType.QUEST,
        value=5,
        effects={},
    )

    items["gold_coin"] = Item(
        id="gold_coin",
        name="Gold Coin",
        description="A single gold coin, tarnished but recognizable.",
        item_type=ItemType.MISC,
        value=5,
        effects={},
    )

    items["lantern"] = Item(
        id="lantern",
        name="Oil Lantern",
        description="A brass lantern with just enough oil left to provide light.",
        item_type=ItemType.MISC,
        value=12,
        effects={},
    )

    return items


def _create_npcs() -> dict[str, NPC]:
    """Create NPCs that inhabit the keep."""
    from app.models.game_state import NPC

    npcs: dict[str, NPC] = {}

    npcs["ghost_guard"] = NPC(
        id="ghost_guard",
        name="Captain Aldric",
        description=(
            "A translucent figure in tattered armor stands near the courtyard fountain. "
            "His eyes glow with a faint blue light."
        ),
        location="courtyard",
        dialogue={
            "greeting": (
                "Halt, traveler. I am Captain Aldric, last guardian of this keep. "
                "The dark things lurk in the lower halls. Take the sword and be wary."
            ),
            "farewell": "Go with courage. This forgotten place will remember you.",
            "quest": (
                "Three keys unlock the deeper secrets of the keep. "
                "Find the Iron Key in the armory, the Brass Key in the tower, "
                "and the Silver Key in the library. Together they open the way out."
            ),
        },
        quest_giver=True,
    )

    npcs["shadow_cat"] = NPC(
        id="shadow_cat",
        name="Shadow Cat",
        description=(
            "A sleek black cat with golden eyes watches you from atop the armory wall. "
            "It seems curious but unafraid."
        ),
        location="armory",
        dialogue={
            "greeting": (
                "The cat mews softly and rubs against your leg. "
                "It seems to want you to follow it..."
            ),
            "farewell": "The cat gives you one last piercing look before slinking away.",
        },
        quest_giver=False,
    )

    return npcs


def _assign_items_to_rooms(rooms: dict[str, Room], items: dict[str, Item]) -> None:
    """Place items in their starting rooms."""
    # Entrance Hall: gold coin, lantern
    rooms["entrance_hall"].items = ["gold_coin", "lantern"]

    # Courtyard: health potion
    rooms["courtyard"].items = ["health_potion"]

    # Armory: rusted sword, broken shield, old key
    rooms["armory"].items = ["rusted_sword", "shield_broken", "old_key"]

    # Library: leather journal
    rooms["library"].items = ["leather_journal"]

    # Tower Chamber: nothing extra


def _assign_npcs_to_rooms(rooms: dict[str, Room], npcs: dict[str, NPC]) -> None:
    """Place NPCs in their starting rooms."""
    for npc in npcs.values():
        if npc.location and npc.location in rooms:
            rooms[npc.location].npcs.append(npc.id)


def seed_initial_world() -> GameState:
    """Create and return a fully seeded initial GameState.

    Returns:
        A GameState with rooms, items, NPCs, and a default player
        placed in the entrance hall.
    """
    rooms = _create_rooms()
    items = _create_items()
    npcs = _create_npcs()

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
