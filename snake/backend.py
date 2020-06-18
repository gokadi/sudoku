import random
from typing import NamedTuple, List


class Coordinates(NamedTuple):
    column: int
    row: int


class Snake:
    def __init__(
        self, init_row: int, init_column: int, end_row: int, end_column: int
    ):
        self.init_row = init_row
        self.init_column = init_column
        self.end_row = end_row
        self.end_column = end_column

        head_column = (end_column - init_column) // 2
        head_row = (end_row - init_row) // 2
        self.snake_coordinates = [
            Coordinates(head_column, head_row),
            Coordinates(head_column - 1, head_row),
            Coordinates(head_column - 2, head_row),
        ]
        self.apple = self.generate_apple()

    def move_down(self):
        self.snake_coordinates.insert(
            0, Coordinates(row=self.head.row + 1, column=self.head.column)
        )

    @property
    def head(self) -> Coordinates:
        return self.snake_coordinates[0]

    @property
    def tail(self) -> List[Coordinates]:
        return self.snake_coordinates[1:]

    def generate_apple(self):
        apple = []
        while apple is []:
            column = random.randint(self.init_column + 1, self.end_column - 1)
            row = random.randint(self.init_row + 1, self.end_row - 1)
            apple_coordinate = Coordinates(column, row)
            if apple_coordinate not in self.snake_coordinates:
                apple.append(apple_coordinate)
        return apple

    def is_stuck_in_borders(self, max_rows: int, max_columns: int) -> bool:
        head_coordinates = self.head
        return (
            head_coordinates.row >= max_rows - 1
            or head_coordinates.row <= 0
            or head_coordinates.column >= max_columns - 1
            or head_coordinates.column <= 0
        )

    def is_stuck_with_self(self) -> bool:
        return self.head in self.tail
