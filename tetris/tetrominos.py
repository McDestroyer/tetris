"""Class"""

# pylint: disable=consider-using-enumerate
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

from utilities import color
from tetris_functions import *
class Tetromino:
    """The tetrominoes falling, held, or in future."""

    def __init__(self, shape: list, pos: list, status: int = 3):
        """Initiate the tetromino class by adding various stats.

        Args:
            shape (list):
                The shape and color of the tetromino.
            pos (list):
                The position of the top left corner of the tetromino.
            status (int, optional):
                -1 if held, 0 if falling, or 1, 2, or 3 if stored.
                Defaults to 3.
        """
        self.color = shape[-1]
        self.shape = shape[:len(shape)-1]
        self.position = pos
        self.rotation = 0
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.size = len(shape[0])
        self.status = status
        self.was_held = False


    def move(self, grid: list, direction: str = "down", infinite_move: bool = False) -> tuple:
        """Move a tetromino in a given direction a given distance.

        Args:
            grid (list):
                The current positions of all obstacles.
            direction (str, optional):
                The direction to move.
                Options: "left", "right", "down"
                Defaults to "down".
            infinite_move (bool, optional):
                The determines whether or not the block continues to
                move until it can't or if it just moves 1 space.
                Defaults to False.

        Returns:
            bool:
                Returns True if the block moved at least one space.
                Otherwise, returns False.
        """

        while not False:

            # Step 1. Check to see if you can move:
            if not self.check_dir(grid, direction):
                return False


            if direction == "down":
                for i in range(len(grid)-1, -1, -1):
                    for j in range(len(grid[0])):
                        if grid[i][j][0] == "##":
                            grid[i+1][j][0] = "##"
                            grid[i+1][j][1] = self.color
                            grid[i][j][0] = "██"
                            grid[i][j][1] = color.BLACK
                self.update_position([self.pos_x, self.pos_y + 1])

            elif direction == "left":
                for i in range(0, len(grid)):
                    for j in range(0, len(grid[0])):
                        if j < len(grid[0])-1:
                            if grid[i][j+1][0] == "##" :
                                grid[i][j][0] = "##"
                                grid[i][j][1] = self.color
                                grid[i][j+1][0] = "██"
                                grid[i][j+1][1] = color.BLACK
                self.update_position([self.pos_x - 1, self.pos_y])

            elif direction == "right":
                for i in range(len(grid)):
                    for j in range(len(grid[0])-1, -1, -1):
                        if j > 0:
                            if grid[i][j-1][0] == "##" :
                                grid[i][j][0] = "##"
                                grid[i][j][1] = self.color
                                grid[i][j-1][0] = "██"
                                grid[i][j-1][1] = color.BLACK
                self.update_position([self.pos_x + 1, self.pos_y])

            # Break if only moving once.
            if not infinite_move:
                return True


    def check_dir(self, grid: list, direction: str = "down") -> bool:
        if direction == "down":
            # Loop rows
            for i, row in enumerate(grid):
                # As long as it's not at the end
                if i < len(grid) - 1:
                    # Loop positions in the row
                    for j, square in enumerate(row):
                        # If the current pos is falling
                        if square[0] == "##":
                            # If the next square down is not empty
                            if (not grid[i+1][j][0] == "##" and
                                not grid[i+1][j][1] == color.BLACK):
                                # Fail.
                                return False

                # If at the end
                else:
                    # If there's a falling block, fail.
                    for j, square in enumerate(row):
                        if square[0] == "##":
                            return False

        elif direction == "left":
            for i, row in enumerate(grid):
                for j, square in enumerate(row):
                    if j > 0:
                        if square[0] == "##":
                            if grid[i][j-1][0] == "##" or grid[i][j-1][1] == color.BLACK:
                                pass
                            else:
                                return False
                    elif square[0] == "##":
                        return False

        elif direction == "right":
            for i, row in enumerate(grid):
                for j, square in enumerate(row):
                    if j < len(row)-1:
                        if square[0] == "##":
                            if grid[i][j+1][0] == "##" or grid[i][j+1][1] == color.BLACK:
                                pass
                            else:
                                return False
                    elif square[0] == "##":
                        return False
        return True


    def move_to(self, grid: list, position: list):
        """Move the tetromino to specific relative coordinates.

        Args:
            grid (list):
                The current positions of all obstacles.
            position (tuple):
                The x and y distance to move.

        Returns:
            list:
                The modified grid.
        """

        for i, row in enumerate(self.shape):
            for j, square in enumerate(row):
                if square == "##":
                    grid[i + position[1]][j + position[0]] = [square, self.color]

        self.update_position(position)



    def rotate(self, grid: list, direction: int) -> bool:
        """Rotate the block and run wallkick calculations.

        Args:
            grid (list):
                The current positions of all obstacles.
            direction (int):
                The direction to rotate. -1 = left and 1 is right.

        Returns:
            bool:
                Returns True if the move succeeded.
                Otherwise, returns False.
        """
        rotated_piece = rotate_array(self.shape, direction)

        # Check where it will fit.
        for x, y in wallkick_motion(self.rotation, direction,
                                    self.color == color.rgb_hex("00", "ff", "ff")):
            mod_x = self.pos_x + x
            mod_y = self.pos_y + -y

            fail = False
            succeed = False

            # Loop through the rotated piece.
            for i in range(mod_y, mod_y + self.size):
                for j in range(mod_x, mod_x + self.size):
                    # If part of the piece would be here:
                    if rotated_piece[i - mod_y][j - mod_x] == "##":
                        if 0 <= j < 10:
                            # If it would hit something, fail. Otherwise, continue.
                            if grid[i][j][1] != color.BLACK and grid[i][j][0] != "##":
                                fail = True
                        else:
                            fail = True
                    if fail:
                        break
                if fail:
                    break

            if fail is False:
                succeed = True
                break

        if not succeed:
            return False

        clear(grid)
        self.shape = rotated_piece
        self.rotation = (self.rotation + direction) % 4
        self.update_position([mod_x, mod_y])

        # Actually place it.
        # Loop through the rotated piece.
        for i in range(mod_y, mod_y + self.size):
            for j in range(mod_x, mod_x + self.size):
                # If part of the piece would be here, set it.
                if self.shape[i - mod_y][j - mod_x] == "##":
                    grid[i][j] = ["##", self.color]

        return True


    def change_status(self, position_items: list, status: int = 0) -> None:
        """Change the status and therefore also position of the tetromino.

        Args:
            position_items (list):
                The blocks in their positions.
            status (int, optional):
                The status to change the tetromino to.
        """
        self.status = status
        position_items[status] = self


    def update_position(self, position: list):
        """Update all position variables simultaneously.

        Args:
            position (list):
                The position array.
        """
        self.position = position
        self.pos_x = position[0]
        self.pos_y = position[1]


    def visualize(self, offsets: list):
        positions = [
            [0, 0],
            [offsets[0] + 20 + 3, 2],
            [offsets[0] + 20 + 3, 2 + 5],
            [offsets[0] + 20 + 3, 2 + 10],
            [2, 2]
        ]

        pos = positions[self.status][:]

        for i in range(4):
            cursor.set_pos(pos[0] + 1, pos[1] + i + 1)
            for _ in range(4):
                text("██", mods=[color.BLACK], letter_time=0, end="", flush=False)

        for i in range(self.size):
            cursor.set_pos(pos[0] + 1, pos[1] + i + 1)
            for j in range(self.size):
                if self.shape[i][j] == "##":
                    text("██", mods=[self.color], letter_time=0, end="", flush=False)
                else:
                    text("██", mods=[color.BLACK], letter_time=0, end="", flush=False)
        
        text("", end="", letter_time=0, flush=True)


WALLKICK_TABLE = [

    [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]], # 0>3 left

    [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]], # 0>1 right

    [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]], # 1>0 left

    [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]], # 1>2 right

    [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]], # 2>1 left

    [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]], # 2>3 right

    [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]], # 3>2 left

    [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]] # 3>0 right
]
I_WALLKICK_TABLE = [
    [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]], # 0>3 left
    [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]], # 0>1 right
    [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]], # 1>0 left
    [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]], # 1>2 right
    [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]], # 2>1 left
    [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]], # 2>3 right
    [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]], # 3>2 left
    [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]], # 3>0 right
]

def wallkick_motion(original_rotation: int, direction: int, is_i: bool = False) -> list:

    rotation = (original_rotation * 2) + 1 + min(direction, 0)

    if not is_i:
        return WALLKICK_TABLE[rotation][:]
    else:
        return I_WALLKICK_TABLE[rotation][:]
