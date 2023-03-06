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


# This is an importer I made for all of my programs going forward so I wouldn't have to deal with
# creating and renaming the personal_functions.py and universal_colors.py for every program.
# Probably adds unnecessary bulk here, but I don't care enough to make it reliable without it.
import sys
import os
import time

try:
    from utilities import color
    from utilities import cursor
    from utilities import animations
    from utilities import audio
    from utilities import keyboard_input
    from utilities.personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))

    while current.split("\\")[-1] != "tetris":
        current = os.path.dirname(current)
    sys.path.append(current)

    from utilities import color
    from utilities import cursor
    from utilities import animations
    from utilities import audio
    from utilities import keyboard_input
    from utilities.personal_functions import *

from tetris_functions import *

# Formatting settings (screen size and offset from the left side of the screen so far)
grid = (10, 24)
LEFT_OFFSET = 5

# Scores, levels, and life. Only life is implemented as of yet.
score = 0
high_scores = ["Name", "Score"]
level = 1
dead = False

# The delta time (how long each frame should take)
delta_seconds = 1 / 60
delta = delta_seconds / 1_000_000_000

# The time between downward block movements. Scales inversely with level.
g_time = (0.8 - ((level - 1) * 0.007)) ** (level - 1)
previous_g = time.monotonic_ns()

# The current loop and the loop on which to move down.
loop = 0
g_loop = rounder(g_time * (1 / delta_seconds))

# The symbols used to represent a filled or empty square
BS = "██"
bl = "  "

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
        [BS, BS], # [][]
        [BS, BS], # [][]
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

# This is the screen grid of squares and their colors
# The outer list is the list of horizontal lines. The inner list is the relevant column entries.
# Example: [0][0] is the bottom left, [4][3] is the 5th item up and the 4th item across.
current_positions = [
        [
            ["  ", color.DEFAULT_COLOR] for _ in range(grid[0])
        ] for _ in range(grid[1])
    ]


def _main() -> None:
    """Main"""
    text("Welcome to our Tetris recreation!\n", mods=[color.UNDERLINE, color.GREET])
    intext("Press Enter to start the game...", mods=[color.CYAN])

    initialize()

    while not dead:
        play()


def play():
    """Run the game."""
    start_time = time.monotonic_ns()

    # Prints all blocks in all rotations as a test. It works.
    # Left it as a visual representation of action occuring.
    for b in blocks:
        for i in range(4):
            print_block(rotate(b, i))

    # Gets keyboard commands and sends the summary of the actions requested to a list.
    commands = listener()
    print(commands)


    # To be added:
        # Check inputs and decide what needs to be done (keyboard listener WIP)
        # Move blocks
            # First rotate and move, then apply gravity
            # Apply wallkick rules when applicable
        # Clear lines and give points
            # Add code for combos too
        # Check if leveled up
        # Check if dead

        # Also maybe local multiplayer if I get really bored and we finish too early.


    # Wait for the delta -- Done!
    delta_wait(start_time, loop)


def initialize():
    """Set up the screen and variables."""
    animations.loading_v3()
    audio.play_background("tetris/assets/music/Tetris.mp3", -1)
    # Build "screen" frame


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
        commands.append("soft drop")
    if keyboard_input.is_newly_pressed("w"):
        commands.append("hard drop")

    if keyboard_input.is_newly_pressed("j"):
        commands.append("rotate left")
    if keyboard_input.is_newly_pressed("l"):
        if "rotate left" not in commands:
            commands.append("rotate right")
        else:
            commands.remove("rotate left")

    if keyboard_input.is_newly_pressed("i"):
        commands.append("store")

    return commands


def delta_wait(start_time: int, current_loop: int):
    """Pause for a short period to rate-limit the game and framerate.

    Args:
        start_time (int): The time at which the loop began.
        loop (int): The current loop (used primarily for gravity)
    """
    end_time = time.monotonic_ns()
    real_delta = start_time - end_time
    if real_delta < delta:
        pause_nanoseconds(delta - real_delta)
    else:
        print("OVERTIME")

    current_loop += 1


if __name__ == "__main__":
    try:
        # Clears the screen to allow for a cleaner experience before running the program.
        cursor.clear_screen()

        _main()
    # :P
    except KeyboardInterrupt:
        # The 2nd try/except clears all formatting without wasting time
        # so you don't have to wait for it to scroll out.
        try:
            text("CTRL + C?! You're killing me!!! Aww, fine... Bye!", mods=[color.ERROR])
            sys.exit()
        except KeyboardInterrupt:
            text()
            sys.exit()
