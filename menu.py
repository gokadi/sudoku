import curses
from curses import panel
from typing import Optional, List, Callable


class Menu:
    def __init__(
        self,
        items: list,
        window,
        screen_sizes: tuple,
        type_messages: Optional[List[Callable]]
    ):
        self.window = window
        self.type_messages = type_messages
        self.screen_sizes = screen_sizes
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.window.refresh()

        self.active_menu_item_index = 0
        self.items = items
        self.items.append(('Exit', 'exit'))
        self.is_menu_active = False

    def navigate(self, n: int):
        self.active_menu_item_index += n
        if self.active_menu_item_index < 0:
            self.active_menu_item_index = len(self.items) - 1
        elif self.active_menu_item_index >= len(self.items):
            self.active_menu_item_index = 0

    def display(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.window.bkgd(' ', curses.color_pair(1))
        self.window.clear()
        self.window.refresh()

        max_len_of_menu_item = max(len(item[0]) for item in self.items)
        initial_x_position = (
            self.screen_sizes[1] - max_len_of_menu_item
        ) // 2
        initial_y_position = (
            self.screen_sizes[0] - len(self.items)
        ) // 2

        while not self.is_menu_active:
            for type_msg_func in self.type_messages:
                type_msg_func()
            self.window.refresh()
            for index, item in enumerate(self.items):
                is_item_chosen = index == self.active_menu_item_index
                menu_item_label = item[0]
                self.window.addstr(
                    initial_y_position + index, initial_x_position,
                    menu_item_label,
                    curses.A_REVERSE if is_item_chosen else curses.A_NORMAL
                )

            key = self.window.getch()
            active_item = self.items[self.active_menu_item_index]

            if key in [curses.KEY_ENTER, ord('\n')]:
                # refactor this to new MenuItem type
                do_need_exit = (
                    isinstance(active_item[1][0], Callable)
                    and active_item[1][0]()
                )
                self.is_menu_active = do_need_exit or (
                    self.active_menu_item_index == len(self.items) - 1
                )

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)

        self.is_menu_active = False
        self.window.clear()
        self.window.refresh()
        # refactor this
        if len(active_item[1]) == 2:
            active_item[1][1]()

    def hide(self):
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()
        self.window.refresh()
