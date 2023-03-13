"""Class"""

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
        self.position = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.size = len(shape[0])
        self.status = status
        self.was_held = False


    def move(self, grid: list, direction: str = "down", distance: int = 1) -> tuple:
        """Move a tetromino in a given direction a given distance.

        Args:
            grid (list):
                The current positions of all obstacles.
            direction (str, optional):
                The direction to move.
                Options: "left", "right", "down"
                Defaults to "down".
            distance (int, optional):
                The distance to move. -1 = as far as possible.
                Defaults to 1.

        Returns:
            bool:
                Returns True if the block moved at least one space.
                Otherwise, returns False.
        """

        # Insert code here
        # TODO Zeph here


    def move_to(self, grid: list, position: tuple) -> bool:
        """Move the tetromino to specific relative coordinates.

        Args:
            grid (list):
                The current positions of all obstacles.
            position (tuple):
                The x and y distance to move.

        Returns:
            bool:
                Returns True if the move succeeded.
                Otherwise, returns False.
        """


    def rotate(self, grid: list, direction: int) -> bool:
        """Rotate the block and run wallkick calculations.

        Args:
            grid (list):
                The current positions of all obstacles.
            direction (int):
                The direction to rotate. -1  = left and 1 is right.

        Returns:
            bool:
                Returns True if the move succeeded.
                Otherwise, returns False.
        """


    def change_status(self, status: int = 0) -> None:
        """Change the status and therefore also position of the tetromino.

        Args:
            status (int):
                The status to change the tetromino to.
        """
