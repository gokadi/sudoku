import curses

from menu import Menu, MenuItem, MenuItemCallback
from snake.gui import SnakeMain
from sudoku.gui import SudokuMain


class MainMenu:
    def __init__(self, window):
        self.window = window
        self.screen_sizes = self.window.getmaxyx()
        sudoku_menu = SudokuMain(self.window).main_menu
        snake_menu = SnakeMain(self.window).main_menu
        main_menu_items = [
            MenuItem('Sudoku', MenuItemCallback(sudoku_menu.display)),
            MenuItem('Snake', MenuItemCallback(snake_menu.display)),
            MenuItem('Exit', MenuItemCallback(lambda: True))
        ]
        self.main_menu = Menu(main_menu_items, self.window, self.screen_sizes)
        self.main_menu.display()


if __name__ == '__main__':
    curses.wrapper(MainMenu)
