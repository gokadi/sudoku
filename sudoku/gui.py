import copy
import curses
from enum import Enum

from menu import MenuItem, MenuItemCallback, Menu
from sudoku.backend import (
    ItemCoordinate, Sudoku, DEFAULT_POINTER_POSITION,
    ITEM_COORD_TO_BOARD_MAPPER
)

# Should not be changed or board will become ugly
BOARD_ROWS = 13
BOARD_COLUMNS = 25

CONTROLS_HELP = (
    'Chosen level: {level}.\nControls:\n- (N) new game;\n'
    '- (↑↓→←) choose cell;\n- (Q) quit;\n- (R) reset;\n'
)
# Uncomment below for cheating
# HINTS_HELP = (
#     'Hints:\n- (C) candidates;\n- (S) solve.\n'
#     'Underlined `-` means there is only one possible value for this cell.'
# )
USER_HINTS_HELP = (
    '\nHints:\n- (H) fill in the cell.'
)


class Levels(int, Enum):
    easy = 36
    normal = 18
    hard = 9


class SudokuMain:
    def get_menu(self):
        change_level_submenu_items = [
            MenuItem(
                Levels.easy.name.capitalize(),
                MenuItemCallback(self.set_level, {'level': Levels.easy})
            ),
            MenuItem(
                Levels.normal.name.capitalize() + ' (may be slow)',
                MenuItemCallback(self.set_level, {'level': Levels.normal})
            ),
            MenuItem(
                Levels.hard.name.capitalize() + ' (may be slow)',
                MenuItemCallback(self.set_level, {'level': Levels.hard})
            ),
            MenuItem('Exit', MenuItemCallback(lambda: True))
        ]
        change_level_submenu = Menu(
            change_level_submenu_items, self.window,
            self.screen_sizes,
            type_messages=[self._type_level, self._type_hints]
        )
        main_menu_items = [
            MenuItem(
                'Start',
                MenuItemCallback(self.close_menu),
                MenuItemCallback(self.start_game)
            ),
            MenuItem('Level', MenuItemCallback(change_level_submenu.display)),
            MenuItem('Hints', MenuItemCallback(self.toggle_hints)),
            # Uncomment below for cheating
            # MenuItem('Hints_dev', self.toggle_dev_hints),
            MenuItem('Exit', MenuItemCallback(lambda: True))
        ]
        return Menu(
            main_menu_items, self.window, self.screen_sizes,
            type_messages=[self._type_level, self._type_hints]
        )

    def __init__(self, window):
        self.window = window
        self.screen_sizes = self.window.getmaxyx()
        self.level = Levels.easy
        self.hints_on = False
        self.dev_hints_on = False
        curses.curs_set(0)
        self.main_menu = self.get_menu()
        self.sudoku = Sudoku()
        self.cached_sudoku = None

    def toggle_dev_hints(self):
        self.dev_hints_on = not self.hints_on

    def toggle_hints(self):
        self.hints_on = not self.hints_on
        self._type_hints()

    def _type_hints(self):
        self.window.move(self.screen_sizes[0] - 3, 0)
        self.window.clrtoeol()
        message = f'Hints: {"on" if self.hints_on else "off"}'
        self.window.addstr(
            self.screen_sizes[0] - 3,
            (self.screen_sizes[1] - len(message)) // 2,
            message, curses.A_BOLD
        )

    def _type_level(self):
        self.window.move(self.screen_sizes[0] - 2, 0)
        self.window.clrtoeol()
        message = f'Chosen level: {self.level.name}'
        self.window.addstr(
            self.screen_sizes[0] - 2,
            (self.screen_sizes[1] - len(message)) // 2,
            message, curses.A_BOLD
        )

    def set_level(self, **kwargs):
        self.level = kwargs['level']
        self._type_level()
        return True

    def close_menu(self):
        return True

    def _get_and_draw_textbox(self, init_row: int, init_column: int):
        textbox_wrapper = self.window.subwin(
            BOARD_ROWS, BOARD_COLUMNS, init_row, init_column
        )
        textbox_wrapper.box()
        textbox_wrapper.refresh()
        textbox = textbox_wrapper.subwin(
            BOARD_ROWS - 2, BOARD_COLUMNS - 2, init_row + 1, init_column + 1
        )

        return textbox

    @staticmethod
    def type_message_in_box(box, message: str):
        box.clear()
        box.move(0, 0)
        box.addstr(message)
        box.refresh()

    def draw_grid(self, board_box):
        """
        ┌───────┬───────┬───────┐
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        ├───────┼───────┼───────┤<- second_row
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        ├───────┼───────┼───────┤<- third_row
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        │ 0 0 0 │ 0 0 0 │ 0 0 0 │
        └───────┴───────┴───────┘<- last_row
                ^       ^       ^
                |       |       |
         second_column  |   last_column
                     third_column
        No need to compute `first_column` and `first_row`, because it's
        provided by `board_box` borders
        """
        last_row = BOARD_ROWS - 1
        second_row = last_row // 3
        third_row = last_row // 3 * 2

        last_column = BOARD_COLUMNS - 1
        second_column = last_column // 3
        third_column = last_column // 3 * 2
        # Can not use nested boxes here because it's ugly
        board_box.vline(0, second_column, curses.ACS_VLINE, BOARD_ROWS)
        board_box.vline(0, third_column, curses.ACS_VLINE, BOARD_ROWS)
        board_box.hline(second_row, 0, curses.ACS_HLINE, BOARD_COLUMNS)
        board_box.hline(third_row, 0, curses.ACS_HLINE, BOARD_COLUMNS)
        board_box.addch(0, second_column, curses.ACS_TTEE)
        board_box.addch(0, third_column, curses.ACS_TTEE)
        board_box.addch(last_row, second_column, curses.ACS_BTEE)
        board_box.addch(last_row, third_column, curses.ACS_BTEE)
        board_box.addch(second_row, 0, curses.ACS_LTEE)
        board_box.addch(third_row, 0, curses.ACS_LTEE)
        board_box.addch(second_row, last_column, curses.ACS_RTEE)
        board_box.addch(third_row, last_column, curses.ACS_RTEE)
        board_box.addch(second_row, second_column, curses.ACS_PLUS)
        board_box.addch(second_row, third_column, curses.ACS_PLUS)
        board_box.addch(third_row, second_column, curses.ACS_PLUS)
        board_box.addch(third_row, third_column, curses.ACS_PLUS)
        board_box.refresh()

    def draw_items(
        self, board_box,
        active_item: ItemCoordinate = DEFAULT_POINTER_POSITION,
        hints_on: bool = False
    ):
        for y in range(0, 9):
            for x in range(0, 9):
                item_coordinates = ItemCoordinate(column=x, row=y)
                value = self.sudoku[item_coordinates]
                attrs = curses.A_BOLD if value < 0 else 0
                # Mark cells with only one possible solution.
                if (
                    hints_on
                    and len(self.sudoku.candidates(item_coordinates)) == 1
                ):
                    attrs |= curses.A_UNDERLINE
                item_board_coords = ITEM_COORD_TO_BOARD_MAPPER[
                    item_coordinates
                ]
                if item_coordinates == active_item:
                    attrs |= curses.A_REVERSE
                if value == 0:
                    board_box.addch(
                        item_board_coords.row, item_board_coords.column,
                        '-', attrs
                    )
                else:
                    board_box.addch(
                        item_board_coords.row, item_board_coords.column,
                        ord('0') + abs(value), attrs
                    )

                board_box.refresh()

    def start_game(self):
        self.window.border(0)
        self.window.refresh()
        init_row = (self.screen_sizes[0] - BOARD_ROWS) // 2
        init_column = (self.screen_sizes[1] - BOARD_COLUMNS) // 2
        board_box = self.window.subwin(
            BOARD_ROWS, BOARD_COLUMNS, init_row, init_column
        )
        message_box = self._get_and_draw_textbox(
            init_row, init_column - BOARD_COLUMNS
        )
        help_box = self._get_and_draw_textbox(
            init_row, init_column + BOARD_COLUMNS
        )
        if self.hints_on:
            help_text = CONTROLS_HELP + USER_HINTS_HELP
        else:
            help_text = CONTROLS_HELP
        self.type_message_in_box(help_box, help_text)

        board_box.box()
        self.draw_grid(board_box)

        pointer = DEFAULT_POINTER_POSITION
        pointer_column = pointer.column
        pointer_row = pointer.row
        self.type_message_in_box(
            message_box, 'Started generating new board...'
        )
        self.sudoku.populate(self.level.value)
        self.cached_sudoku = copy.deepcopy(self.sudoku)
        self.draw_items(board_box, pointer, self.dev_hints_on)
        self.type_message_in_box(
            message_box, 'Finished generating board!'
        )
        while True:
            is_solved = self.sudoku.is_solved()
            if is_solved:
                self.type_message_in_box(message_box, 'Solved sudoku!')
            key = chr(self.window.getch())
            if key == 'q':
                break
            elif not is_solved and self.dev_hints_on and key == 'c':
                if self.sudoku.candidates(pointer):
                    self.type_message_in_box(
                        message_box,
                        f'Possible values for this cell: '
                        f'{self.sudoku.candidates(pointer)}'
                    )
                else:
                    self.type_message_in_box(
                        message_box, 'This is a predefined cell.'
                    )
            elif not is_solved and self.dev_hints_on and key == 's':
                self.type_message_in_box(message_box, 'Started solving...')
                if not self.sudoku.solve():
                    self.type_message_in_box(message_box, 'Could not solve.')
                self.draw_items(
                    board_box,
                    ItemCoordinate(row=pointer_row, column=pointer_column),
                    self.dev_hints_on
                )
            elif key == 'n':
                self.type_message_in_box(
                    message_box, 'Started generating new board...'
                )
                self.sudoku.clear()
                self.draw_items(board_box, pointer, self.dev_hints_on)

                self.sudoku.populate(self.level.value)
                self.cached_sudoku = copy.deepcopy(self.sudoku)
                self.draw_items(board_box, pointer, self.dev_hints_on)

                self.type_message_in_box(
                    message_box, 'Finished generating board!'
                )
            elif self.hints_on and key == 'h':
                try:
                    self.sudoku.fill_cell(pointer)
                    self.draw_items(board_box, pointer, self.dev_hints_on)
                except Exception as e:
                    self.type_message_in_box(message_box, str(e))
            elif key == 'r':
                self.sudoku = copy.deepcopy(self.cached_sudoku)
                self.draw_items(board_box, pointer, self.dev_hints_on)

            elif key == chr(curses.KEY_LEFT):
                pointer_column -= 1
                if pointer_column < 0:
                    pointer_column = 8
                elif pointer_column == 9:
                    pointer_column = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                self.draw_items(board_box, pointer, self.dev_hints_on)
            elif key == chr(curses.KEY_RIGHT):
                pointer_column += 1
                if pointer_column < 0:
                    pointer_column = 8
                elif pointer_column == 9:
                    pointer_column = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                self.draw_items(board_box, pointer, self.dev_hints_on)
            elif key == chr(curses.KEY_UP):
                pointer_row -= 1
                if pointer_row < 0:
                    pointer_row = 8
                elif pointer_row == 9:
                    pointer_row = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                self.draw_items(board_box, pointer, self.dev_hints_on)
            elif key == chr(curses.KEY_DOWN):
                pointer_row += 1
                if pointer_row < 0:
                    pointer_row = 8
                elif pointer_row == 9:
                    pointer_row = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                self.draw_items(board_box, pointer, self.dev_hints_on)
            elif not is_solved and key in '0123456789':
                try:
                    self.sudoku[pointer] = ord(key) - ord('0')
                    self.draw_items(board_box, pointer, self.dev_hints_on)
                except Exception as e:
                    self.type_message_in_box(message_box, str(e))
            else:
                self.type_message_in_box(
                    message_box,
                    'Unknown button.\nMake sure you switched to EN.'
                )
                self.window.refresh()

            self.window.refresh()
        self.main_menu.display()
