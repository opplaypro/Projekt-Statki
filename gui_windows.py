import traceback
import arcade
import arcade.gui
import logging
from datetime import datetime
import maingame as mg
import pyperclip as pc

is_player = -1  # global variable to check if player or server, -1 undefined, 0 server, 1 player

logging.basicConfig(filename='latest.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)



# Main menu of the game
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.background_color = arcade.color.CITRON

        width, height = self.size
        wr = height / 1080  # window ratio

        # create buttons with relative size
        switch_menu_button = arcade.gui.UIFlatButton(text="Start", width=250*wr)

        @switch_menu_button.event("on_click")
        def on_click_switch_button(event):
            # Passing the main view into menu view as an argument.
            connect_menu_view = ConnectMenuView(self)
            self.window.show_view(connect_menu_view)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=switch_menu_button,
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.CITRON)

        self.manager.enable()


# menu for connecting
class ConnectMenuView(arcade.View):
    def __init__(self, previous_view: arcade.View):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.background_color = arcade.color.MAHOGANY

        width, height = self.size
        wr = height / 1080  # window ratio

        # create buttons with relative size
        join_button = arcade.gui.UIFlatButton(text="Join", width=250*wr)
        create_button = arcade.gui.UIFlatButton(text="Create", width=250*wr)
        back_button = arcade.gui.UIFlatButton(text="Back", width=250*wr)

        @join_button.event("on_click")
        def on_click_connect(event):
            join_menu_view = JoinMenuView(self)
            self.window.show_view(join_menu_view)

        @create_button.event("on_click")
        def on_click_exit(event):
            code = mg.create_lobby_server()
            create_menu_view = CreateMenuView(self, code)
            self.window.show_view(create_menu_view)

        @back_button.event("on_click")
        def on_click_back(event):
            if previous_view:
                self.window.show_view(previous_view)


        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=join_button,
            align_y=100 * wr,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=create_button,
            align_y=0,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=back_button,
            align_y=-100 * wr,
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.MAHOGANY)

        self.manager.enable()


class JoinMenuView(arcade.View):
    def __init__(self, previous_view: arcade.View):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.push_handlers(self)
        self.background_color = arcade.color.BLUSH
        self.is_input_focused = False

        width, height = self.size
        wr = height / 1080  # window ratio

        # create input field and a button to join the game
        self.enter_code_text = arcade.gui.UITextArea(text="Enter game code below", width=250*wr,
                                                     text_color=arcade.color.BLACK)
        self.enter_code_field = arcade.gui.UIInputText(width=250*wr, text_color=arcade.color.BLACK)
        join_button = arcade.gui.UIFlatButton(text="Join", width=250*wr)
        back_button = arcade.gui.UIFlatButton(text="Back", width=250*wr)


        @self.enter_code_field.event("on_focus")
        def on_focus_input(event):
            self.is_input_focused = True

        @self.enter_code_field.event("on_blur")
        def on_blur_input(event):
            self.is_input_focused = False

        @join_button.event("on_click")
        def on_click_back(event):
            try:
                global is_player
                is_player = 1
                server_address = mg.decode_ip(self.enter_code_field.text)
                mg.join_lobby_player(server_address)

                create_board_view = CreateBoardView(self)
                self.window.show_view(create_board_view)
            except Exception as e:
                print(e)
                self.enter_code_field.text = "Wrong code"

        @back_button.event("on_click")
        def on_click_back(event):
            try:
                mg.threads[0].terminate()
            except Exception as e:
                logger.error(f"[{datetime.now():%H:%M:%S}] Error terminating connection: {e}")
            if previous_view:
                self.window.show_view(previous_view)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.enter_code_text,
            align_y=100 * wr,
        )

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.enter_code_field,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=join_button,
            align_y=-100 * wr,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=back_button,
            align_y=-200 * wr,
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.V and (modifiers & arcade.key.MOD_CTRL):
            self.enter_code_field.text = pc.paste()
            return True
        return False

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLUSH)

        self.manager.enable()


class CreateMenuView(arcade.View):
    def __init__(self, previous_view: arcade.View, lobby_code: str):
        self.lobby_code = lobby_code
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.background_color = arcade.color.LAVENDER

        width, height = self.size
        wr = height / 1080  # window ratio

        # create buttons with relative size
        lobby_code = arcade.gui.UIFlatButton(text=lobby_code, width=250*wr,
                                             text_color=arcade.color.BLACK)
        create_button = arcade.gui.UIFlatButton(text="Create", width=250*wr)
        back_button = arcade.gui.UIFlatButton(text="Back", width=250*wr)
        # field showing code for players to connect
        # TODO
        # field with connected players

        @lobby_code.event("on_click")
        def on_click_lobby_code(event):
            pc.copy(self.lobby_code)

        @create_button.event("on_click")
        def on_click_create(event):
            global is_player
            is_player = 0
            create_board_view = CreateBoardView(self)
            self.window.show_view(create_board_view)

        @back_button.event("on_click")
        def on_click_back(event):
            try:
                mg.threads[1].terminate()
            except Exception as e:
                logger.error(f"[{datetime.now():%H:%M:%S}] Error terminating connection: {e}")
                logger.error(f"[{datetime.now():%H:%M:%S}] {traceback.format_exc()}")
            if previous_view:
                self.window.show_view(previous_view)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=lobby_code,
            align_y=100 * wr,
        )

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=create_button,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=back_button,
            align_y=-100 * wr,
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.LAVENDER)
        self.manager.enable()


class CreateBoardView(arcade.View):
    def __init__(self, previous_view: arcade.View):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.push_handlers(self)
        self.background_color = arcade.color.OXFORD_BLUE
        self.grid_sprite_list = arcade.SpriteList()
        self.ships_sprite_list = arcade.SpriteList()
        self.grid_sprites = []
        self.selected_ship = None
        self.highlighted_sprites = []
        self.placed_ships = []
        self.board_state = [[0 for _ in range(10)] for _ in range(10)]  # 0: empty, 1: ship, 2: forbidden
        self.state_colors = {0: arcade.color.GRAY, 1: arcade.color.TEAL, 2: arcade.color.GRAY}
        self.mouse_x = 0
        self.mouse_y = 0

        # get ratio correct
        width, height = self.size
        self.wr = height / 1080  # window ratio

        # Add a confirm button
        self.confirm_button = arcade.gui.UIFlatButton(text="Confirm", width=250 * self.wr)
        self.confirm_button.disabled = True

        @self.confirm_button.event("on_click")
        def on_click_confirm(event):
            if self.confirm_button.disabled:
                return
            # send ready signal
            mg.send_data({'status': 'ready'})
            # Pass the board state to the game view
            game_view = GameView(self, self.board_state)
            self.window.show_view(game_view)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(
            anchor_x="right",
            anchor_y="center_y",
            child=self.confirm_button,
            align_x=-200 * self.wr
        )

        size = (75 * self.wr, 2 * self.wr)
        w, m = size

        # create 1 10x10 grid and place it on the left
        self.grid_sprites.append([])
        for row in range(10):
            self.grid_sprites[0].append([])
            for col in range(10):
                x = (156 * self.wr + col * (w + m) + (w / 2))
                y = height - (156 * self.wr + row * (w + m) + (w / 2))
                # noinspection PyTypeChecker
                sprite = arcade.SpriteSolidColor(w, w, color=arcade.color.GRAY)
                sprite.center_x = x
                sprite.center_y = y
                self.grid_sprites[0][row].append(sprite)
                self.grid_sprite_list.append(sprite)

        # create ships on the right
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        start_x = 1100 * self.wr
        start_y = height - (156 * self.wr)
        for i, ship_size in enumerate(ship_sizes):
            ship_width = ship_size * w + (ship_size - 1) * m
            ship_height = w
            x = start_x + ship_width / 2
            y = start_y - i * (w + 20 * self.wr)
            # noinspection PyTypeChecker
            ship_sprite = arcade.SpriteSolidColor(int(ship_width), int(ship_height), color=arcade.color.WHITE)
            ship_sprite.center_x = x
            ship_sprite.center_y = y
            ship_sprite.properties['ship_size'] = ship_size
            ship_sprite.properties['is_horizontal'] = True
            ship_sprite.properties['original_x'] = x
            ship_sprite.properties['original_y'] = y
            self.ships_sprite_list.append(ship_sprite)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.grid_sprite_list.draw()
        self.ships_sprite_list.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if we are trying to place a ship on highlighted sprites
            if self.selected_ship and self.highlighted_sprites:
                # Check if placement is valid (not red)
                if self.highlighted_sprites and self.highlighted_sprites[0].color == arcade.color.GREEN:
                    grid_sprites_under_mouse = arcade.get_sprites_at_point((x, y), self.grid_sprite_list)
                    if any(sprite in self.highlighted_sprites for sprite in grid_sprites_under_mouse):
                        # Store ship info
                        ship_info = {
                            'sprite_ref': self.selected_ship,
                            'sprites': self.highlighted_sprites[:],
                            'size': self.selected_ship.properties['ship_size'],
                            'is_horizontal': self.selected_ship.properties['is_horizontal']
                        }
                        self.placed_ships.append(ship_info)

                        # Remove the ship from the list and deselect
                        self.selected_ship.remove_from_sprite_lists()
                        self.selected_ship = None

                        self._update_board_and_colors()
                        if sum(row.count(1) for row in self.board_state) == 20:
                            self.confirm_button.disabled = False
                        # Manually update to clear highlights
                        self.on_mouse_motion(x, y, 0, 0)
                        return

            # Check if we are clicking on an already placed ship
            grid_sprites_under_mouse = arcade.get_sprites_at_point((x, y), self.grid_sprite_list)
            if grid_sprites_under_mouse:
                clicked_sprite = grid_sprites_under_mouse[0]
                for ship_info in self.placed_ships:
                    if clicked_sprite in ship_info['sprites']:
                        # Pick up the ship
                        for sprite in ship_info['sprites']:
                            sprite.color = arcade.color.GRAY  # Reset grid color

                        # Re-add the original ship sprite to the list
                        ship_to_restore = ship_info['sprite_ref']
                        ship_to_restore.center_x = ship_to_restore.properties['original_x']
                        ship_to_restore.center_y = ship_to_restore.properties['original_y']
                        ship_to_restore.color = arcade.color.YELLOW
                        ship_to_restore.properties['is_horizontal'] = True
                        self.ships_sprite_list.append(ship_to_restore)
                        self.selected_ship = ship_to_restore

                        self.placed_ships.remove(ship_info)
                        self.confirm_button.disabled = True
                        self._update_board_and_colors()
                        self.on_mouse_motion(x, y, 0, 0)
                        return

            # Standard ship selection/deselection logic
            ships = arcade.get_sprites_at_point((x, y), self.ships_sprite_list)

            if self.selected_ship:
                self.selected_ship.color = arcade.color.WHITE
                self.selected_ship = None

            if ships:
                self.selected_ship = ships[0]
                self.selected_ship.color = arcade.color.YELLOW

            # We need to manually call on_mouse_motion to update highlighting without moving the mouse
            self.on_mouse_motion(x, y, 0, 0)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y
        # un-highlight previously highlighted sprites
        for sprite in self.highlighted_sprites:
            r, c = self._get_sprite_indices(sprite)
            if r != -1:
                sprite.color = self.state_colors[self.board_state[r][c]]
        self.highlighted_sprites.clear()

        if self.selected_ship:
            grid_sprites_under_mouse = arcade.get_sprites_at_point((x, y), self.grid_sprite_list)

            if grid_sprites_under_mouse:
                start_sprite = grid_sprites_under_mouse[0]
                ship_size = self.selected_ship.properties['ship_size']
                is_horizontal = self.selected_ship.properties['is_horizontal']

                # Find start sprite's indices
                start_row, start_col = self._get_sprite_indices(start_sprite)

                if start_row != -1:
                    sprites_to_highlight = []
                    valid_placement = True
                    if is_horizontal and start_col + ship_size <= 10:
                        for i in range(ship_size):
                            sprites_to_highlight.append(self.grid_sprites[0][start_row][start_col + i])
                    elif not is_horizontal and start_row + ship_size <= 10:
                        for i in range(ship_size):
                            sprites_to_highlight.append(self.grid_sprites[0][start_row + i][start_col])
                    else:
                        valid_placement = False

                    if valid_placement and sprites_to_highlight:
                        # Check for collision
                        is_colliding = False
                        for s in sprites_to_highlight:
                            r, c = self._get_sprite_indices(s)
                            if r != -1 and self.board_state[r][c] != 0:
                                is_colliding = True
                                break
                        color = arcade.color.RED if is_colliding else arcade.color.GREEN

                        for sprite in sprites_to_highlight:
                            sprite.color = color
                            self.highlighted_sprites.append(sprite)

    def _get_sprite_indices(self, sprite):
        for r_idx, row_list in enumerate(self.grid_sprites[0]):
            if sprite in row_list:
                c_idx = row_list.index(sprite)
                return r_idx, c_idx
        return -1, -1

    def _get_sprite_neighbors(self, r_idx, c_idx):
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r_idx + dr, c_idx + dc
                if 0 <= nr < 10 and 0 <= nc < 10:
                    neighbors.append(self.grid_sprites[0][nr][nc])
        return neighbors

    def _update_board_and_colors(self):
        # Reset board state
        self.board_state = [[0 for _ in range(10)] for _ in range(10)]

        # Mark ships and forbidden zones
        for ship_info in self.placed_ships:
            for sprite in ship_info['sprites']:
                r, c = self._get_sprite_indices(sprite)
                if r != -1:
                    self.board_state[r][c] = 1  # Mark as ship

        for r in range(10):
            for c in range(10):
                if self.board_state[r][c] == 1:
                    neighbors = self._get_sprite_neighbors(r, c)
                    for neighbor_sprite in neighbors:
                        nr, nc = self._get_sprite_indices(neighbor_sprite)
                        if nr != -1 and self.board_state[nr][nc] == 0:
                            self.board_state[nr][nc] = 2  # Mark as forbidden

        # Update sprite colors based on the final board state
        for r in range(10):
            for c in range(10):
                self.grid_sprites[0][r][c].color = self.state_colors[self.board_state[r][c]]

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.R and self.selected_ship:
            self.selected_ship.properties['is_horizontal'] = not self.selected_ship.properties['is_horizontal']
            # We need to manually call on_mouse_motion to update highlighting without moving the mouse
            self.on_mouse_motion(self.mouse_x, self.mouse_y, 0, 0)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.OXFORD_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()


# Menu when player is in the game
class GameView(arcade.View):
    def __init__(self, previous_view: arcade.View, player_board_state: list[list[int]] = None):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.background_color = arcade.color.SEA_BLUE
        self.grid_sprite_list = arcade.SpriteList()
        self.grid_sprites = []
        self.player_board_state = player_board_state
        self.game_started = False
        self.remote_player_ready = False
        self.waiting_for_shot_result = False

        # get ratio correct
        width, height = self.size
        self.wr = height / 1080  # window ratio

        # Waiting label
        self.waiting_label = arcade.gui.UILabel(text="Waiting for second player...", font_size=24,
                                                font_name="Arial", text_color=arcade.color.WHITE)

        # Turn indicator
        global is_player
        self.is_my_turn = (is_player == 0)  # Host starts
        turn_text = "Your turn" if self.is_my_turn else "Opponent's turn"
        self.turn_label = arcade.gui.UILabel(text=turn_text, font_size=24, font_name="Arial",
                                             text_color=arcade.color.WHITE)
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(child=self.waiting_label, anchor_x="center_x", anchor_y="top", align_y=-50 * self.wr)

        size = (75 * self.wr, 2 * self.wr)

        # create 2 10x10 grids and place them on board

        for i in range (0, 2):
            self.grid_sprites.append([])
            for row in range(10):
                self.grid_sprites[i].append([])
                for col in range(10):
                    w, m = size
                    x = (156 * self.wr + 72 * self.wr * i + col * (w + m) + (w / 2))
                    x += i * (10 * w + 9 * m)
                    y = height - (156 * self.wr + row * (w + m) + (w / 2))
                    # noinspection PyTypeChecker
                    color = arcade.color.DARK_GRAY
                    sprite = arcade.SpriteSolidColor(w, w, color=color)
                    sprite.center_x = x
                    sprite.center_y = y
                    self.grid_sprites[i][row].append(sprite)
                    self.grid_sprite_list.append(sprite)

        # Set player's board based on the state from CreateBoardView
        if player_board_state:
            state_colors = {0: arcade.color.GRAY, 1: arcade.color.TEAL, 2: arcade.color.GRAY}
            for r in range(10):
                for c in range(10):
                    state = player_board_state[r][c]
                    if state == 1:  # If there is a ship
                        self.grid_sprites[0][r][c].color = state_colors[state]

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.grid_sprite_list.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            if not self.game_started:
                return
            clicked_sprites = arcade.get_sprites_at_point((x, y), self.grid_sprite_list)
            if clicked_sprites:
                clicked_sprite = clicked_sprites[0]
                try:
                    index = self.grid_sprite_list.index(clicked_sprite)
                    if index >= 100:  # Opponent's grid
                        if clicked_sprite.color == arcade.color.DARK_GRAY:
                            clicked_sprite.color = arcade.color.LIGHT_GRAY
                        elif clicked_sprite.color == arcade.color.LIGHT_GRAY:
                            clicked_sprite.color = arcade.color.DARK_GRAY
                except ValueError:
                    pass
            return

        if not self.is_my_turn or not self.game_started or self.waiting_for_shot_result:
            return

        clicked_sprites = arcade.get_sprites_at_point((x, y), self.grid_sprite_list)

        if clicked_sprites:
            clicked_sprite = clicked_sprites[0]
            try:
                index = self.grid_sprite_list.index(clicked_sprite)

                # Clicks on player's own grid (left one) are ignored for shooting
                if index < 100:
                    return

                # Prevent shooting at the same spot twice or on marked cells
                if self.grid_sprite_list[index].color != arcade.color.DARK_GRAY:
                    return

                # It's a click on the opponent's grid (right one)
                row = (index - 100) // 10
                col = (index - 100) % 10

                # Send move to opponent
                mg.send_data({'move': (row, col)})

                self.waiting_for_shot_result = True

            except ValueError:
                pass

    def on_update(self, delta_time: float):
        # Check if game can start
        if not self.game_started and self.remote_player_ready:
            self.game_started = True
            self.anchor.remove(self.waiting_label)
            self.anchor.add(child=self.turn_label, anchor_x="center_x", anchor_y="top", align_y=-50 * self.wr)

        # Check for messages from the other player
        try:
            while not mg.queues['received'].empty():
                data = mg.queues['received'].get_nowait()

                if not self.game_started and 'status' in data and data['status'] == 'ready':
                    self.remote_player_ready = True

                elif self.game_started and 'move' in data:
                    row, col = data['move']
                    # This move is on our board (the left one)
                    is_hit = self.player_board_state[row][col] == 1
                    result = 'hit' if is_hit else 'miss'

                    # Send result back to the opponent
                    mg.send_data({'shot_result': result, 'coords': (row, col)})

                    # Update our own board visually
                    color = arcade.color.RED if is_hit else arcade.color.WHITE
                    self.grid_sprites[0][row][col].color = color

                    if result == 'miss':
                        self.is_my_turn = True
                        self.turn_label.text = "Your turn"
                    else:  # hit
                        self.is_my_turn = False
                        self.turn_label.text = "Opponent's turn"
                    self.turn_label.fit_content()

                elif self.game_started and 'shot_result' in data:
                    self.waiting_for_shot_result = False
                    result = data['shot_result']
                    row, col = data['coords']
                    color = arcade.color.RED if result == 'hit' else arcade.color.WHITE
                    # Update the opponent's grid (the right one)
                    index = 100 + row * 10 + col
                    self.grid_sprite_list[index].color = color

                    if result == 'miss':
                        self.is_my_turn = False
                        self.turn_label.text = "Opponent's turn"
                    else:  # hit
                        self.is_my_turn = True
                        self.turn_label.text = "Your turn"
                    self.turn_label.fit_content()

        except Exception as e:
            logger.error(f"[{datetime.now():%H:%M:%S}] Error processing queue: {e}")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            pause_view = PauseGameView(self)
            self.window.show_view(pause_view)

    def on_show(self):
        self.manager.enable()

    def on_hide(self):
        self.manager.disable()


''' # old code, 4P version, moving to 2P
# Menu when player is in the game
class GameView(arcade.View):
    def __init__(self, previous_view: arcade.View):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.background_color = arcade.color.AMAZON
        self.grid_sprite_list = arcade.SpriteList()
        self.grid_sprites = []

        # get ratio correct
        width, height = self.size
        wr = height / 1080  # window ratio
        margin_grid = 75 * wr
        size_big = (51 * wr, 2 * wr)
        size_sml = (30.9 * wr, 2 * wr)

        # create 5 10x10 grids and place them on board
        for num in range(1, 6):
            self.grid_sprites.append([])
            for row in range(10):
                self.grid_sprites[num - 1].append([])
                for col in range(10):
                    # create 3 smaller, other players' grids:
                    if num in [1, 2, 3]:
                        w, m = size_sml
                        x = (margin_grid * num + col * (w + m) + (w / 2))
                        x += (num - 1) * (10 * w + 9 * m)
                        y = height - (margin_grid + row * (w + m) + (w / 2))
                        # noinspection PyTypeChecker
                        sprite = arcade.SpriteSolidColor(w, w, color=arcade.color.RED)
                        sprite.center_x = x
                        sprite.center_y = y
                        self.grid_sprites[num - 1][row].append(sprite)
                        self.grid_sprite_list.append(sprite)

                    # create 2 bigger grids for player and common one:
                    elif num in [4, 5]:
                        w, m = size_big
                        x = (margin_grid * (num - 3) + col * (w + m) + (w / 2))
                        x += (num - 4) * (10 * w + 9 * m)
                        y = (margin_grid + row * (w + m) + (w / 2))
                        # noinspection PyTypeChecker
                        sprite = arcade.SpriteSolidColor(w, w, color=arcade.color.RED)
                        sprite.center_x = x
                        sprite.center_y = y
                        self.grid_sprites[num - 1][row].append(sprite)
                        self.grid_sprite_list.append(sprite)
                    else:
                        logger.error(f"[{datetime.now():%H:%M:%S}]tried to create grid {num=}")

        # Create a list of solid-color sprites to represent each grid location

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.grid_sprite_list.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        print(f"{x=}, {y=}, {button=}, {modifiers=}")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            pause_view = PauseGameView(self)
            self.window.show_view(pause_view)

    def on_show(self):
        self.manager.enable()

    def on_hide(self):
        self.manager.disable()'''


# pause menu
class PauseGameView(arcade.View):
    def __init__(self, game_view: GameView):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.game_view = game_view

        width, height = self.size
        wr = height / 1080  # window ratio

        # create buttons with relative size
        resume_button = arcade.gui.UIFlatButton(text="Resume", width=250*wr)
        exit_button = arcade.gui.UIFlatButton(text="Exit", width=250*wr)

        @resume_button.event("on_click")
        def on_click_resume(event):
            self.window.show_view(self.game_view)

        @exit_button.event("on_click")
        def on_click_exit(event):
            arcade.exit()

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=resume_button,
        )
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=exit_button,
            align_y=-100 * wr,
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BURGUNDY)
        self.manager.enable()


# for testing purposes
def main():
    window = arcade.Window(800, 450, "test", fullscreen=False, resizable=True)
    game = MainMenuView()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
