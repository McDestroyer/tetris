"""Work with keyboard inputs."""
# Disables annoying and usually incorrect warnings.
# pylint: disable=wrong-import-position
# pylint: disable=import-error

import os
import time
import pkg_resources

# Checks to see if the dependency is installed. If not, installs it.
DEPENDENCY = "keyboard"
try:
    pkg_resources.require(DEPENDENCY)
except pkg_resources.DistributionNotFound:
    os.system(f'pip install {DEPENDENCY} --quiet')
    os.system(f'python -m pip install {DEPENDENCY} --quiet')
    os.system(f'python3 -m pip install {DEPENDENCY} --quiet')
    os.system(f'py -m pip install {DEPENDENCY} --quiet')

import keyboard

# The keys previously pressed
keys = {}
frames_since = {}


def is_newly_pressed(buttons: str | list, function: callable or None = None,
                     args: list | None = None) -> bool:
    """Detect if a key is pressed and return True if
    it wasn't pressed the last time this function was called.
    Designed to be run every frame.

    Args:
        buttons (str | list): 
             Key(s) to check the newness of the compression thereof.
        function (str, optional): 
             The function to execute if the key is newly pressed.
        args (list | None, optional):
            The arguments to pass to the function if given.
            Defaults to None.

    Returns:
        bool: True if the key is pressed but was not pressed during the previous call.
        False otherwise.
    """
    if isinstance(buttons, list):
        loops = len(buttons)
    else:
        buttons = [buttons]
        loops = 1

    for i in range(loops):
        result = False
        # If the key has been pressed previously, check it's previous value.
        # If it says it wasn't pressed, but it is now, change to fit and set the result accordingly
        # and vise-versa.
        # If the current and previous values are the same, set the result to False.
        if buttons[i] in keys:
            if keyboard.is_pressed(buttons[i]) and keys[buttons[i]][0] is False:
                keys[buttons[i]] = [True, time.monotonic()]
                result = True
            elif keyboard.is_pressed(buttons[i]) and keys[buttons[i]][0] is True:
                pass
            else:
                keys[buttons[i]][0] = False

        # If it isn't in the list, set the result and the value
        # to whether or not it's currently pressed.
        else:
            if keyboard.is_pressed(buttons[i]):
                keys[buttons[i]] = [True, time.monotonic()]
                result = True
            else:
                keys[buttons[i]] = [False, time.monotonic()]

        # If a function is provided and the result was True, run the function.
        if result and function is not None:
            if not args is None:
                function(*args)
            else:
                function()

        if result is True:
            return result
    return False


def is_long_pressed(buttons: str | list, function: callable or None = None,
                     args: list | None = None, initial: bool = True,
                     time_delay: float = .2, speed: int = 0) -> bool:
    """Detect if a key is pressed and return True if
    it wasn't pressed the last time this function was called
    or if it has been (time_delay) seconds since the last call.
    Designed to be run every frame.

    Args:
        buttons (str): 
             Key(s) to check the newness of the compression thereof.
        function (str, optional): 
             The function to execute if the key is newly pressed.
        args (list | None, optional):
            The arguments to pass to the function if given.
            Defaults to None.
        initial (bool, optional):
            Determines if it returns true when the key was just pressed.
            Defaults to True.
        time_delay (float, optional):
            The amount of time in seconds required to pass before it returns True.
            Defaults to .2.
        speed (int, optional):
            The number of frames it takes to run. Highter is slower.
            Defaults to 0.

    Returns:
        bool: True if the conditions are met. Otherwise, False.
    """
    if isinstance(buttons, list):
        loops = len(buttons)
    else:
        buttons = [buttons]
        loops = 1

    for i in range(loops):
        success = False
        if buttons[i] in frames_since:
            frames_since[buttons[i]] += 1
        else:
            frames_since[buttons[i]] = 0

        if is_newly_pressed(buttons[i], function, args) and initial:
            frames_since[buttons[i]] = 0
            success = True

        if frames_since[buttons[i]] >= speed:
            frames_since[buttons[i]] = 0

            if (is_currently_pressed(buttons[i]) and
                keys[buttons[i]][1] + time_delay <= time.monotonic()):
                success = True

            else:
                success = False

        if success is True:
            return success

    return False

def is_currently_pressed(buttons: str | list, function: callable or None = None,
                         args: list | None = None) -> bool:
    """Check to see if a key is currently pressed.

    Args:
        buttons (str):
            The key(s) to check.
        function (callable | None, optional):
            The function to call if the key is pressed.
            Defaults to None.
        args (list | None, optional):
            The arguments to pass to the function if given.
            Defaults to None.

    Returns:
        bool: True if the key is pressed. False otherwise.
    """
    if isinstance(buttons, list):
        loops = len(buttons)
    else:
        buttons = [buttons]
        loops = 1

    for i in range(loops):
        # Update the list
        try:
            keys[buttons[i]][0] = keyboard.is_pressed(buttons[i])
        except KeyError:
            keys[buttons[i]] = [keyboard.is_pressed(buttons[i]), time.monotonic()]

        # Run if true
        if function is not None and keys[buttons[i]][0] is True:
            if not args is None:
                function(*args)
            else:
                function()

        if keys[buttons[i]][0]:
            return True
    return False


def simulate(key: str, delay: int | None = None):
    """Simulate a keypress or keypresses after a certain amount of time.

    Args:
        key (str):
            The key(s) to simulate separated by a +.
        delay (int | None, optional):
            The time to wait before simulating the key(s).
            Defaults to None.
    """
    if not delay is None:
        time.sleep(delay)
    keyboard.send(key)
