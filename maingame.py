from gamedata import *

def turn(game_data, current_player: int):
    player = game_data.players[current_player]
    print(f"{player.name}'s turn")

    while True:
        try:
            x = int(input("Enter x coordinate to shoot: "))
            y = int(input("Enter y coordinate to shoot: "))
            if 0 <= x < game_data.size and 0 <= y < game_data.size:
                break
            else:
                print(f"Coordinates must be between 0 and {game_data.size-1}.")
        except ValueError:
            print("Invalid input. Please enter integers for coordinates.")

    result = player.player_board.shoot_cell(x, y)
    if result == 1:
        print("Hit!")
    elif result == 0:
        print("Miss!")
    else:
        print("Already shot at this cell.")
