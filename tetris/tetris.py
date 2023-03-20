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


# This is an importer I made for all of my programs going forward so I wouldn't have to deal with
# creating and renaming the personal_functions.py and universal_colors.py for every program.
# Probably adds unnecessary bulk here, but I don't care enough to make it reliable without it.
import sys
import os
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


# Formatting settings (screen size and offset from the left side of the screen so far)
GRID = (10, 24)
FORCAST_PIECES = 3 # Number of future pieces to show on the right.
FRAME_TOP_MATERIAL = "-"
FRAME_SIDE_MATERIAL = "|"
X_Y_OFFSET = (len(FRAME_SIDE_MATERIAL) * 2 + 8 + 3, 1) # (2 for each block [4], frames, and spaces)

# Scores, levels, and life. Only life is implemented as of yet.
score = 0
high_scores = ["Name", "Score"]
level = 1
lines = 0
dead = False

# The delta time (how long each frame should take)
delta_seconds = 1 / 60
delta = delta_seconds * 1_000_000_000

# The time between downward block movements. Scales inversely with level.
g_time = (0.8 - ((level - 1) * 0.007)) ** (level - 1)
previous_g = time.monotonic_ns()

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
relevant_blocks = []



def _main() -> None:
    """Main"""
    initialize()

    while not dead:
        play()


def play():
    """Run the game."""
    start_time = time.monotonic_ns()
    global loop

    # Prints all blocks in all rotations as a test. It works.
    # Left it as a visual representation of action occuring.
    # for b in blocks:
    #     for i in range(4):
    #         print_block(rotate(b, i))

    # Gets keyboard commands and sends the summary of the actions requested to a list.
    commands = listener()
    # print(commands)


    # To be added:
        # Check inputs and decide what needs to be done (keyboard listener WIP)
        # Move blocks


    if "rotate_right" in commands:
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
        relevant_blocks[0].rotate(current_positions, 1)
    elif "rotate_left" in commands:
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
        relevant_blocks[0].rotate(current_positions, -1)

    if "right" in commands:
        relevant_blocks[0].move(current_positions, "right")
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0
    elif "left" in commands:
        relevant_blocks[0].move(current_positions, "left")
        if not relevant_blocks[0].check_dir(current_positions):
            loop = 0

    if "hard_drop" in commands:
        relevant_blocks[0].move(current_positions, "down", True)
        solidify(current_positions, relevant_blocks)
        relevant_blocks[0].move_to(current_positions, [3, 2])
        relevant_blocks[-2] = Tetromino(rand_choice(blocks), [2, 3])
        relevant_blocks[1].visualize(X_Y_OFFSET)
        relevant_blocks[2].visualize(X_Y_OFFSET)
        relevant_blocks[3].visualize(X_Y_OFFSET)
    if "soft_drop" in commands:
        if loop >= 2:
            if relevant_blocks[0].move(current_positions, "down"):
                loop = 0

    if "store" in commands:

        if not relevant_blocks[0].was_held:

            clear(current_positions)

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
        if not relevant_blocks[0].move(current_positions, "down"):
            solidify(current_positions, relevant_blocks)

            relevant_blocks[0].move_to(current_positions, [3, 2])

            relevant_blocks[-2] = Tetromino(rand_choice(blocks), [2, 3])

            relevant_blocks[1].visualize(X_Y_OFFSET)
            relevant_blocks[2].visualize(X_Y_OFFSET)
            relevant_blocks[3].visualize(X_Y_OFFSET)
            # First rotate and move, then apply gravity
            # Apply wallkick rules when applicable
        # Clear lines and give points
            # Add code for combos too
        # Check if leveled up
        # Check if dead

        # Also maybe local multiplayer if I get really bored and we finish too early.

    update_ghost(current_positions, relevant_blocks[0])

    if current_positions != old_positions:
        update_screen_dynamically(current_positions, old_positions)

    # Wait for the delta -- Done!
    delta_wait(start_time)
    loop += 1


def initialize():
    """Set up the screen and variables."""

    loading_screen()

    cursor.hide()

    # Music
    file_location = os.path.dirname(os.path.realpath(__file__))
    audio.play_background(file_location + "/assets/music/Tetris.mp3", -1)

    generate_frame()

    relevant_blocks.append(Tetromino(rand_choice(blocks), [5, 0], 0))
    relevant_blocks.append(Tetromino(rand_choice(blocks), [5, 0], 1))
    relevant_blocks.append(Tetromino(rand_choice(blocks), [5, 0], 2))
    relevant_blocks.append(Tetromino(rand_choice(blocks), [5, 0], 3))
    relevant_blocks.append(Tetromino(blank, [5, 0], 3))
    relevant_blocks[0].move_to(current_positions, [3, 2])
    relevant_blocks[1].visualize(X_Y_OFFSET)
    relevant_blocks[2].visualize(X_Y_OFFSET)
    relevant_blocks[3].visualize(X_Y_OFFSET)
    update_screen_dynamically(current_positions, old_positions)


def loading_screen():
    """Run loading animations."""
    text("Welcome to our Tetris recreation!\n", mods=[color.UNDERLINE, color.GREET])
    intext("Please make the terminal as large as possible to ensure the best possible experience," +
           " then press Enter to start the game...", mods=[color.CYAN])

    logo = [
        "##########  --------  __________  ======    ......    //////  ",
        "    ##      --            __      ==    ==    ..    //        ",
        "    ##      ----          __      ======      ..      //////  ",
        "    ##      --            __      ==  ==      ..            //",
        "    ##      --------      __      ==    ==  ......    //////  "
    ]

    symbol_colors = {
        "#": color.GREEN,
        "-": color.RED,
        "_": color.ERROR,
        "=": color.BLUE,
        ".": color.YELLOW,
        "/": color.CYAN
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
         letter_time=0, flush=True, end="")

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



def listener() -> list:
    """Find out which commands need to be run. Could be later modified to run these commands.

    Returns:
        list: The list of commands to be followed.
    """
    commands = []

    # Designed so if opposing commands are included, they will cancel out.
    if keyboard_input.is_newly_pressed("a"):
        commands.append("left")
    if keyboard_input.is_newly_pressed("d"):
        if "left" not in commands:
            commands.append("right")
        else:
            commands.remove("left")

    if keyboard_input.is_currently_pressed("s"):
        commands.append("soft_drop")
    if keyboard_input.is_newly_pressed("w"):
        commands.append("hard_drop")

    if keyboard_input.is_newly_pressed("j"):
        commands.append("rotate_left")
    if keyboard_input.is_newly_pressed("l"):
        if "rotate left" not in commands:
            commands.append("rotate_right")
        else:
            commands.remove("rotate_left")

    if keyboard_input.is_newly_pressed("i"):
        commands.append("store")

    return commands


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
                        text("[]", mods=[square[1], color.BACKGROUND_BLACK], letter_time=0, end="")
                    else:
                        text("██", mods=[square[1]], letter_time=0, end="")
                    old_pos[i][j] = square[:]
                else:
                    cursor.cursor_right(2)

        cursor.set_pos(X_Y_OFFSET[0]+1, X_Y_OFFSET[1] + i-4 + 2)


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
    else:
        cursor.set_pos()
        print("OVERTIME")



if __name__ == "__main__":
    try:
        # Clears the screen to allow for a cleaner experience before running the program.
        cursor.clear_screen()
        cursor.set_pos()

        _main()
    # :P
    except KeyboardInterrupt:
        audio.stop_music()

        # The 2nd try/except clears all formatting without wasting time
        # so you don't have to wait for it to scroll out.
        try:
            text("CTRL + C?! You're killing me!!! Aww, fine... Bye!", mods=[color.ERROR])
            sys.exit()
        except KeyboardInterrupt:
            text()
            sys.exit()
