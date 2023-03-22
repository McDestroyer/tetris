"""
File: generic.py
Name: Jason Fanger
ID: X00504571
Desc: A generic function containing my default functions.
"""

# These get rid of annoying errors that usually mean nothing.
# Remove non-import related ones if seriously struggling


# pylint: disable=unused-import
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unexpected-keyword-arg
# pylint: disable=no-member
# pylint: disable=ungrouped-imports
# pylint: disable=undefined-variable
# pylint: disable=invalid-name
# pylint: disable=global-statement
# pylint: disable=global-at-module-level
# pylint: disable=dangerous-default-value


# This is an importer I made for all of my programs going forward so I wouldn't have to deal with
# creating and renaming the personal_functions.py and universal_colors.py for every program.
# Probably adds unnecessary bulk here, but I don't care enough to make it reliable without it.
import string
import subprocess
import sys
import os
import threading
import time

try:
    import color
    import cursor
    import animations
    import audio
    import keyboard_input
    from personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))

    while current.split("\\")[-1] != "tetris":
        current = os.path.dirname(current)
    sys.path.append(os.path.join(current, "utilities"))

    import color
    import cursor
    import animations
    import audio
    import keyboard_input
    from personal_functions import *

from tetrominos import *
import top_score


# Formatting settings (screen size and offset from the left side of the screen so far)
GRID = (10, 24)
FORCAST_PIECES = 3 # Number of future pieces to show on the right.
FRAME_TOP_MATERIAL = "-"
FRAME_SIDE_MATERIAL = "|"
X_Y_OFFSET = (len(FRAME_SIDE_MATERIAL) * 2 + 8 + 3, 1) # (2 for each block [4], frames, and spaces)

# Scores, levels, and life.
global score
score = 0
global combo
combo = 0
global difficult_combo
difficult_combo = -1
global tspin
tspin = 0

global level
level = 1
global level_goal
level_goal = 5

global lines
lines = 0

dead = False

# The delta time (how long each frame should take)
delta_seconds = 1 / 60
delta = delta_seconds * 1_000_000_000

# The time between downward block movements. Scales inversely with level.
g_time = (0.8 - ((level - 1) * 0.007)) ** (level - 1)

# The current loop and the loop on which to move down.
global loop
loop = 0
g_loop = rounder(g_time * (1 / delta_seconds))

# The symbols used to represent a filled or empty square
BS = "##"
bl = ""

# The list of tetrominoes. The grids are shaped so they rotate correctly around the center.
blocks = [
    [
        [bl, bl, bl, bl],
        [BS, BS, BS, BS], # [][][][]
        [bl, bl, bl, bl],
        [bl, bl, bl, bl],
        color.rgb_hex("00", "ff", "ff") # Cyan
    ],
    [
        [BS, bl, bl], # []
        [BS, BS, BS], # [][][]
        [bl, bl, bl],
        color.rgb_hex("00", "00", "ff") # Blue
    ],
    [
        [bl, bl, BS], #     []
        [BS, BS, BS], # [][][]
        [bl, bl, bl],
        color.rgb_hex("ff", "7f", "00") # Orange
    ],
    [
        [bl, BS, bl], #   []
        [BS, BS, BS], # [][][]
        [bl, bl, bl],
        color.rgb_hex("80", "00", "80") # Purple
    ],
    [
        [bl, bl, bl, bl],
        [bl, BS, BS, bl], # [][]
        [bl, BS, BS, bl], # [][]
        [bl, bl, bl, bl],
        color.rgb_hex("ff", "ff", "00") # Yellow
    ],
    [
        [bl, BS, BS], #   [][]
        [BS, BS, bl], # [][]
        [bl, bl, bl],
        color.rgb_hex("00", "ff", "00") # Green
    ],
    [
        [BS, BS, bl], # [][]
        [bl, BS, BS], #   [][]
        [bl, bl, bl],
        color.rgb_hex("ff", "00", "00") # Red
    ]
]

blank = [
        [bl, bl, bl, bl],
        [bl, bl, bl, bl],
        [bl, bl, bl, bl],
        [bl, bl, bl, bl],
        color.BLACK
]
# This is the screen grid of squares and their colors
# The outer list is the list of horizontal lines. The inner list is the relevant column entries.
# Example: [0][0] is the top left, [4][3] is the 5th item down and the 4th item across.
current_positions = [
        [
            ["██", color.BLACK] for _ in range(GRID[0])
        ] for _ in range(GRID[1])
    ]
old_positions = [
        [
            ["██", color.BLACK] for _ in range(GRID[0])
        ] for _ in range(GRID[1])
    ]
global relevant_blocks
relevant_blocks = []



def clear_lines (grid: list) -> int:
    """Clear any full lines and return the number cleared.

    Args:
        grid (list):
            The current positions of everything.

    Returns:
        int: The number of lines cleared.
    """
    cleared_lines = 0
    for _, row in enumerate(grid):
        can_clear = True
        for _, square in enumerate(row):
            if square[0] in ("##", "[]"):
                can_clear = False

        if (not ["██", color.BLACK] in row) and can_clear:
            empty_line = [["██", color.BLACK] for _ in enumerate(row)]
            grid.remove(row)
            grid.insert(0, empty_line)
            cleared_lines += 1

    return cleared_lines



def _main() -> None:
    """Main"""
    initialize()

    while not dead:
        play()


def play():
    """Run the game."""
    start_time = time.monotonic_ns()
    global loop
    global score
    global tspin

    # Gets keyboard commands and sends the summary of the actions requested to a list.
    commands = listener()
    if "rotate_right" in commands:
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
        spin, rotated = relevant_blocks[0].rotate(current_positions, 1)
        if rotated:
            tspin = spin
    elif "rotate_left" in commands:
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
        spin, rotated = relevant_blocks[0].rotate(current_positions, -1)
        if rotated:
            tspin = spin

    if "right" in commands:
        _, move = relevant_blocks[0].move(current_positions, "right")
        if move:
            tspin = 0
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
    elif "left" in commands:
        _, move = relevant_blocks[0].move(current_positions, "left")
        if move:
            tspin = 0
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0

    if "hard_drop" in commands:
        distance, _ = relevant_blocks[0].move(current_positions, "down", True)
        score += distance * 2
        if distance > 0:
            tspin = 0
        solidify(current_positions, relevant_blocks)
        if len(relevant_blocks) < 6:
            add_seven()
        sleep(0.1)
        relevant_blocks[0].move_to(current_positions, [3, 2])
        relevant_blocks[1].visualize(X_Y_OFFSET)
        relevant_blocks[2].visualize(X_Y_OFFSET)
        relevant_blocks[3].visualize(X_Y_OFFSET)
    if "soft_drop" in commands:
        if loop >= 2:
            _, success = relevant_blocks[0].move(current_positions, "down")
            if success:
                tspin = 0
                score += 1
                loop = 0

    if "store" in commands:

        if not relevant_blocks[0].was_held:

            clear(current_positions)
            sleep(0.1)

            tspin = 0

            relevant_blocks[-1], relevant_blocks[0] = relevant_blocks[0], relevant_blocks[-1]
            relevant_blocks[-1].was_held = True
            relevant_blocks[-1].status = -1
            relevant_blocks[0].status = 0

            if relevant_blocks[0].shape == blank[:-1]:
                for i in range(len(relevant_blocks) - 2):
                    relevant_blocks[i] = relevant_blocks[i + 1]
                    relevant_blocks[i].status = i

            relevant_blocks[0].move_to(current_positions, [3, 2])
            relevant_blocks[-2] = Tetromino(rand_choice(blocks), [2, 3])

            relevant_blocks[-1].visualize(X_Y_OFFSET)
            relevant_blocks[1].visualize(X_Y_OFFSET)
            relevant_blocks[2].visualize(X_Y_OFFSET)
            relevant_blocks[3].visualize(X_Y_OFFSET)

    # Gravity
    if loop >= g_loop:
        loop = 0
        _, fell = relevant_blocks[0].move(current_positions, "down")
        if not fell:
            solidify(current_positions, relevant_blocks)
            if len(relevant_blocks) < 6:
                add_seven()

            sleep(0.1)

            relevant_blocks[0].move_to(current_positions, [3, 2])

            relevant_blocks[-2] = Tetromino(rand_choice(blocks), [2, 3])

            relevant_blocks[1].visualize(X_Y_OFFSET)
            relevant_blocks[2].visualize(X_Y_OFFSET)
            relevant_blocks[3].visualize(X_Y_OFFSET)
        else:
            tspin = 0

        # Also maybe local multiplayer if I get really bored and we finish too early.

    update_ghost(current_positions, relevant_blocks[0])

    global lines
    global difficult_combo
    global combo

    cleared_lines = clear_lines(current_positions)
    lines += cleared_lines

    if cleared_lines == 1:
        score += 100 * level * (1.5 if difficult_combo >= 1 and tspin != 0 else 1)

        if tspin != 0:
            if tspin == 1:
                score += 200 * level * (1.5 if difficult_combo >= 1 else 1)
                difficult_combo += 1
            elif tspin == 2:
                score += 800 * level * (1.5 if difficult_combo >= 1 else 1)
                difficult_combo += 1
        else:
            difficult_combo = -1

        if is_clear(current_positions):
            score += 800 * level

        combo += 1
        score += 50 * combo * level

    elif cleared_lines == 2:
        score += 300 * level * (1.5 if difficult_combo >= 1 and tspin != 0 else 1)

        if tspin != 0:
            if tspin == 1:
                score += 400 * level * (1.5 if difficult_combo >= 1 else 1)
                difficult_combo += 1
            elif tspin == 2:
                score += 1200 * level * (1.5 if difficult_combo >= 1 else 1)
                difficult_combo += 1
        else:
            difficult_combo = -1

        if is_clear(current_positions):
            score += 1200 * level

        combo += 1
        score += 50 * combo * level

    elif cleared_lines == 3:
        score += 500 * level * (1.5 if difficult_combo >= 1 and tspin != 0 else 1)

        if tspin != 0:
            if tspin == 2:
                score += 1600 * level * (1.5 if difficult_combo >= 1 else 1)
                difficult_combo += 1
        else:
            difficult_combo = -1

        if is_clear(current_positions):
            score += 1800 * level

        combo += 1
        score += 50 * combo * level

    elif cleared_lines == 4:
        score += 800 * level * (1.5 if difficult_combo >= 1 else 1)
        difficult_combo += 1
        combo += 1
        score += 50 * combo * level

        if is_clear(current_positions):
            score += 2000 * level * (1.6 if difficult_combo >= 1 else 1)

    else:
        combo = -1

        if tspin == 1:
            score += 100 * level
        elif tspin == 2:
            score += 400 * level

    level_up()

    score = int(score)

    update_score()
    update_level()
    update_lines(level_goal)

    if current_positions != old_positions:
        update_screen_dynamically(current_positions, old_positions)

    if check_death(current_positions):
        death_animation(current_positions, False)

    if level == 20:
        death_animation(current_positions, True)

    # Wait for the delta -- Done!
    delta_wait(start_time)
    loop += 1


def initialize():
    """Set up the screen and variables."""

    try:
        sys.argv[1]
    except IndexError:
        loading_screen()

    cursor.hide()

    # Music
    file_location = os.path.dirname(os.path.realpath(__file__))

    music_files = ["Tetris", "russian"]

    random_number = rand(100)
    if random_number <= 4:
        file = music_files[1]
    else:
        file = music_files[0]

    audio.play_background(file_location + f"/assets/music/{file}.mp3", -1)

    generate_frame()


    relevant_blocks.append(Tetromino(blank, [5, 0], 3))
    add_seven()

    relevant_blocks[0].move_to(current_positions, [3, 2])
    relevant_blocks[1].visualize(X_Y_OFFSET)
    relevant_blocks[2].visualize(X_Y_OFFSET)
    relevant_blocks[3].visualize(X_Y_OFFSET)
    update_screen_dynamically(current_positions, old_positions)


def add_seven():
    """Randomize the order of the 7 tetrominos and add them to the queue."""
    global relevant_blocks
    # Remove the end
    held = relevant_blocks[-1]
    relevant_blocks = relevant_blocks[:-1]

    # Generate and shuffle the seven
    seven = []
    for b in blocks:
        seven.append(Tetromino(b, [5, 0], 0))

    seven = shuffle(seven, 100)

    for i, b in enumerate(seven):
        b.status = len(relevant_blocks) + i

    # Add them back
    relevant_blocks += seven
    relevant_blocks.append(held)


def loading_screen():
    """Run loading animations."""
    text("Welcome to our Tetris recreation!\n", mods=[color.UNDERLINE, color.GREET])
    intext("Please make the terminal as large as possible to ensure the best possible experience," +
           " then press Enter to start the game...", mods=[color.CYAN])

    logo = [
        "##########  --------  __________  ======    ......  //////  ",
        "    ##      --            __      ==    ==    ..    //        ",
        "    ##      ----          __      ======      ..    //////  ",
        "    ##      --            __      ==  ==      ..        //",
        "    ##      --------      __      ==    ==  ......  //////  "
    ]

    symbol_colors = {
        "#": color.rgb_hex("ff", "00", "00"),
        "-": color.rgb_hex("ff", "7f", "00"),
        "_": color.rgb_hex("ff", "ff", "00"),
        "=": color.rgb_hex("00", "ff", "00"),
        ".": color.rgb_hex("00", "00", "ff"),
        "/": color.rgb_hex("80", "00", "80")
    }

    animations.drop_down(logo, symbol_colors, 5, 20, "█")
    sleep(2)
    cursor.cursor_down()
    text(" " * 28 + "Loading...")
    animations.loading_v3(message="", loading_time=7.5, length=50, message_mods=[color.GREEN],
                          container_mods=[color.RED], bar_mods=[color.BLUE],
                          percent_mods=[color.YELLOW], percent=True)


def generate_frame():
    """Draw the gameplay screen."""


    # Main


    # Build "screen" frame
    cursor.clear_screen()

    x = X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1)
    y = X_Y_OFFSET[1] - 1

    cursor.set_pos(x + 1, y + 1)

    # Top of frame
    text(FRAME_TOP_MATERIAL * (GRID[0] * 2 + (len(FRAME_SIDE_MATERIAL) + 1) * 2),
         letter_time=0, flush=False)

    # Walls of frame and grid
    for i in range(GRID[1] - 4):
        cursor.cursor_right(X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1))
        text(FRAME_SIDE_MATERIAL, end=" ", letter_time=0, flush=False)

        for j in range(GRID[0]):
            text(current_positions[i][j][0], end="", letter_time=0,
                 flush=False, mods=[current_positions[i][j][1]])

        text(" " + FRAME_SIDE_MATERIAL, letter_time=0, flush=False)

    # Bottom of frame
    cursor.cursor_right(X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1))
    text(FRAME_TOP_MATERIAL * (GRID[0] * 2 + (len(FRAME_SIDE_MATERIAL) + 1) * 2),
         letter_time=0, flush=False)


    # Hold


    cursor.set_pos()
    cursor.cursor_down(X_Y_OFFSET[1] - 1)

    text(FRAME_TOP_MATERIAL * rounder((((X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1))- 4) / 2)),
         letter_time=0, flush=False, end="")

    text("HOLD", letter_time=0, flush=False, end="")

    text(FRAME_TOP_MATERIAL * (rounder((((X_Y_OFFSET[0] -
         (len(FRAME_SIDE_MATERIAL) + 1))- 4) / 2)) - 1),
         letter_time=0, flush=False, end="")

    # Walls of hold and empty contents
    for i in range(4):

        cursor.cursor_down()
        cursor.beginning()

        text(FRAME_SIDE_MATERIAL, end=" ", letter_time=0, flush=False)

        text("██" * 4, end="", letter_time=0, flush=False, mods=[color.BLACK])

    cursor.cursor_down()
    cursor.beginning()

    text(FRAME_TOP_MATERIAL * (X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1)),
         letter_time=0, flush=False, end="")


    # Next up


    for i in range(FORCAST_PIECES):

        y = X_Y_OFFSET[1] + (5 * i)

        x = X_Y_OFFSET[0] + GRID[0] * 2 + len(FRAME_SIDE_MATERIAL) + 1

        cursor.set_pos(x + 1, y + 1)

        if i == 0:

            text(FRAME_TOP_MATERIAL * (2 + 1), letter_time=0, flush=False, end="")

            text("NEXT", letter_time=0, flush=False, end="")

            text(FRAME_TOP_MATERIAL * (2 + 1 + len(FRAME_SIDE_MATERIAL)),
                letter_time=0, flush=False, end="")

        else:

            text(FRAME_TOP_MATERIAL * (8 + 2 + len(FRAME_SIDE_MATERIAL)),
                letter_time=0, flush=False, end="")

        for _ in range(4):

            cursor.cursor_down()
            cursor.beginning()
            cursor.cursor_right(X_Y_OFFSET[0] + GRID[0] * 2 + len(FRAME_SIDE_MATERIAL) + 1)

            text(" " + "██" * 4, end="", letter_time=0, flush=False, mods=[color.BLACK])
            text(f" {FRAME_SIDE_MATERIAL}", end="", letter_time=0, flush=False)

        # End cap the forcast

        if i + 1 == FORCAST_PIECES:

            cursor.cursor_down()
            cursor.beginning()
            cursor.cursor_right(X_Y_OFFSET[0] + GRID[0] * 2 + len(FRAME_SIDE_MATERIAL) + 1)

            text(FRAME_TOP_MATERIAL * (8 + 2 + len(FRAME_SIDE_MATERIAL)),
                letter_time=0, flush=False, end="")


    # Stats


    # Score

    y = X_Y_OFFSET[1] + 5
    cursor.set_pos(0, y + 1)
    val_len = len(str(score))

    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")
    text("SCORE", letter_time=0, flush=False, end="")
    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")

    cursor.cursor_down()
    cursor.beginning()

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(score, letter_time=0, flush=False, end="")

    # Level

    cursor.cursor_down()
    cursor.beginning()

    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")
    text("LEVEL", letter_time=0, flush=False, end="")
    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")

    cursor.cursor_down()
    cursor.beginning()

    val_len = len(str(level))

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(level, letter_time=0, flush=False, end="")

    # Lines

    cursor.cursor_down()
    cursor.beginning()

    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")
    text("LINES", letter_time=0, flush=False, end="")
    text(FRAME_TOP_MATERIAL * int(5 + len(FRAME_TOP_MATERIAL) - 3),
         letter_time=0, flush=False, end="")

    cursor.cursor_down()
    cursor.beginning()

    val_len = len(str(lines))

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(lines, letter_time=0, flush=False, end="")

    # Wrap it up

    cursor.cursor_down()
    cursor.beginning()

    text(FRAME_TOP_MATERIAL * (X_Y_OFFSET[0] - (len(FRAME_SIDE_MATERIAL) + 1)),
         letter_time=0, flush=True, end="")


def listener(ctrls: dict = None) -> list:
    """Find out which commands need to be run. Could be later modified to run these commands.

    Returns:
        list: The list of commands to be followed.
    """
    ctrls = get_controls()
    commands = []

    # Designed so if opposing commands are included, they will cancel out.
    if keyboard_input.is_long_pressed(ctrls["left"], speed = 3):
        commands.append("left")
    if keyboard_input.is_long_pressed(ctrls["right"], speed = 3):
        if "left" not in commands:
            commands.append("right")
        else:
            commands.remove("left")

    if keyboard_input.is_currently_pressed(ctrls["soft_drop"]):
        commands.append("soft_drop")
    if keyboard_input.is_newly_pressed(ctrls["hard_drop"]):
        commands.append("hard_drop")

    if keyboard_input.is_newly_pressed(ctrls["rotate_left"]):
        commands.append("rotate_left")
    if keyboard_input.is_newly_pressed(ctrls["rotate_right"]):
        if "rotate left" not in commands:
            commands.append("rotate_right")
        else:
            commands.remove("rotate_left")

    if keyboard_input.is_newly_pressed(ctrls["store"]):
        commands.append("store")

    return commands


def get_controls() -> dict:
    """Get the controls and map them to the keys in the file.

    Returns:
        dict: The controls and their keys.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, "data")
    path = os.path.join(path, "controls.txt")

    file = open(path, "r", encoding="UTF-8")

    file_lines = file.readlines()[:]

    control_map = {}

    for line in file_lines:
        control = line.split("=")
        if control[0].startswith("#"):
            return control_map
        control_map[control[0].strip()] = control[1].strip().lower()

    file.close()

    return control_map


def update_ghost(grid: list, block: Tetromino) -> None:
    """Create a ghostly image of the falling block and update its position.

    Args:
        grid (list):
            The current positions of everything.
        block (Tetromino):
            The block to make a ghost of.
    """

    # Clear the previous ghost.
    for i, row in enumerate(grid):
        for j, square in enumerate(row):
            if square[0] == "[]":
                grid[i][j] = ["██", color.BLACK]

    # Feel out distances and find the shortest.
    distance = 25
    for i, row in enumerate(grid):
        for j, square in enumerate(row):
            if square[0] == "##":
                distance = min(ghost_dist_find(grid, i, j), distance)

    # Spawn a new piece of one wherever there's a falling block.
    for i, row in enumerate(grid):
        for j, square in enumerate(row):
            if square[0] == "##":
                ghost_fall(grid, i, j, block.color, distance)


def ghost_dist_find(grid: list, start_y: int, x_pos: int) -> int:
    """Find the distance the ghost piece can fall.

    Args:
        grid (list):
            The current positions of everything.
        start_y (int):
            The height of the piece of block being checked.
        x_pos (int):
            The x-axis to check on.

    Returns:
        int: The distance the piece could fall.
    """
    dist = 0
    if not start_y == len(grid) - 1:
        for i in range(start_y, len(grid) - 1):
            # If the blelow square is [] or neither black nor ## (A solid block),
            # that's how far this one can go, so return it.
            if (grid[i + 1][x_pos][0] == "[]" or
                (grid[i + 1][x_pos][1] != color.BLACK and
                grid[i + 1][x_pos][0] != "##")):
                return dist
            dist += 1
    # If it doesn't find anything, put it on the floor.
    return len(grid) - 1 - start_y


def ghost_fall(grid: list, start_y: int, x_pos: int, ghost_color: str, dist: int):
    """Make the ghost block fall until it lands on something.

    Args:
        grid (list):
            The current positions of everything.
        start_y (int):
            The height of the piece of block being checked.
        x_pos (int):
            The x-axis to check on.
        ghost_color (str):
            The color of the block.
        dist (int):
            The distance down to move.

    Returns:
        int: The distance down moved.
    """
    if not start_y == len(grid) - 1:

        if grid[start_y + dist][x_pos][0] != "##":
            grid[start_y + dist][x_pos] = ["[]", ghost_color]


def update_score():
    """Put the current score on the screen."""
    y = X_Y_OFFSET[1] + 5
    cursor.set_pos(0, y + 2)
    val_len = len(str(score))

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(score, letter_time=0, flush=False, end="")


def update_level():
    """Put the current level on the screen."""
    y = X_Y_OFFSET[1] + 5 + 2
    cursor.set_pos(0, y + 2)
    val_len = len(str(level))

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(level, letter_time=0, flush=False, end="")


def update_lines(level_up_num):
    """Put the current number of cleared lines on the screen."""
    y = X_Y_OFFSET[1] + 5 + 2 + 2
    cursor.set_pos(0, y + 2)

    val_len = len(str(lines) + "/" + str(level_up_num))

    text(FRAME_SIDE_MATERIAL, letter_time=0, flush=False, end=" ")

    text(" " * int(4 - val_len / 2), letter_time=0, flush=False, end="")
    text(str(lines) + "/" + str(level_up_num), letter_time=0, flush=False, end="")


def level_up():
    """Check and level up if enough levels have been aquired.

    Args:
        current_level (int):
            The current level.
        current_lines (int):
            The current number of lines.
        level_up_num (int):
            The number of lines needed to level up.
        gravity_loop (int):
            g_loop.
        gravity_time (float):
            g_time.
    """
    global level_goal
    if lines >= level_goal:
        global level
        level_goal += 5 * level
        level += 1
        global g_time
        global g_loop
        g_time = (0.8 - ((level - 1) * 0.007)) ** (level - 1)
        g_loop = rounder(g_time * (1 / delta_seconds))


def is_clear(grid: list) -> bool:
    """Check to see if the screen has been fully cleared.

    Args:
        grid (list):
            The current positions of everything.

    Returns:
        bool: True if the screen is empty. False otherwise.
    """
    for _, row in enumerate(grid):
        for _, square in enumerate(row):
            if square[0] == "██" and square[1] != color.BLACK:
                return False
    return True


def check_death(grid: list) -> bool:
    """Check to see if you are dead.

    Args:
        grid (list):
            The current positions of everything.

    Returns:
        bool: Dead?
    """
    for i in range(4):
        for j in range(10):
            if grid[i][j][0] == "██" and grid[i][j][1] != color.BLACK:
                return True
    return False


def update_screen_dynamically(current_pos: list, old_pos: list) -> None:
    """Update the screen by only replacing the parts that are different.

    Args:
        current_pos (list):
            The screen modified during this frame.
        old_pos (list):
            The state of the screen from the end of the last frame.
    """
    cursor.set_pos(X_Y_OFFSET[0]+1, X_Y_OFFSET[1])

    for i, row in enumerate(current_pos):

        if i > 3:

            for j, square in enumerate(row):
                if square != old_pos[i][j]:
                    if square[0] == "[]":
                        text("[]", mods=[square[1], color.BACKGROUND_BLACK],
                             letter_time=0, end="", flush=False)
                    else:
                        text("██", mods=[square[1]], letter_time=0, end="", flush=False)
                    old_pos[i][j] = square[:]
                else:
                    cursor.cursor_right(2)

        cursor.set_pos(X_Y_OFFSET[0]+1, X_Y_OFFSET[1] + i-4 + 2)
    print("", end="", flush=True)


def delta_wait(start_time: int):
    """Pause for a short period to rate-limit the game and framerate.

    Args:
        start_time (int): The time at which the loop began.
        loop (int): The current loop (used primarily for gravity)
    """
    end_time = time.monotonic_ns()
    real_delta = end_time - start_time
    if real_delta < delta:
        pause_nanoseconds(delta - real_delta)
        cursor.set_pos()
        print("        ")
    else:
        cursor.set_pos()
        print("OVERTIME")


def death_animation(grid: list, state: bool) -> None:
    """Generate the death message.

    Args:
        grid (list):
            The current positions of everything.
    """
    audio.stop_music()
    sleep(.5)
    for i, row in enumerate(grid):
        for j, square in enumerate(row):
            if square[0] == "██" and square[1] != color.BLACK or square[0] == "##":
                grid[i][j][1] = color.BRIGHT_BLACK
            elif square[0] == "[]":
                grid[i][j] = ["██", color.BLACK]

        update_screen_dynamically(grid, old_positions)
        sleep(.25)

    sleep(1)

    cursor.set_pos(2, 2)
    text("██" * 22, letter_time=0, end="", mods=[color.WHITE])
    for i in range(18):
        cursor.set_pos(2, 3 + i)
        text("██" * 1, letter_time=0, end="", mods=[color.WHITE])
        text("  " * 20, letter_time=0, end="")
        text("██" * 1, letter_time=0, end="", mods=[color.WHITE])
    cursor.set_pos(2, 4 + i)
    text("██" * 22, letter_time=0, end="", mods=[color.WHITE])

    y = 4
    x = 6

    cursor.set_pos(x, y)
    if state is False:
        died = "YOU LOST"
        cursor.cursor_right(18 - int(len(died) / 2))
        text(died, end="", mods=[color.RED])
    else:
        won = "YOU WON!"
        cursor.cursor_right(18 - int(len(won) / 2))
        text(won, end="", mods=[color.BRIGHT_GREEN])

    y += 3
    cursor.set_pos(x, y)

    high_scores = top_score.get_scores()
    high = False

    if score > high_scores[4][2]:
        text("New Highscore!!!", end="", mods=[color.BRIGHT_YELLOW, color.UNDERLINE])
        text(" ", end="", mods=[color.BRIGHT_YELLOW])
        high = True

    text(f"Score: {score}", end="", mods=[color.GREEN])

    y += 1
    cursor.set_pos(x, y)
    text(f"Lines Cleared: {lines}", end="", mods=[color.GREEN])

    y += 1
    cursor.set_pos(x, y)
    text(f"Level Reached: {level}", end="", mods=[color.GREEN])

    cursor.set_pos(x, y + 4)
    text("High Scores:", end="", mods=[color.BRIGHT_YELLOW])

    num = -1
    mod_scores = []
    for i, val in enumerate(high_scores):

        if score > val[2] and num == -1:
            mod_scores.append([i + 1, "___", score])
            num = i

        mod_scores.append(val)


        if len(mod_scores) >= 5:
            mod_scores = mod_scores[:5]
            break


    for i, val in enumerate(mod_scores):
        cursor.set_pos(x, y + 6 + i)
        text(f"{val[1]}: {val[2]}", end="", mods=[color.BRIGHT_BLUE])


    y += 2
    cursor.set_pos(x, y)
    # text("Please Hit Enter...", end="", mods=[color.CYAN])

    thread = threading.Thread(target=keybd.simulate, args=("enter", .02))
    thread.start()

    cursor.set_pos(0, 25)
    st = time.monotonic_ns()
    while time.monotonic_ns() < st + 10_000_000:
        input()
        cursor.cursor_up()

    cursor.set_pos(0, 24)
    cursor.clear_screen_after()

    cursor.set_pos(x, y)

    if high:
        text("Please enter your initials below:", mods=[color.CYAN])
        cursor.set_pos(x, y + 4 + num)
        initials = input(color.BRIGHT_BLUE).upper()

        initials += "-" * max((3 - len(initials)), 0)
        initials = initials[:3]
        initials = initials.replace(" ", "-")

        top_score.add_score(initials, score, high_scores)

    cursor.set_pos(x, y)
    text(" " * 36, end="")
    cursor.set_pos(x, y)
    text("Hit enter to play again!", end="", mods=[color.CYAN])

    cursor.set_pos(0, 25)
    input()

    python = sys.executable

    args = [python, "tetris.py", "false"]

    # os.execl(python, python, *arg)
    subprocess.call(args)


if __name__ == "__main__":
    try:
        # Clears the screen to allow for a cleaner experience before running the program.
        cursor.clear_screen()
        cursor.set_pos()

        _main()
    # :P
    except KeyboardInterrupt:

        # Pretty self-explanitory...
        audio.stop_music()

        # The 2nd try/except clears all formatting without wasting time
        # so you don't have to wait for it to scroll out.
        try:
            cursor.set_pos()
            text("CTRL + C?! You're killing me!!! Aww, fine... Bye!", mods=[color.ERROR])
            sys.exit()
        except KeyboardInterrupt:
            text()
            sys.exit()
