import curses
from enum import Enum

from menu import MenuItem, MenuItemCallback, Menu

HELP_BOX_COLUMNS = 30
CONTROLS_HELP = (
    'Chosen level: {level}.\nControls:\n- (N) new game;\n'
    '- (↑↓→←) move;\n- (Q) quit;\n- (R) reset;\n'
)


class Levels(int, Enum):
    easy = 36
    normal = 18
    hard = 9


class SnakeMain:
    def get_menu(self):
        change_level_submenu_items = [
            MenuItem(
                Levels.easy.name.capitalize(),
                MenuItemCallback(self.set_level, {'level': Levels.easy})
            ),
            MenuItem(
                Levels.normal.name.capitalize(),
                MenuItemCallback(self.set_level, {'level': Levels.normal})
            ),
            MenuItem(
                Levels.hard.name.capitalize(),
                MenuItemCallback(self.set_level, {'level': Levels.hard})
            ),
            MenuItem('Exit', MenuItemCallback(lambda: True))
        ]
        change_level_submenu = Menu(
            change_level_submenu_items, self.window,
            self.screen_sizes,
            type_messages=[self._type_level]
        )
        main_menu_items = [
            MenuItem(
                'Start',
                MenuItemCallback(self.close_menu),
                MenuItemCallback(self.start_game)
            ),
            MenuItem('Level', MenuItemCallback(change_level_submenu.display)),
            MenuItem('Exit', MenuItemCallback(lambda: True))
        ]
        return Menu(
            main_menu_items, self.window, self.screen_sizes,
            type_messages=[self._type_level]
        )

    def __init__(self, window):
        self.window = window
        self.screen_sizes = self.window.getmaxyx()
        self.level = Levels.easy
        self.score = 0
        curses.curs_set(0)
        self.main_menu = self.get_menu()
        # self.sudoku = Sudoku()

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
            self.screen_sizes[0], HELP_BOX_COLUMNS, init_row, init_column
        )
        textbox_wrapper.box()
        textbox_wrapper.refresh()
        textbox = textbox_wrapper.subwin(
            self.screen_sizes[0] - 2, HELP_BOX_COLUMNS - 2,
            init_row + 1, init_column + 1
        )

        return textbox

    @staticmethod
    def type_message_in_box(box, message: str):
        box.clear()
        box.move(0, 0)
        box.addstr(message)
        box.refresh()

    def type_score_in_box(self, box, message: str):
        box.clear()
        box.move(
            self.screen_sizes[0] - 3, (HELP_BOX_COLUMNS - len(message)) // 2
        )
        box.addstr(message, curses.A_BOLD)
        box.refresh()

    def start_game(self):
        self.window.border(0)
        self.window.refresh()
        init_row = 0
        init_column = 0
        end_row = self.screen_sizes[0] - 1
        end_column = self.screen_sizes[1] - HELP_BOX_COLUMNS

        board_rows = self.screen_sizes[0]
        board_columns = self.screen_sizes[1] - HELP_BOX_COLUMNS
        board_box = self.window.subwin(
            self.screen_sizes[0], self.screen_sizes[1] - HELP_BOX_COLUMNS,
            init_row, init_column
        )
        board_box.box()
        help_box = self._get_and_draw_textbox(init_row, end_column)
        # help_box = self._get_and_draw_textbox(
        #     init_row, init_column + BOARD_COLUMNS
        # )
        # if self.hints_on:
        #     help_text = CONTROLS_HELP + USER_HINTS_HELP
        # else:
        #     help_text = CONTROLS_HELP
        self.type_message_in_box(help_box, CONTROLS_HELP)
        self.type_score_in_box(help_box, f'Score: {self.score}')
        #
        # board_box.box()
        # self.draw_grid(board_box)
        #
        # pointer = DEFAULT_POINTER_POSITION
        # pointer_column = pointer.column
        # pointer_row = pointer.row
        # self.type_message_in_box(
        #     message_box, 'Started generating new board...'
        # )
        # self.sudoku.populate(self.level.value)
        # self.draw_items(board_box, pointer, self.dev_hints_on)
        # self.type_message_in_box(
        #     message_box, 'Finished generating board!'
        # )
        while True:
        #     is_solved = self.sudoku.is_solved()
        #     if is_solved:
        #         self.type_message_in_box(message_box, 'Solved sudoku!')
            key = chr(self.window.getch())
            if key == 'q':
                break
        #     elif not is_solved and self.dev_hints_on and key == 'c':
        #         if self.sudoku.candidates(pointer):
        #             self.type_message_in_box(
        #                 message_box,
        #                 f'Possible values for this cell: '
        #                 f'{self.sudoku.candidates(pointer)}'
        #             )
        #         else:
        #             self.type_message_in_box(
        #                 message_box, 'This is a predefined cell.'
        #             )
        #     elif not is_solved and self.dev_hints_on and key == 's':
        #         self.type_message_in_box(message_box, 'Started solving...')
        #         if not self.sudoku.solve():
        #             self.type_message_in_box(message_box, 'Could not solve.')
        #         self.draw_items(
        #             board_box,
        #             ItemCoordinate(row=pointer_row, column=pointer_column),
        #             self.dev_hints_on
        #         )
        #     elif key == 'n':
        #         self.type_message_in_box(
        #             message_box, 'Started generating new board...'
        #         )
        #         self.sudoku.clear()
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #
        #         self.sudoku.populate(self.level.value)
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #
        #         self.type_message_in_box(
        #             message_box, 'Finished generating board!'
        #         )
        #     elif self.hints_on and key == 'h':
        #         try:
        #             self.sudoku.fill_cell(pointer)
        #             self.draw_items(board_box, pointer, self.dev_hints_on)
        #         except Exception as e:
        #             self.type_message_in_box(message_box, str(e))
        #     elif key == chr(curses.KEY_LEFT):
        #         pointer_column -= 1
        #         if pointer_column < 0:
        #             pointer_column = 8
        #         elif pointer_column == 9:
        #             pointer_column = 0
        #         pointer = ItemCoordinate(
        #             row=pointer_row, column=pointer_column
        #         )
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #     elif key == chr(curses.KEY_RIGHT):
        #         pointer_column += 1
        #         if pointer_column < 0:
        #             pointer_column = 8
        #         elif pointer_column == 9:
        #             pointer_column = 0
        #         pointer = ItemCoordinate(
        #             row=pointer_row, column=pointer_column
        #         )
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #     elif key == chr(curses.KEY_UP):
        #         pointer_row -= 1
        #         if pointer_row < 0:
        #             pointer_row = 8
        #         elif pointer_row == 9:
        #             pointer_row = 0
        #         pointer = ItemCoordinate(
        #             row=pointer_row, column=pointer_column
        #         )
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #     elif key == chr(curses.KEY_DOWN):
        #         pointer_row += 1
        #         if pointer_row < 0:
        #             pointer_row = 8
        #         elif pointer_row == 9:
        #             pointer_row = 0
        #         pointer = ItemCoordinate(
        #             row=pointer_row, column=pointer_column
        #         )
        #         self.draw_items(board_box, pointer, self.dev_hints_on)
        #     elif not is_solved and key in '0123456789':
        #         try:
        #             self.sudoku[pointer] = ord(key) - ord('0')
        #             self.draw_items(board_box, pointer, self.dev_hints_on)
        #         except Exception as e:
        #             self.type_message_in_box(message_box, str(e))
        #     else:
        #         self.type_message_in_box(
        #             message_box,
        #             'Unknown button.\nMake sure you switched to EN.'
        #         )
        #         self.window.refresh()
            self.type_score_in_box(help_box, f'Score: {self.score}')

            self.window.refresh()
        self.main_menu.display()
