'''top_score.py
I intend to make a code that tries to check for existing scores and store new ones.
'''

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
# pylint: disable=import-error
# pylint: disable=wrong-import-position


# This is an importer I made for all of my programs going forward so I wouldn't have to deal with
# creating and renaming the personal_functions.py and universal_colors.py for every program.
# Probably adds unnecessary bulk here, but I don't care enough to make it reliable without it.
import sys
import os

parent = os.path.dirname(os.path.realpath(__file__))

while not "utilities" in os.listdir(parent):
    parent = os.path.dirname(parent)
sys.path.append(os.path.join(parent, "utilities"))

import color
from personal_functions import *


def get_scores() -> list:
    """Get the previous high scores.

    Returns:
        list: The high scores.
    """
    path_exist = True
    # If a score file exists we'll go into sorting scores, otherwise skip it.
    try:
        read_scores = open(f"{parent}/data/score.txt", "r", encoding="UTF-8")
    except FileNotFoundError:
        path_exist = False

    scorage = []

    if path_exist:
        listo = read_scores.readlines()[:]

        for item in listo:
            # Splitting wasn't working with one list so splitting into another.
            scorage.append(item.split())

    read_scores.close()

    for z, _ in enumerate(scorage):
        # Changing numbers to integers for math.
        scorage[z][0] = int(scorage[z][0])
        scorage[z][2] = int(scorage[z][2])

    # Adding blank scores if none exist.
    length_list = len(scorage)
    while length_list < 5:
        blank = [length_list, "AAA", -1]
        scorage.append(blank)
        length_list = len(scorage)

    return scorage


def add_score(name: str, score: int, scorage: list) -> None:
    """Add a score to the high scores and cull the lowest before saving them again.

    Args:
        name (str):
            The player's initials.
        score (int):
            The new score.
        scorage (list):
            The previous scores.
    """

    init = name
    scorio = score
    new_score = [6, init, scorio]
    scorage.append(new_score)


    for i in range(len(scorage) - 1):
        for j in range(1,len(scorage)):
            # Having it sort by checking values and rearranging by first number.
            if scorage[-j][2] > scorage[-j - 1][2]:
                scorage[-j][0] = scorage[-j - 1][0]
                scorage[-j - 1][0] -= 1
                # Popping out my list value as a side variable to preserve during rearranging.
                sidestep = scorage[-j - 1]
                scorage[-j - 1] = scorage[-j]
                scorage[-j] = sidestep

    # It was easier to let it go into the nagatives to sort and fix it after.
    # It's chaotic, but it works.
    for i, _ in enumerate(scorage):
        scorage[i][0] = i + 1

    # Keeping the list to top 5.
    while len(scorage) > 5:
        scorage.remove(scorage[-1])

    write_scores =  open(f"{parent}/data/score.txt", "w", encoding="UTF-8")
    for i, _ in enumerate(scorage):
        # Setting a line to the first element in list.
        liney = scorage[i]
        # Converting to string for joining.
        for j, _ in enumerate(liney):
            liney[j] = str(liney[j])
        liney = " ".join(liney)
        # It outputs the same format as I told it to take in.
        print(liney, file = write_scores)
    write_scores.close()
