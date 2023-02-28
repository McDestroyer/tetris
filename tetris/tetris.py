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
# creating and renaming the personal_functions.py and universal_colors.py for every program
import sys
import os
import time

try:
    from utilities import color
    from utilities import cursor
    from utilities import animations
    from utilities.personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))

    while current.split("\\")[-1] != "src":
        current = os.path.dirname(current)
    sys.path.append(current)

    from utilities import color
    from utilities import cursor
    from utilities import animations
    from utilities.personal_functions import *

from tetris_functions import *


grid = (10, 24)
LEFT_OFFSET = 5

score = 0
high_scores = ["Name", "Score"]
level = 1
dead = False

loop = 0
delta_seconds = 1 / 60
delta = delta_seconds / 1_000_000_000

g_time = (0.8 - ((level - 1) * 0.007)) ** (level - 1)
previous_g = time.monotonic_ns()

BS = "██"
bl = "  "

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

# Columns in lines
current_positions = [
        [
            ["", color.DEFAULT_COLOR] for _ in range(grid[0])
        ] for _ in range(grid[1])
    ]


def _main() -> None:
    """Main"""
    text("Welcome to our Tetris recreation!", mods=[color.UNDERLINE, color.GREET])
    intext("Press Enter to start the game...")

    initialize()

    while not dead:
        play()


def play():
    """Run the game."""
    global loop
    start_time = time.monotonic_ns()


    for b in blocks:
        for i in range(4):
            print_block(rotate(b, i))
    input()



    # Check inputs
    # Move blocks
    # Check lines
    # Clear and give points
    # Check if dead
    # Wait for the delta
    end_time = time.monotonic_ns()
    real_delta = start_time - end_time
    if real_delta < delta:
        print(real_delta / delta)
        pause_nanoseconds(delta - real_delta)
    else:
        print("OVERTIME")
    loop += 1
    if loop >= 60:
        loop = 0


def initialize():
    """Set up the screen and variables."""
    # Greet
    # Build "screen"


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
