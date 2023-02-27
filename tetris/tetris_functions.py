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

try:
    import utilities.cursor as cursor
    import utilities.win_vsc_color as color
    from utilities.personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))

    while current.split("\\")[-1] != "src":
        current = os.path.dirname(current)
    sys.path.append(current)

    import utilities.cursor as cursor
    import utilities.win_vsc_color as color
    from utilities.personal_functions import *


def print_block(block: list):
    """Temporary program to print out a block.
    Could theoretically be used to print the screen, albeit inefficiently

    Args:
        block (list): The block to print.
    """
    for i, line in enumerate(block):
        if i < len(block) - 1:
            for elem in line:
                text(elem, end="", mods=[block[-1]], letter_time=0)
            text(letter_time=0)


def rotate(shape: list, rotations: int) -> list:
    """Rotate a block a given number of times in the given direction.

    Args:
        shape (list): The block to rotate.
        rotations (int): The direction and number of rotations.
            Positive rotates to the right, negative to the left. 0 makes no change.

    Returns:
        list: The block rotated a given number of times.
    """
    block = shape[:]
    shape_color = block[-1]
    block.remove(shape_color)

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

    block.append(shape_color)

    return block
