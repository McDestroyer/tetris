"""A list of tetris-specific functions"""

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


# This is an importer I made for all of my programs going forward so I wouldn't have to deal with
# creating and renaming the personal_functions.py and universal_colors.py for every program
import sys
import os
import time

try:
    from utilities import color
    from utilities import cursor
    from utilities.personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))

    while current.split("\\")[-1] != "tetris":
        current = os.path.dirname(current)
    sys.path.append(current)

    from utilities import color
    from utilities import cursor
    from utilities.personal_functions import *


def print_block(block: list):
    """Temporary program to print out a block.
    Could theoretically be used to print the full screen, albeit inefficiently

    Args:
        block (list): The block to print.
    """
    for i, line in enumerate(block):
        if i < len(block) - 1:
            for elem in line:
                text(elem, end="", mods=[block[-1]], letter_time=0)
            text(letter_time=0)


def rotate_array(shape: list, rotations: int) -> list:
    """Rotate a block a given number of times in the given direction.

    Args:
        shape (list): The block to rotate.
        rotations (int): The direction and number of rotations.
            Positive rotates to the right, negative to the left. 0 makes no change.

    Returns:
        list: The block rotated a given number of times.
    """
    block = shape[:]

    # A rotation algorithm created via. trial and error.
    # I couldn't explain it if I tried, but it seems to work.
    # Loops for the number of rotations specified.
    for _ in range(abs(rotations)):
        rotated = [
            [
                "" for _ in enumerate(block)
            ] for _ in enumerate(block)
        ]

        length = len(block) - 1

        if rotations < 0:
            for i, line in enumerate(block):
                for j, elem in enumerate(line):
                    rotated[length - j][i] = elem
        elif rotations > 0:
            for i, line in enumerate(block):
                for j, elem in enumerate(line):
                    rotated[j][length - i] = elem
        else:
            rotated = block[:]
        block = rotated

    return block


def solidify(grid: list, relevant) -> None:
    """Stop all falling pieces from falling.

    Args:
        grid (list): The positions of everything on the screen.
    """
    for row in grid:
        for square in row:
            if square[0] != "[]":
                square[0] = "██"

    for i in range(len(relevant) - 2):
        relevant[i] = relevant[i + 1]
        relevant[i + 1] = None
        relevant[i].status = i

    for _ in enumerate(relevant):
        try:
            relevant.remove(None)
        except ValueError:
            break


def get_controls() -> dict:
    """Get the controls and map them to the keys in the file.

    Returns:
        dict: The controls and their keys.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, "data")
    path = os.path.join(path, "default_controls.txt")

    file = open(path, "r", encoding="UTF-8")

    file_lines = file.readlines()[:]

    control_map = {}

    for line in file_lines:

        if line.startswith("#"):
            return control_map

        control = line.split("=")

        button = control[1].strip().lower()
        ctrl = control[0].strip().lower()

        if not ctrl in control_map:
            control_map[ctrl] = []

        control_map[ctrl].append(button)

    file.close()

    return control_map


def clear(grid: list) -> None:
    """Clear all falling pieces from falling.

    Args:
        grid (list): The positions of everything on the screen.
    """
    for i, row in enumerate(grid):
        for j, square in enumerate(row):
            if square[0] == "##":
                grid[i][j] = ["██", color.BLACK]


def update_ghost(grid: list, block) -> None:
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


def pause(keyboard_input, controls: dict):
    """Pause the game and run a little pause animation until unpaused.

    Args:
        keyboard_input (module):
            The keyboard_input module, obviously.
        controls (dict):
            The dictionary of controls and their keys.
    """
    cursor.set_pos()
    print("Paused...")
    pause_time = time.monotonic()
    prev_dots = 3
    while not keyboard_input.is_newly_pressed(controls["pause"]):
        dots = int((time.monotonic() - pause_time) % 4)
        if dots != prev_dots:
            cursor.set_pos()
            print("Paused" + "." * dots + " " * (3 - dots))
            prev_dots = dots
    cursor.set_pos()
    print("         ")


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
