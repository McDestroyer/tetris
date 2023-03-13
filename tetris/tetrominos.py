"""Class"""

class tetromino:

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
        self.x = pos[0]
        self.y = pos[1]
        self.size = len(shape[0])
        self.status = status


    def move(self, direction: str = "down", distance: int = 1) -> tuple:
        """Move a tetromino in a given direction a given distance.

        Args:
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
                Otherwise, returns False
        """

        # Insert code here
