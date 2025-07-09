import arcade
import arcade.gui
import logging
# import game data  # FIX REMOVE SPACE

logging.basicConfig(filename='latest.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Statki.temp"
WINDOW_ICON = "battleship.png"

# class for main game window
class GameView(arcade.View):

    def __init__(self, size):
        super().__init__()
        self.manager = arcade.gui.UIManager()

        self.background_color = arcade.color.AMAZON

        self.grid_sprite_list = arcade.SpriteList()

        self.grid_sprites = []

        # create 5 10x10 grids and place them on board
        # for 1080p (for now)
        width, height = size
        wr = width / 1920 # window ratio

        margin_grid = 75 * wr
        size_big = (51 * wr, 2 * wr)
        size_sml = (30.9 * wr, 2 * wr)
        # grid_num =:   1, 2, 3 are small, 4, 5 are large

        # create 3 other players' grids:
        for num in range(1, 6):
            self.grid_sprites.append([])
            for row in range(10):
                self.grid_sprites[num-1].append([])
                for col in range(10):
                    if num in [1, 2, 3]:
                        w, m = size_sml
                        x = (margin_grid * num + col * (w + m) + (w / 2))
                        x += (num - 1) * (10 * w + 9 * m)
                        y =  height - (margin_grid + row * (w + m) + (w / 2))
                        sprite = arcade.SpriteSolidColor(w, w,
                                                         color=arcade.color.RED)
                        sprite.center_x = x
                        sprite.center_y = y
                        self.grid_sprites[num - 1][row].append(sprite)
                        self.grid_sprite_list.append(sprite)

                    if num in [4, 5]:
                        w, m = size_big
                        x = (margin_grid * (num - 3) + col * (w + m) + (w / 2))
                        x += (num - 4) * (10 * w + 9 * m)
                        y =  (margin_grid + row * (w + m) + (w / 2))
                        sprite = arcade.SpriteSolidColor(w, w,
                                                         color=arcade.color.RED)
                        sprite.center_x = x
                        sprite.center_y = y
                        self.grid_sprites[num - 1][row].append(sprite)
                        self.grid_sprite_list.append(sprite)
                    else:
                        logger.error(f"tried to create grid {num=}")


        # Create a list of solid-color sprites to represent each grid location


    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.grid_sprite_list.draw()


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        print(self.grid_sprites)
        print(x, y)


    def on_show(self):
        self.manager.enable()


    def on_hide(self):
        self.manager.disable()



def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
                           fullscreen=True)
    window_size = arcade.get_window().size

    game = GameView(window_size)

    window.show_view(game)

    arcade.run()


if __name__ == "__main__":
    main()

# TODO
# read: todo.md