import curses
from enum import Enum

from menu import MenuItem, MenuItemCallback, Menu
from snake.backend import Snake, Coordinates

HELP_BOX_COLUMNS = 30
CONTROLS_HELP = (
    'Chosen level: {level}.\nControls:\n- (N) new game;\n'
    '- (↑↓→←) move;\n- (Space) pause;\n- (Q) quit.'
)


class Levels(int, Enum):
    easy = 140
    normal = 80
    hard = 50


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
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.main_menu = self.get_menu()

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

    def _get_and_draw_textbox(self, init_row: int, init_column: int) -> tuple:
        textbox_wrapper = self.window.subwin(
            self.screen_sizes[0], HELP_BOX_COLUMNS, init_row, init_column
        )
        textbox_wrapper.box()
        textbox_wrapper.refresh()
        textbox = textbox_wrapper.subwin(
            self.screen_sizes[0] - 2, HELP_BOX_COLUMNS - 2,
            init_row + 1, init_column + 1
        )

        return textbox, textbox_wrapper

    @staticmethod
    def type_message_in_box(box, message: str):
        box.move(0, 0)
        box.addstr(message)

    def type_score_in_box(self, box, message: str):
        box.move(
            self.screen_sizes[0] - 3, (HELP_BOX_COLUMNS - len(message)) // 2
        )
        box.clrtoeol()
        box.refresh()
        box.addstr(message, curses.A_BOLD)
        box.refresh()

    def draw_snake(self, box, snake: Snake):
        for snake_tail in snake.tail:
            box.move(snake_tail.row, snake_tail.column)
            box.addstr('⧳', curses.color_pair(2))
        box.move(snake.head.row, snake.head.column)
        box.addstr('◍', curses.color_pair(1))
        box.refresh()

    def draw_apples(self, box, apples: list):
        for apple in apples:
            try:
                box.move(apple.row, apple.column)
            except Exception as e:
                assert False, (apple.row, apple.column, e)
            box.addstr('◍', curses.color_pair(1) | curses.A_BOLD)
        box.refresh()

    def start_game(self):
        init_row = 0
        init_column = 0
        board_rows = self.screen_sizes[0]
        board_columns = self.screen_sizes[1] - HELP_BOX_COLUMNS

        board_box = self.window.subwin(
            self.screen_sizes[0],
            self.screen_sizes[1] - HELP_BOX_COLUMNS,
            init_row, init_column
        )
        board_box.box()
        help_box, help_box_wrapper = self._get_and_draw_textbox(
            init_row, board_columns
        )
        help_box.clear()

        snake = Snake(init_row, init_column, board_rows, board_columns)

        self.draw_snake(board_box, snake)
        self.draw_apples(board_box, snake.apples)

        board_box.keypad(1)
        key = curses.KEY_RIGHT
        failed = False
        board_box.timeout(self.level + len(snake.snake_coordinates))
        while not failed:
            help_box.clear()
            self.type_message_in_box(
                help_box, CONTROLS_HELP.format(level=self.level.name)
            )
            self.type_score_in_box(help_box, f'Score: {self.score}')
            previous_key = key
            event = board_box.getch()
            if event != -1:
                key = event

            if key == ord('q'):
                break
            elif key == ord('n'):
                key = curses.KEY_RIGHT
                board_box.clear()
                board_box.box()
                board_box.refresh()
                help_box.clear()
                snake = Snake(
                    init_row, init_column, board_rows, board_columns
                )
                self.score = 0
                self.draw_snake(board_box, snake)
            elif key == ord(' '):
                key = None
                while key != ord(' '):
                    help_box.clear()
                    self.type_message_in_box(
                        help_box, 'Paused. Press space to continue.'
                    )
                    key = self.window.getch()
                key = previous_key
            elif key not in (
                curses.KEY_DOWN,
                curses.KEY_UP,
                curses.KEY_RIGHT,
                curses.KEY_LEFT,
            ):
                key = previous_key
            elif (
                previous_key == curses.KEY_DOWN and key == curses.KEY_UP
                or previous_key == curses.KEY_UP and key == curses.KEY_DOWN
                or previous_key == curses.KEY_LEFT and key == curses.KEY_RIGHT
                or previous_key == curses.KEY_RIGHT and key == curses.KEY_LEFT
            ):
                key = previous_key
            else:
                new_row = (
                    snake.head.row
                    + (key == curses.KEY_DOWN and 1)
                    + (key == curses.KEY_UP and -1)
                )
                new_column = (
                    snake.head.column
                    + (key == curses.KEY_RIGHT and 1)
                    + (key == curses.KEY_LEFT and -1)
                )
                snake.snake_coordinates.insert(
                    0, Coordinates(row=new_row, column=new_column)
                )

                if (
                    snake.is_stuck_in_borders(board_rows, board_columns)
                    or snake.is_stuck_with_self()
                ):
                    failed = True
                elif snake.head in snake.apples:
                    curses.beep()
                    self.score += 1
                    snake.apples.remove(snake.head)
                    snake.apples.append(snake.generate_apple())
                    self.draw_apples(board_box, snake.apples)
                else:
                    tail_end = snake.snake_coordinates.pop()
                    board_box.addstr(tail_end.row, tail_end.column, ' ')
                self.draw_snake(board_box, snake)

            if failed:
                board_box.clear()
                board_box.refresh()
                help_box_wrapper.clear()
                help_box_wrapper.refresh()
                board_box.addstr(
                    self.screen_sizes[0] // 2,
                    self.screen_sizes[1] // 2 - 4,
                    'YOU LOST!'
                )
                board_box.addstr(
                    self.screen_sizes[0] // 2 + 1,
                    self.screen_sizes[1] // 2 - 8,
                    f'Your score is: {self.score}.'
                )
                board_box.addstr(
                    self.screen_sizes[0] // 2 + 2,
                    self.screen_sizes[1] // 2 - 6,
                    '[Press Enter]'
                )
                self.score = 0
                while True:
                    key = board_box.getch()
                    if key in [curses.KEY_ENTER, ord('\n')]:
                        break

        self.main_menu.display()

