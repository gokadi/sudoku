import copy
import random
from typing import NamedTuple


class ItemCoordinate(NamedTuple):
    row: int
    column: int


class ItemCoordinateInBlock(NamedTuple):
    row: int
    column: int


def __create_mapper_inner_coordinates_to_board():
    mapper = {}
    y_modifier_for_stdout = 0
    for y in range(0, 9):
        x_modifier_for_stdout = 0
        if y in [3, 6]:  # 3 and 6 positions need for grid
            y_modifier_for_stdout += 1
        for x in range(0, 9):
            if x in [3, 6]:  # 3 and 6 positions need for grid
                x_modifier_for_stdout += 2
            mapper[
                ItemCoordinate(row=y, column=x)
            ] = ItemCoordinate(
                row=1 + y + y_modifier_for_stdout,
                column=2 + 2 * x + x_modifier_for_stdout
            )
    return mapper


ITEM_COORD_TO_BOARD_MAPPER = __create_mapper_inner_coordinates_to_board()
DEFAULT_POINTER_POSITION = ItemCoordinate(row=0, column=0)


class Block:
    # negative values mean preset default values
    def __init__(self):
        self.items = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __setitem__(self, item_coordinate: ItemCoordinateInBlock, value: int):
        item_coordinate_in_block = (
            item_coordinate.row + 3 * item_coordinate.column
        )
        if abs(self.items[item_coordinate_in_block]) == abs(value):
            self.items[item_coordinate_in_block] = value
            return

        if value != 0 and (value in self.items or -value in self.items):
            raise ValueError(f'Block already contains {value}')

        self.items[item_coordinate_in_block] = value

    def __getitem__(self, item_coordinate: ItemCoordinateInBlock):
        return self.items[item_coordinate.row + 3 * item_coordinate.column]


class Sudoku:
    allowed_values = list(range(1, 10))

    def __init__(self):
        self.blocks = [Block() for _ in range(9)]
        self.virtual_sudoku = copy.deepcopy(self)
        self.cached_sudoku = copy.deepcopy(self)

    def clear(self):
        for block in self.blocks:
            block.items = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def candidates(self, item_coordinate: ItemCoordinate):
        candidates = set()
        previous = self[item_coordinate]
        for i in self.allowed_values:
            try:
                self[item_coordinate] = i
            except ValueError:
                pass
            else:
                candidates.add(i)
        self[item_coordinate] = previous
        return candidates

    def populate(self, n: int = 36):
        # Cached values used in solve() and populate()
        coordinates = list(ITEM_COORD_TO_BOARD_MAPPER.keys())
        # Randomize the list of points and values
        random.shuffle(coordinates)
        random.shuffle(self.allowed_values)
        self.clear()
        self.solve()

        for coordinate in coordinates:
            if self[coordinate] == 0:
                continue
            current_value = self[coordinate]
            for new_value in self.candidates(coordinate):
                if new_value == current_value:
                    continue
                self[coordinate] = new_value
                if self.solve(True):
                    self[coordinate] = current_value
                    break
            else:
                if (
                    81 - sum(block.items.count(0) for block in self.blocks)
                    < n
                ):
                    self[coordinate] = current_value
                    break
                self[coordinate] = 0

        for coordinate in coordinates:
            self[coordinate] *= -1

        self.virtual_sudoku = copy.deepcopy(self)
        self.cached_sudoku = copy.deepcopy(self)
        self.virtual_sudoku.solve()

    def __getitem__(self, item_coordinate: ItemCoordinate):
        block_column = item_coordinate.column // 3
        block_row = item_coordinate.row // 3

        block = self.blocks[block_row + 3 * block_column]

        return block[ItemCoordinateInBlock(
            column=item_coordinate.column % 3, row=item_coordinate.row % 3
        )]

    def __setitem__(self, item_coordinate: ItemCoordinate, value: int):
        if self[item_coordinate] < 0 <= value:
            raise ValueError(
                f'Value at point {item_coordinate} is pre-defined'
            )
        if value != 0:
            for i in range(9):
                if (
                    i != item_coordinate.row
                    and abs(self[ItemCoordinate(
                        column=item_coordinate.column, row=i
                    )]) == abs(value)
                ):
                    raise ValueError(f'Already in column: {value}')
                if (
                    i != item_coordinate.column
                    and abs(self[ItemCoordinate(
                        column=i, row=item_coordinate.row
                    )]) == abs(value)
                ):
                    raise ValueError(f'Already in row: {value}')

        pb = (item_coordinate.column // 3, item_coordinate.row // 3)
        block = self.blocks[pb[1] + 3 * pb[0]]

        block[ItemCoordinateInBlock(
            column=item_coordinate.column % 3, row=item_coordinate.row % 3
        )] = value

    def is_solved(self):
        return all(0 not in self.blocks[i].items for i in range(0, 9))

    def fill_cell(self, item_coordinates: ItemCoordinate):
        self[item_coordinates] = self.virtual_sudoku[item_coordinates]

    def solve(self, check=False):
        if self.is_solved():
            return True

        item_coordinate = None
        for column in range(9):
            if item_coordinate is not None:
                break
            for row in range(9):
                if self[ItemCoordinate(column=column, row=row)] == 0:
                    item_coordinate = ItemCoordinate(column=column, row=row)
                    break

        if item_coordinate is None:
            return True

        for value in self.allowed_values:
            try:
                self[item_coordinate] = value
            except ValueError:
                continue
            else:
                if self.solve(check):
                    if check:
                        self[item_coordinate] = 0
                    return True
                else:
                    self[item_coordinate] = 0
