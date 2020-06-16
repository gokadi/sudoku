import curses
from enum import Enum

from menu import Menu
from sudoku import (
    SudokuBoard, Sudoku, ItemCoordinate, BOARD_ROWS,
    BOARD_COLUMNS, DEFAULT_POINTER_POSITION
)

CONTROLS_HELP = (
    'Chosen level: {level}.\nControls:\n- (N) new game;\n'
    '- (↑↓→←) choose cell;\n- (Q) quit;\n- (R) reset;\n'
)
HINTS_HELP = (
    'Hints:\n- (c)andidates;\n- (s)olve.\n'
    'Underlined `0` means there is only one possible value for this cell.'
)


class Levels(int, Enum):
    easy = 36
    normal = 18
    hard = 9


class SudokuMain:
    def __init__(self, window):
        self.window = window
        self.screen_sizes = self.window.getmaxyx()
        self.level = Levels.easy
        self.hints_on = False
        curses.curs_set(0)
        # describe type for menu item with callbacks
        # first callback to handle menu click, second to do after menu exit
        change_level_submenu_items = [
            (Levels.easy.name.capitalize(), [self.set_level_easy]),
            (
                Levels.normal.name.capitalize() + ' (may be slow)',
                [self.set_level_normal]
            ),
            (
                Levels.hard.name.capitalize() + ' (may be slow)',
                [self.set_level_hard]
            ),
        ]
        change_level_submenu = Menu(
            change_level_submenu_items, self.window,
            self.screen_sizes,
            type_messages=[self.__type_level, self.__type_hints]
        )
        main_menu_items = [
            ('Start', [self.close_menu, self.start_game]),
            ('Level', [change_level_submenu.display]),
            ('Hints', [self.toggle_hints])
        ]
        self.main_menu = Menu(
            main_menu_items, self.window, self.screen_sizes,
            type_messages=[self.__type_level, self.__type_hints]
        )
        self.main_menu.display()

    def toggle_hints(self):
        self.hints_on = not self.hints_on
        self.__type_hints()

    def __type_hints(self):
        self.window.move(self.screen_sizes[0] - 3, 0)
        self.window.clrtoeol()
        message = f'Hints: {"on" if self.hints_on else "off"}'
        self.window.addstr(
            self.screen_sizes[0] - 3,
            (self.screen_sizes[1] - len(message)) // 2,
            message, curses.A_BOLD
        )

    def __type_level(self):
        self.window.move(self.screen_sizes[0] - 2, 0)
        self.window.clrtoeol()
        message = f'Chosen level: {self.level.name}'
        self.window.addstr(
            self.screen_sizes[0] - 2,
            (self.screen_sizes[1] - len(message)) // 2,
            message, curses.A_BOLD
        )

    def __set_level(self, level: Levels):
        self.level = level
        self.__type_level()

    def set_level_easy(self):
        self.__set_level(Levels.easy)
        return True

    def set_level_normal(self):
        self.__set_level(Levels.normal)
        return True

    def set_level_hard(self):
        self.__set_level(Levels.hard)
        return True

    def close_menu(self):
        return True

    def draw_help(self, init_row: int, init_column: int):
        if self.hints_on:
            help_text = CONTROLS_HELP + HINTS_HELP
        else:
            help_text = CONTROLS_HELP
        help_box = self.window.subwin(13, 40, init_row, init_column)
        help_box.box()
        help_box.refresh()
        help_box_text = help_box.subwin(11, 38, init_row + 1, init_column + 1)
        help_box_text.move(0, 0)
        help_box_text.addstr(help_text.format(level=self.level.name))
        help_box_text.refresh()

    def get_and_draw_message_box(self, init_row: int, init_column: int):
        message_box_init_column = init_column - 25
        message_box_init_row = init_row
        message_box = self.window.subwin(
            13, 25, message_box_init_row, message_box_init_column
        )
        message_box.box()
        message_box.refresh()
        message_box_text = message_box.subwin(
            11, 23, message_box_init_row + 1, message_box_init_column + 1
        )

        return message_box_text

    def draw_message_in_box(self, box, message: str):
        box.clear()
        box.move(0, 0)
        box.addstr(message)
        box.refresh()

    def start_game(self):
        sudoku = Sudoku()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.window.border(0)
        self.window.refresh()
        self.window.bkgd(' ', curses.color_pair(1))
        init_row = (self.screen_sizes[0] - BOARD_ROWS) // 2
        init_column = (self.screen_sizes[1] - BOARD_COLUMNS) // 2
        board_box = self.window.subwin(
            BOARD_ROWS, BOARD_COLUMNS, init_row, init_column
        )
        board_box.box()
        board = SudokuBoard(board_box, sudoku)
        board.draw_grid()
        message_box = self.get_and_draw_message_box(init_row, init_column)
        self.draw_help(init_row, init_column + BOARD_COLUMNS)
        pointer = DEFAULT_POINTER_POSITION
        pointer_column = pointer.column
        pointer_row = pointer.row
        self.draw_message_in_box(
            message_box, 'Started generating new board...'
        )
        sudoku.populate(self.level.value)
        board.draw_items(pointer, self.hints_on)
        self.draw_message_in_box(
            message_box, 'Finished generating board!'
        )
        while True:
            is_solved = sudoku.is_solved()
            if is_solved:
                self.draw_message_in_box(message_box, 'Solved sudoku!')
            key = chr(self.window.getch())
            if key == 'q':
                break
            elif not is_solved and self.hints_on and key == 'c':
                if sudoku.candidates(pointer):
                    self.draw_message_in_box(
                        message_box,
                        f'Possible values for this cell: '
                        f'{sudoku.candidates(pointer)}'
                    )
                else:
                    self.draw_message_in_box(
                        message_box, 'This is a predefined cell.'
                    )
            elif not is_solved and self.hints_on and key == 's':
                self.draw_message_in_box(message_box, 'Started solving...')
                if not sudoku.solve():
                    self.draw_message_in_box(message_box, 'Could not solve.')
                board.draw_items(
                    ItemCoordinate(row=pointer_row, column=pointer_column),
                    self.hints_on
                )
            elif key == 'n':
                self.draw_message_in_box(
                    message_box, 'Started generating new board...'
                )
                sudoku.clear()
                board.draw_items(pointer, self.hints_on)

                sudoku.populate(self.level.value)
                board.draw_items(pointer, self.hints_on)

                self.draw_message_in_box(
                    message_box, 'Finished generating board!'
                )
            elif key == chr(curses.KEY_LEFT):
                pointer_column -= 1
                if pointer_column < 0:
                    pointer_column = 8
                elif pointer_column == 9:
                    pointer_column = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                board.draw_items(pointer, self.hints_on)
            elif key == chr(curses.KEY_RIGHT):
                pointer_column += 1
                if pointer_column < 0:
                    pointer_column = 8
                elif pointer_column == 9:
                    pointer_column = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                board.draw_items(pointer, self.hints_on)
            elif key == chr(curses.KEY_UP):
                pointer_row -= 1
                if pointer_row < 0:
                    pointer_row = 8
                elif pointer_row == 9:
                    pointer_row = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                board.draw_items(pointer, self.hints_on)
            elif key == chr(curses.KEY_DOWN):
                pointer_row += 1
                if pointer_row < 0:
                    pointer_row = 8
                elif pointer_row == 9:
                    pointer_row = 0
                pointer = ItemCoordinate(
                    row=pointer_row, column=pointer_column
                )
                board.draw_items(pointer, self.hints_on)
            elif not is_solved and key in '0123456789':
                try:
                    sudoku[pointer] = ord(key) - ord('0')
                    board.draw_items(pointer, self.hints_on)
                except Exception as e:
                    self.draw_message_in_box(message_box, str(e))
            else:
                self.draw_message_in_box(
                    message_box,
                    'Unknown button.\nMake sure you switched to EN.'
                )
                self.window.refresh()

            self.window.refresh()
        self.main_menu.display()


if __name__ == '__main__':
    curses.wrapper(SudokuMain)
