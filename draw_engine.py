import arcade
import arcade.gui
import logging

import gui_windows as gw
# import gamedata  # FIX REMOVE SPACE

logging.basicConfig(filename='latest.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)

WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
WINDOW_TITLE = "Statki.temp"


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=False)
    window_size = arcade.get_window().size
    main_window = gw.MainMenuView()
    window.show_view(main_window)
    arcade.run()


if __name__ == "__main__":
    main()
    print("test")

# TODO
# read: todo.md
