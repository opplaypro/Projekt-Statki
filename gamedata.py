# this file contains necessary classes required for game
# game is intended to be played by four players
# usage:
# from gamedata import *


class Cell:
    def __init__(self, celldata: tuple[int, int]):
        self.state = celldata[0]
        self.player_id = celldata[1]
        # celldata is a tuple of (state, player_id)
        # state = 0 - empty, 1 - ship, 2 - hit, 3 - miss
        # player_id is the id of the player who owns the cell, -1 if empty

    def shoot(self):
        if self.state == 0:
            self.state = 3
            return 0  # miss
        elif self.state == 1:
            self.state = 2
            return 1  # hit
        else:
            return -1


# class for board of every player
class Board:
    def __init__(self, player_id: int = -1):
        self.id = player_id
        self.cells = [
            [Cell((0, player_id)) for _ in range(10)] for _ in range(10)
            ]


class Player:
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.board = Board(player_id)

    def shoot_enemy(self, x: int, y: int, enemy_id: int):
        ...
        '''
        cell = self.board.cells[x][y]
        result = cell.shoot()
        if result == 1:
            print(f"{self.name} hit enemy {enemy_id}'s ship at ({x}, {y})!")
        elif result == 0:
            print(f"{self.name} missed at ({x}, {y}).")
        else:
            print(f"{self.name} already shot at ({x}, {y}).")
        return result'''


def setup_game() -> list[Player]:
    players = []
    for i in range(4):
        name = input(f"Enter name for player {i + 1}: ")  # get player name
        players.append(Player(i, name))
    return players


class Game:
    def __init__(self):
        self.players = setup_game()