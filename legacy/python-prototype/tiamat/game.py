from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Callable, Iterable


ROOTMERE_MAP = [
    "########################################",
    "#..............GGGGGG.................T#",
    "#..............GGGGGG..................#",
    "#....######............................#",
    "#....#H..D#..........~~~~~~............#",
    "#....######..........~~~~~~............#",
    "#....................~~==~~............#",
    "#..........######....~~==~~............#",
    "#..........#L..D#....~~~~~~............#",
    "#..........######......................#",
    "#......................................#",
    "#.....######...............######......#",
    "#.....#S..D#...............#....#......#",
    "#.....######...............#....#......#",
    "#..........................######......#",
    "#........GGGGGG.......................>#",
    "#........GGGGGG........................#",
    "########################################",
]

ROUTE_01_MAP = [
    "########################################",
    "#<......GGGGGG........~~~~~~...........#",
    "#.......GGGGGG........~~~~~~....N......#",
    "#.............######..~~==~~...........#",
    "#..######.............~~==~~....GGGG...#",
    "#..#....#.............~~~~~~....GGGG...#",
    "#..#....#..............................#",
    "#..######...........########...........#",
    "#...................#......#...........#",
    "#.....GGGG..........#......#...........#",
    "#.....GGGG..........#......#...........#",
    "#...................########...........#",
    "#......................................#",
    "#...............######.................#",
    "#...............#....#.................#",
    "#...............#....#.............>...#",
    "#...............######.................#",
    "########################################",
]

THORNWILD_MAP = [
    "########################################",
    "#...............######.................#",
    "#....######.....#....#.....######......#",
    "#....#....#.....#....#.....#....#......#",
    "#....#....#.....######.....#....#......#",
    "#....######................######......#",
    "#......................................#",
    "#...........GGGGGG.....................#",
    "#...........GGGGGG.........~~~~~~......#",
    "#.........................~~==~~.......#",
    "#....N....................~~==~~.......#",
    "#.........................~~~~~~.......#",
    "#......................................#",
    "#..............######..................#",
    "#..............#....#..................#",
    "#..............######...............<..#",
    "#......................................#",
    "########################################",
]

PLAYER_HOME_MAP = [
    "#########",
    "#.......#",
    "#..B....#",
    "#.......#",
    "#...N...#",
    "#...<...#",
    "#########",
]

MORPH_LAB_MAP = [
    "###########",
    "#.........#",
    "#..N...N..#",
    "#.........#",
    "#...C.....#",
    "#.........#",
    "#....<....#",
    "###########",
]

SUPPLY_HUT_MAP = [
    "#########",
    "#.......#",
    "#..N....#",
    "#.......#",
    "#..C....#",
    "#...<...#",
    "#########",
]

PASSABLE_TILES = {".", "G", "D", ">", "<", "="}
ENCOUNTER_RATE = 0.25
VIEWPORT_WIDTH = 20
VIEWPORT_HEIGHT = 10


@dataclass(frozen=True)
class Move:
    name: str
    power: int = 0
    defense_boost: int = 0
    description: str = ""

    @property
    def is_defensive(self) -> bool:
        return self.defense_boost > 0


@dataclass
class Morph:
    name: str
    type_name: str
    role: str
    description: str
    max_hp: int
    attack: int
    defense: int
    moves: tuple[Move, ...]
    hp: int = field(init=False)
    defense_modifier: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.hp = self.max_hp

    @property
    def current_defense(self) -> int:
        return self.defense + self.defense_modifier

    def fresh_copy(self) -> "Morph":
        return Morph(
            name=self.name,
            type_name=self.type_name,
            role=self.role,
            description=self.description,
            max_hp=self.max_hp,
            attack=self.attack,
            defense=self.defense,
            moves=self.moves,
        )


@dataclass(frozen=True)
class MapData:
    name: str
    tiles: tuple[str, ...]
    encounters: bool


@dataclass(frozen=True)
class Transition:
    target_map: str
    target_pos: tuple[int, int]
    name: str
    message: str


STARTERS = {
    "spriglet": Morph(
        name="Spriglet",
        type_name="Nature",
        role="Balanced",
        description="A small leafy Morph with glowing green veins.",
        max_hp=22,
        attack=5,
        defense=4,
        moves=(
            Move("Leaf Tap", power=2, description="Light Nature damage."),
            Move("Root Guard", defense_boost=2, description="Raises defense."),
        ),
    ),
    "cindlet": Morph(
        name="Cindlet",
        type_name="Ember",
        role="Offensive",
        description="A tiny fox-like Morph with a smoldering tail.",
        max_hp=18,
        attack=7,
        defense=3,
        moves=(
            Move("Spark Bite", power=4, description="Medium Ember damage."),
            Move("Ember Puff", power=2, description="Light Ember damage."),
        ),
    ),
    "drizzle": Morph(
        name="Drizzle",
        type_name="Tide",
        role="Defensive",
        description="A round water Morph with ripple markings.",
        max_hp=26,
        attack=4,
        defense=5,
        moves=(
            Move("Bubble Knock", power=2, description="Light Tide damage."),
            Move("Soak Shell", defense_boost=2, description="Raises defense."),
        ),
    ),
}

STARTER_ORDER = ("spriglet", "cindlet", "drizzle")

MAPS = {
    "rootmere": MapData("Rootmere", tuple(ROOTMERE_MAP), encounters=True),
    "route_01": MapData("Route 01", tuple(ROUTE_01_MAP), encounters=True),
    "thornwild": MapData("Thornwild", tuple(THORNWILD_MAP), encounters=True),
    "player_home": MapData("Player Home", tuple(PLAYER_HOME_MAP), encounters=False),
    "morph_lab": MapData("Morph Lab", tuple(MORPH_LAB_MAP), encounters=False),
    "supply_hut": MapData("Supply Hut", tuple(SUPPLY_HUT_MAP), encounters=False),
}

DOORS = {
    "rootmere": {
        (9, 4): Transition(
            target_map="player_home",
            target_pos=(4, 5),
            name="Player Home",
            message="You entered Player Home.",
        ),
        (15, 8): Transition(
            target_map="morph_lab",
            target_pos=(4, 6),
            name="Morph Lab",
            message="You entered Morph Lab.",
        ),
        (10, 12): Transition(
            target_map="supply_hut",
            target_pos=(4, 5),
            name="Supply Hut",
            message="You entered Supply Hut.",
        ),
    }
}

EXITS = {
    "rootmere": {
        (38, 15): Transition(
            target_map="route_01",
            target_pos=(1, 1),
            name="Route 01",
            message="You set out onto Route 01.",
        )
    },
    "route_01": {
        (1, 1): Transition(
            target_map="rootmere",
            target_pos=(37, 15),
            name="Rootmere",
            message="You return to Rootmere.",
        ),
        (35, 15): Transition(
            target_map="thornwild",
            target_pos=(36, 15),
            name="Thornwild",
            message="You arrive in Thornwild.",
        ),
    },
    "thornwild": {
        (36, 15): Transition(
            target_map="route_01",
            target_pos=(33, 15),
            name="Route 01",
            message="You head back toward Route 01.",
        )
    },
    "player_home": {
        (4, 5): Transition(
            target_map="rootmere",
            target_pos=(9, 5),
            name="Rootmere",
            message="You returned to Rootmere.",
        )
    },
    "morph_lab": {
        (4, 6): Transition(
            target_map="rootmere",
            target_pos=(15, 9),
            name="Rootmere",
            message="You returned to Rootmere.",
        )
    },
    "supply_hut": {
        (4, 5): Transition(
            target_map="rootmere",
            target_pos=(10, 13),
            name="Rootmere",
            message="You returned to Rootmere.",
        )
    },
}

INTERACTION_TEXT = {
    ("player_home", "B"): "This is your room. The journey begins here.",
    ("rootmere", "T"): "The Trial Gate is locked. Complete your first Trial later.",
    ("morph_lab", "N"): "Caretaker Vella smiles. The marsh always chooses its Tamers well.",
    ("player_home", "N"): "A folded note reads: The reeds are calm today. Travel far.",
    ("supply_hut", "N"): "The keeper says: Supplies are still being unpacked.",
    ("supply_hut", "C"): "Crates of lantern oil and travel rope sit neatly stacked.",
    ("rootmere", "H"): "Home rests behind the rain-dark boards.",
    ("rootmere", "L"): "The Morph Lab windows glow with patient green light.",
    ("rootmere", "S"): "The supply hut smells like sawdust and sealed crates.",
    ("route_01", "N"): "A patient Tamer says: Thornwild is just ahead if the reeds stay quiet.",
    ("thornwild", "N"): "A traveler whispers: Thornwild wakes early, before the mist lets go.",
}


def calculate_damage(attacker: Morph, move: Move, defender: Morph) -> int:
    if move.power <= 0:
        return 0
    return max(1, attacker.attack + move.power - defender.current_defense)


def apply_move(attacker: Morph, defender: Morph, move: Move) -> str:
    if move.is_defensive:
        previous = attacker.defense_modifier
        attacker.defense_modifier = min(6, attacker.defense_modifier + move.defense_boost)
        if attacker.defense_modifier == previous:
            return f"{attacker.name} is already fully braced."
        return f"{attacker.name} used {move.name}. Defense rose."

    damage = calculate_damage(attacker, move, defender)
    defender.hp = max(0, defender.hp - damage)
    return f"{attacker.name} used {move.name}. {defender.name} took {damage} damage."


class TiamatGame:
    def __init__(
        self,
        *,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
        rng: random.Random | None = None,
    ) -> None:
        self.input = input_func
        self.output = output_func
        self.rng = rng if rng is not None else random.Random()
        self.current_map = "rootmere"
        self.player_x = 7
        self.player_y = 5
        self.starter: Morph | None = None
        self.running = True
        self.message = "Welcome to Rootmere."

    @property
    def map(self) -> tuple[str, ...]:
        return MAPS[self.current_map].tiles

    @property
    def player_position(self) -> tuple[int, int]:
        return self.player_x, self.player_y

    @property
    def starter_status(self) -> str:
        if self.starter is None:
            return "Starter: none"
        return f"Starter: {self.starter.name} ({self.starter.type_name}, HP {self.starter.max_hp})"

    @property
    def starter_chosen(self) -> bool:
        return self.starter is not None

    def run(self) -> None:
        while self.running:
            self.clear_screen()
            self.output(self.render())
            command = self.input("> ").strip().lower()
            self.handle_command(command)

        self.clear_screen()
        self.output("Thanks for visiting Rootmere.")

    def render(self) -> str:
        lines = [f"Tiamat - {MAPS[self.current_map].name}", ""]
        for y, row in self.viewport_rows():
            rendered_row = []
            for x, tile in row:
                rendered_row.append("@" if (x, y) == self.player_position else tile)
            lines.append("".join(rendered_row))

        lines.extend(
            [
                "",
                self.starter_status,
                f"Map: {self.current_map}  Pos: ({self.player_x}, {self.player_y})",
                "Controls: W/A/S/D move, E interact, Q quit",
                "",
                self.message,
            ]
        )
        return "\n".join(lines)

    def viewport_rows(self) -> list[tuple[int, list[tuple[int, str]]]]:
        width = len(self.map[0])
        height = len(self.map)
        start_x = max(0, min(self.player_x - VIEWPORT_WIDTH // 2, width - VIEWPORT_WIDTH))
        start_y = max(0, min(self.player_y - VIEWPORT_HEIGHT // 2, height - VIEWPORT_HEIGHT))
        end_x = min(width, start_x + VIEWPORT_WIDTH)
        end_y = min(height, start_y + VIEWPORT_HEIGHT)

        rows = []
        for y in range(start_y, end_y):
            rows.append((y, [(x, self.map[y][x]) for x in range(start_x, end_x)]))
        return rows

    def handle_command(self, command: str) -> None:
        if command in {"w", "up"}:
            self.try_move(0, -1)
        elif command in {"s", "down"}:
            self.try_move(0, 1)
        elif command in {"a", "left"}:
            self.try_move(-1, 0)
        elif command in {"d", "right"}:
            self.try_move(1, 0)
        elif command in {"e", "interact"}:
            self.interact()
        elif command in {"q", "quit", "exit"}:
            self.running = False
        elif command == "":
            self.message = f"{MAPS[self.current_map].name} waits under a hush of reeds."
        else:
            self.message = "Use W/A/S/D to move, E to interact, or Q to quit."

    def try_move(self, dx: int, dy: int) -> bool:
        next_x = self.player_x + dx
        next_y = self.player_y + dy
        tile = self.tile_at(next_x, next_y)

        if tile is None:
            self.message = "The wetland fog thickens. Best stay on the map."
            return False

        if tile in PASSABLE_TILES:
            self.player_x = next_x
            self.player_y = next_y
            self.after_step(tile)
            return True

        self.message = self.blocked_message(tile)
        return False

    def after_step(self, tile: str) -> None:
        if tile == "G":
            if not MAPS[self.current_map].encounters:
                self.message = "The floorboards are quiet here."
                return
            if self.starter is None:
                self.message = "You should visit the Morph Lab before heading into the grass."
                return
            if self.rng.random() < ENCOUNTER_RATE:
                wild = self.rng.choice(list(STARTERS.values())).fresh_copy()
                self.start_battle(wild)
                return
            self.message = "Wet grass brushes your knees. Nothing stirs."
            return

        if tile == "D":
            self.message = "A doorway waits here. Press E to enter."
            return
        if tile == "<":
            self.message = "Press E to travel back."
            return
        if tile == ">":
            self.message = "The road continues on. Press E to travel."
            return
        if tile == "=":
            self.message = "The bridge creaks softly over dark water."
            return

        self.message = f"You walk through {MAPS[self.current_map].name}."

    def interact(self) -> None:
        current = self.tile_at(self.player_x, self.player_y)
        if current in {"D", "<", ">"} and self.try_transition((self.player_x, self.player_y)):
            return

        for x, y, tile in self.interaction_targets():
            if tile in {"D", "<", ">"} and self.try_transition((x, y)):
                return
            if self.current_map == "morph_lab" and tile == "C":
                self.choose_starter()
                return
            if tile == "N":
                self.message = INTERACTION_TEXT.get((self.current_map, tile), "Someone nods politely.")
                return
            if tile == "B":
                self.message = INTERACTION_TEXT[(self.current_map, "B")]
                return
            if tile == "T":
                self.message = INTERACTION_TEXT[(self.current_map, "T")]
                return
            if tile in {"H", "L", "S", ">", "C"}:
                self.message = INTERACTION_TEXT.get((self.current_map, tile), "You take a closer look.")
                return

        self.message = "You hear Morphs rustling in the grass nearby."

    def interaction_targets(self) -> list[tuple[int, int, str]]:
        offsets = ((0, 0), (0, -1), (1, 0), (0, 1), (-1, 0))
        found = []
        for dx, dy in offsets:
            x = self.player_x + dx
            y = self.player_y + dy
            tile = self.tile_at(x, y)
            if tile is not None:
                found.append((x, y, tile))
        return found

    def try_transition(self, position: tuple[int, int]) -> bool:
        registry = DOORS.get(self.current_map, {})
        if position not in registry:
            registry = EXITS.get(self.current_map, {})
            if position not in registry:
                return False

        transition = registry[position]
        self.current_map = transition.target_map
        self.player_x, self.player_y = transition.target_pos
        self.message = transition.message
        return True

    def tile_at(self, x: int, y: int) -> str | None:
        if y < 0 or y >= len(self.map):
            return None
        if x < 0 or x >= len(self.map[y]):
            return None
        return self.map[y][x]

    def blocked_message(self, tile: str) -> str:
        messages = {
            "#": "Trees and timber walls block the way.",
            "~": "The water is too deep to cross.",
            "H": "Rain-dark boards mark your home. Use the door to enter.",
            "L": "The Morph Lab stands sturdy against the marsh wind.",
            "S": "The supply hut door is set into the front wall.",
            "T": "The Trial Gate is locked. Complete your first Trial later.",
            "B": "Your bed looks warm and impossible to walk through.",
            "C": "The console table hums softly with Morph energy.",
            "N": "You stop short before bumping into someone.",
        }
        return messages.get(tile, "Something blocks the way.")

    def choose_starter(self) -> None:
        if self.current_map != "morph_lab":
            self.message = "Starter selection happens inside the Morph Lab."
            return
        if self.starter is not None:
            self.message = "You already chose your first Morph."
            return

        while True:
            self.clear_screen()
            self.output(self.lab_text())
            choice = self.input("Choose 1, 2, or 3: ").strip().lower()
            key = self.starter_key_from_choice(choice)
            if key is None:
                self.output("That capsule stays shut. Try 1, 2, or 3.")
                self.pause()
                continue

            self.starter = STARTERS[key].fresh_copy()
            self.message = f"{self.starter.name} joins your party."
            return

    def starter_key_from_choice(self, choice: str) -> str | None:
        if choice in {"1", "spriglet"}:
            return "spriglet"
        if choice in {"2", "cindlet"}:
            return "cindlet"
        if choice in {"3", "drizzle"}:
            return "drizzle"
        return None

    def lab_text(self) -> str:
        lines = [
            "Morph Lab Console",
            "",
            "The Morph research table hums softly.",
            "Choose your first Morph:",
            "",
        ]
        for index, key in enumerate(STARTER_ORDER, start=1):
            morph = STARTERS[key]
            move_names = ", ".join(move.name for move in morph.moves)
            lines.extend(
                [
                    f"{index}. {morph.name} - {morph.type_name} / {morph.role}",
                    f"   {morph.description}",
                    f"   HP {morph.max_hp} | ATK {morph.attack} | DEF {morph.defense}",
                    f"   Moves: {move_names}",
                    "",
                ]
            )
        return "\n".join(lines)

    def start_battle(self, wild: Morph) -> None:
        if self.starter is None:
            self.message = "You need a starter before facing wild Morphs."
            return

        player = self.starter.fresh_copy()
        battle_log = f"A wild {wild.name} rustles out of the grass."

        while player.hp > 0 and wild.hp > 0:
            self.clear_screen()
            self.output(self.battle_text(player, wild, battle_log))
            command = self.input("> ").strip().lower()

            if command in {"3", "r", "run"}:
                self.message = f"You slipped away from wild {wild.name}."
                return

            move = self.move_from_battle_command(player, command)
            if move is None:
                battle_log = "Choose 1, 2, or 3."
                continue

            lines = [apply_move(player, wild, move)]
            if wild.hp <= 0:
                self.message = f"Wild {wild.name} is worn out. You return to {MAPS[self.current_map].name}."
                return

            wild_move = self.rng.choice(wild.moves)
            lines.append(apply_move(wild, player, wild_move))
            if player.hp <= 0:
                self.message = f"{player.name} is worn out. You hurry back to the path."
                return

            battle_log = "\n".join(lines)

    def battle_text(self, player: Morph, wild: Morph, battle_log: str) -> str:
        move_1, move_2 = player.moves
        return "\n".join(
            [
                "Wild Morph Battle",
                "",
                f"{wild.name} HP: {wild.hp}/{wild.max_hp} DEF {wild.current_defense}",
                f"{player.name} HP: {player.hp}/{player.max_hp} DEF {player.current_defense}",
                "",
                battle_log,
                "",
                f"1. {move_1.name}",
                f"2. {move_2.name}",
                "3. Run",
            ]
        )

    def move_from_battle_command(self, player: Morph, command: str) -> Move | None:
        if command in {"1", player.moves[0].name.lower()}:
            return player.moves[0]
        if command in {"2", player.moves[1].name.lower()}:
            return player.moves[1]
        return None

    def clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self) -> None:
        self.input("Press Enter to continue...")


def validate_map(rows: Iterable[str]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("Map cannot be empty.")

    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise ValueError("Map rows must all be the same width.")


def validate_maps() -> None:
    for map_data in MAPS.values():
        validate_map(map_data.tiles)


def main() -> None:
    validate_maps()
    TiamatGame().run()
