"""Class"""

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

        # Insert code here
        # TO-DO Zeph here

        # Suggestion:

        while not False:

            # Step 1. Check to see if you can move:
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
                                if not grid[i+1][j][0] == "##" and not grid[i+1][j][1] == color.BLACK:
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
                                if grid[i][j+1][0] == "##" or grid[i][j+1][1] == color.BLACK:
                                    pass
                                else:
                                    return False
                        elif square[0] == "##":
                            return False
            elif direction == "right":
                for i, row in enumerate(grid):
                    for j, square in enumerate(row):
                        if j > len(row)-1:
                            if square[0] == "##":
                                if grid[i][j-1][0] == "##" or grid[i][j-1][1] == color.BLACK:
                                    pass
                                else:
                                    return False
                        elif square[0] == "##":
                            return False
            if direction == "down":
                for i in range(len(grid)-1, -1, -1):
                    for j in range(len(row)):
                        if grid[i+1][j][0] == "##" :
                            grid[i][j][0] = "##"
                            grid[i][j][1] = self.color
                            grid[i+1][j][0] = "██"
                            grid[i+1][j][1] = color.BLACK
            if direction == "left":
                for i in range(len(grid)):
                    for j in range(len(row)):
                        if j > len(row)-1:
                            if grid[i][j+1][0] == "##" :
                                grid[i][j][0] = "##"
                                grid[i][j][1] = self.color
                                grid[i][j+1][0] = "██"
                                grid[i][j+1][1] = color.BLACK
            if direction == "right":
                for i in range(len(grid)):
                    for j in range(len(row)-1, -1, -1):
                        if j > len(row)-1:
                            if grid[i][j-1][0] == "##" :
                                grid[i][j][0] = "##"
                                grid[i][j][1] = self.color
                                grid[i][j-1][0] = "██"
                                grid[i][j-1][1] = color.BLACK

            # Break if only moving once.
            if not infinite_move:
                break


    def move_to(self, grid: list, position: tuple):
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
        rotato = rotate_array(self.shape, direction)
        if direction == -1:
            for i in range(self.pos_y, self.pos_y + self.size):
                for j in range(self.pos_x, self.pos_x + self.size):
                    pass
        elif direction == 1:
            for i in range(self.pos_y, self.pos_y + self.size):
                for j in range(self.pos_x, self.pos_x + self.size):
                    pass


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
