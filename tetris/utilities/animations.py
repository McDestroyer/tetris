"""Generates animations such as a loading bar."""

# These get rid of annoying errors that usually mean nothing.
# Remove non-import related ones if seriously struggling

# pylint: disable=unused-import
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unexpected-keyword-arg
# pylint: disable=no-member
# pylint: disable=ungrouped-imports
# pylint: disable=undefined-variable


import sys
import os
from time import sleep


# Needed for some reason when called from outside this folder ¯\_(ツ)_/¯
# It adds the parent to the folders it searches in for dependencies.
# It's nearly entirely unused when in a single folder, it was just irritating me in the editor.
try:
    from utilities import color
    from utilities import cursor
    from utilities.personal_functions import *
except ModuleNotFoundError:
    current = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(current)
    from utilities import color
    from utilities import cursor
    from utilities.personal_functions import *


# def loading1(time: int = 5, message: str = "Loading:", container: str = "[ ]", length: int = 50,
#              text_colors: list | None = None, empty_symbol: str = "-", loaded_symbol: str = "#"):

#     text(message, container.split()[0], empty_symbol * length,
#          container.split()[1], mods=text_colors)

#     beginning = message + " " + container.split()[0]
#     ending = container.split()[1]
#     delta = time / length

#     for i in range(length + 1):
#         sleep(delta)
#         cursor.replace_previous()
#         text(beginning, (loaded_symbol * i) + (empty_symbol * (length - i)), ending,
#              letter_time=0, mods=text_colors)


# def loading2(time: int = 5, message: str = "Loading:", container: str = "[ ]", length: int = 50,
#              message_mods: list | None = None, bar_mods: list | None = None,
#              container_mods: list | None = None, empty_symbol: str = "-",
#              loaded_symbol: str = "#"):

#     beginning = container.split()[0]
#     start = len(message + beginning) + 2
#     ending = container.split()[1]
#     delta = time / length

#     text(message, mods=message_mods, end=" ")
#     text(beginning, mods=container_mods, end=" ")
#     text((empty_symbol * length), mods=bar_mods, end=" ")
#     text(ending, mods=container_mods, end="")

#     cursor.hide()
#     cursor.cursor_up()
#     cursor.beginning()
#     cursor.cursor_right(start)

#     for _ in range(length):
#         sleep(delta)
#         text(loaded_symbol, letter_time=0, mods=bar_mods, end="")

#     cursor.show()


def loading_v3(time: int = 5, message: str = "Loading:", container: str = "[ ]", length: int = 50,
             message_mods: list | None = None, bar_mods: list | None = None,
             percent_mods: list | None = None, container_mods: list | None = None,
             empty_symbol: str = "-", loaded_symbol: str = "#", percent: bool = True):
    """Generate a loading bar that counts up dynamically with an optional percentage.

    Args:
        time (int, optional):
            Amount of time in seconds to "load" for.
            Defaults to 5.
        message (str, optional):
            The "message", "Loading:" for example, to show in front of the percent or bar.
            Defaults to "Loading:".
        container (str, optional):
            The opening and closing brackets or symbols surrounding the bar. Split by a space.
            Defaults to "[ ]".
        length (int, optional): 
            The length of the bar.
            Defaults to 50.
        message_mods (list | None, optional):
            The color mods for the message text.
            Defaults to None.
        bar_mods (list | None, optional):
            The color mods for the bar.
            Defaults to None.
        percent_mods (list | None, optional):
            The color mods for the percentage.
            Defaults to None.
        container_mods (list | None, optional):
            The color mods for the bar container.
            Defaults to None.
        empty_symbol (str, optional):
            The symbol used to represent the unloaded part of the bar.
            Defaults to "-".
        loaded_symbol (str, optional):
            The symbol used to represent the loaded part of the bar.
            Defaults to "#".
        percent (bool, optional):
            Determines if the percentage is shown.
            Defaults to True.
    """

    beginning = container.split()[0]
    if percent:
        start = len(message + beginning) + 3 + 4
    else:
        start = len(message + beginning) + 2
    ending = container.split()[1]
    delta = time / length

    text(message, mods=message_mods, end=" ")
    if percent:
        text("  0%", mods=percent_mods, end=" ")
    text(beginning, mods=container_mods, end=" ")
    text((empty_symbol * length), mods=bar_mods, end=" ")
    text(ending, mods=container_mods, end="\r")

    cursor.hide()
    cursor.cursor_up()

    for i in range(length):
        sleep(delta)

        if percent:
            cursor.cursor_right(len(message) + 1)

            if len(str(int(((i + 1) / length) * 100))) == 1:
                text("  ", end="", letter_time=0)

            elif len(str(int(((i + 1) / length) * 100))) == 2:
                text(" ", end="", letter_time=0)

            text(rounder(((i + 1) / (length)) * 100),
                letter_time=0, mods=percent_mods, end="\r")

        cursor.cursor_right(start)

        text(loaded_symbol * (i + 1), letter_time=0, mods=bar_mods, end="\r")

    cursor.show()


if __name__ == "__main__":
    cursor.clear_screen()
    loading_v3(length=100,message_mods=[color.GREEN], container_mods=[color.RED],
            bar_mods=[color.BLUE], percent_mods=[color.YELLOW], percent=True)


# Tetris

# []
# []
# []
# []

# [][]
#   [][]

#   [][]
# [][]

#   []
# [][][]

# [][][]
#     []

#     []
# [][][]
