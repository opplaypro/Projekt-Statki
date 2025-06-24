# -*- coding: utf-8 -*-
# Creates player class with name and empty board
class Player:
    def __init__(self, name: str, size: int):
        self.name: str = name
        self.player_board: PlayerBoard = PlayerBoard(size)


# class for cell on plaer's board, for now just a state
class PlayerCell:
    def __init__(self, state=0):
        self.state = state
        # 0 - empty, 1 - ship, 2 - hit, 3 - miss


# board for each player
class PlayerBoard:
    def __init__(self, s):
        self.size = s
        self.cells = [[PlayerCell() for y in range(s)] for x in range(s)]
        # 0 - empty, 1 - ship, 2 - hit, 3 - miss

    def get_cell(self, x, y):
        return self.cells[x][y]

    def set_cell(self, x, y, state):
        self.cells[x][y].state = state

    # returns 1 if hit, 0 if miss, -1 if already shot
    def shoot_cell(self, x, y):
        if self.cells[x][y] == 1:
            self.cells[x][y] = 2
            return 1  # hit
        elif self.cells[x][y] == 0:
            self.cells[x][y] = 3
            return 0  # miss
        else:
            return -1  # already shot

    def place_ship(self, ship, x, y, d):
        # d = 0 - up, 1 - right, 2 - down, 3 - left
        if d == 0:
            for i in range(-1, ship + 1):
                if self.get_cell(x - i, y - 1).state != 0:
                    return False
                if self.get_cell(x - i, y).state != 0:
                    return False
                if self.get_cell(x - i, y + 1).state != 0:
                    return False


# class for cell on common board
class CommonCell:
    def __init__(self, state=0, player_id=-1):
        self.state = state
        # 0 - empty, 1 - ship, 2 - hit, 3 - miss
        self.player_id = player_id
        # id of player who owns the cell, -1 if empty


# one central board for all players
class CommonBoard:
    def __init__(self, s, c):
        self.size = s
        self.cells = [[CommonCell() for y in range(s)] for x in range(s)]

    def get_cell(self, x, y):
        return self.cells[x][y]

    def set_cell(self, x, y, state):
        self.cells[x][y].state = state

    def shoot_cell(self, x, y):
        if self.cells[x][y] == 1:
            self.cells[x][y] = 2
            return 1
        elif self.cells[x][y] == 0:
            self.cells[x][y] = 3
            return 0
        else:
            return -1


class GameData:
    def __init__(self, size):
        self.players = []
        self.size = size
        self.center = PlayerBoard(size)

    def add_player(self, name):
        self.players.append(Player(name, self.size))


def round(Game):
    current_player = 0
    while True:
        print(f"Player {current_player + 1}'s turn")
        player_id = int(input("Enter player ID to shoot (1-4): ")) - 1
        if player_id == current_player:
            print("You cannot shoot yourself!")
            continue
        print(f"Choose cell on Player {player_id + 1}'s board to shoot:")
        while True:
            x = int(input("Enter x coordinate: "))
            y = int(input("Enter y coordinate: "))
            if 0 <= x < Game.size and 0 <= y < Game.size:
                break
            else:
                print(f"Coordinates must be between 0 and {Game.size - 1}.")
        if Game.players[player_id].player_board.shoot_cell(x, y) == 1:
            print("Hit!")
        elif Game.players[player_id].player_board.shoot_cell(x, y) == 0:
            print("Miss!")
        else:
            print("Already shot!")
        current_player = (current_player + 1) % len(Game.players)


def test():
    size = 10
    Game = GameData(size)
    for i in range(4):
        Game.add_player(f"Player {i}")
    print(1)
    Game.players[0].player_board.place_ship(3, 7, 4, 0)
    round(Game)


def main():
    size = 10
    Game = GameData(size)
    Game.add_player("Player 1")


if __name__ == "__main__":
    test()


'''
# -*- coding: utf-8 -*-

class PlayerBoard:
    def __init__(self, s):
        self.size = s
        self.cells = [[PlayerCell() for y in range(s)] for x in range(s)]
        # 0 - empty, 1 - ship, 2 - hit, 3 - miss

    def get_cell(self, x, y):
        return self.cells[x][y]

    def set_cell(self, x, y, state):
        self.cells[x][y].state = state

    # returns 1 if hit, 0 if miss, -1 if already shot
    def shoot_cell(self, x, y):
        if self.cells[x][y] == 1:
            self.cells[x][y] = 2
            return 1  # hit
        elif self.cells[x][y] == 0:
            self.cells[x][y] = 3
            return 0  # miss
        else:
            return -1  # already shot

    def place_ship(self, ship, x, y, d):
        # d = 0 - up, 1 - right, 2 - down, 3 - left
        if d == 0:
            for i in range(-1, ship + 1):
                if self.get_cell(x - i, y - 1).state != 0:
                    return False
                if self.get_cell(x - i, y).state != 0:
                    return False
                if self.get_cell(x - i, y + 1).state != 0:
                    return False




# one central board for all players
class CommonBoard:
    def __init__(self, s, c):
        self.size = s
        self.cells = [[CommonCell() for y in range(s)] for x in range(s)]

    def get_cell(self, x, y):
        return self.cells[x][y]

    def set_cell(self, x, y, state):
        self.cells[x][y].state = state

    def shoot_cell(self, x, y):
        if self.cells[x][y] == 1:
            self.cells[x][y] = 2
            return 1
        elif self.cells[x][y] == 0:
            self.cells[x][y] = 3
            return 0
        else:
            return -1


class GameData:
    def __init__(self, size):
        self.players = []
        self.size = size
        self.center = PlayerBoard(size)

    def add_player(self, name):
        self.players.append(Player(name, self.size))


def round(Game):
    current_player = 0
    while True:
        print(f"Player {current_player + 1}'s turn")
        player_id = int(input("Enter player ID to shoot (1-4): ")) - 1
        if player_id == current_player:
            print("You cannot shoot yourself!")
            continue
        print(f"Choose cell on Player {player_id + 1}'s board to shoot:")
        while True:
            x = int(input("Enter x coordinate: "))
            y = int(input("Enter y coordinate: "))
            if 0 <= x < Game.size and 0 <= y < Game.size:
                break
            else:
                print(f"Coordinates must be between 0 and {Game.size - 1}.")
        if Game.players[player_id].player_board.shoot_cell(x, y) == 1:
            print("Hit!")
        elif Game.players[player_id].player_board.shoot_cell(x, y) == 0:
            print("Miss!")
        else:
            print("Already shot!")
        current_player = (current_player + 1) % len(Game.players)


def test():
    size = 10
    Game = GameData(size)
    for i in range(4):
        Game.add_player(f"Player {i}")
    print(1)
    Game.players[0].player_board.place_ship(3, 7, 4, 0)
    round(Game)


def main():
    size = 10
    Game = GameData(size)
    Game.add_player("Player 1")


if __name__ == "__main__":
    test()

'''
