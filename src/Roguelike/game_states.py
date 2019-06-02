from enum import Enum

class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMIES_TURN = 2
    PLAYER_DEAD = 3
    SHOWING_INVENTORY = 4
    DROPPING_INVENTORY = 5