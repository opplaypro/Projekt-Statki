# this file contains necessary classes required for a game
# The game is intended to be played by four players

import logging

logging.basicConfig(filename='latest.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Cell:
    def __init__(self):
        self.ships: set[int] = set()  # set of player id who has ship in cell
        self.shots: set[int] = set()  # set if player id who shot this cell
        self.extra_data: dict = {}  # space for extra data that can be stored
        # in
        # cell


# class for board of every player
class Board:
    def __init__(self, owner_id: int = -1):
        self.owner_id = owner_id
        self.cells: list[list[Cell]] = [[Cell() for _ in range(10)] for _ in range(10)]


class Player:
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name

    def shot_from_enemy(self, x: int, y: int, enemy_id: int):
        ...  # TODO


def setup_game() -> list[Player]:
    players = []
    for i in range(4):
        name = input(f"Enter name for player {i + 1}: ")  # get player name
        players.append(Player(i, name))
    return players


class Game:
    def __init__(self):
        self.players = setup_game()
        self.boards = [Board() for _ in range(5)]
