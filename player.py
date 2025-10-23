import socket
import os
import time

class Board:
    def __init__(self, rows, cols):
        self.__rows = rows
        self.__cols = cols
        self.__board = [[' ' for i in range(0, self.__cols)] for i in range(0, self.__rows)]

    def __out(self, x, y):
        return x >= self.__cols or y >= self.__rows
    
    def __str__(self):
        return '\n'.join('|'.join(row) for row in self.__board)
    
    @property
    def rows(self):
        return self.__rows
    
    @property
    def cols(self):
        return self.__cols

    def empty(self, x, y):
        if self.__out(x, y):
            raise IndexError(f"Position [{x},{y}]: OUT OF BOARD")
        return self.__board[x][y] == ' '
    
    def place(self, x, y, piece):
        if not self.empty(x, y):
            raise IndexError(f"Position [{x},{y}]: OCCUPIED")
        self.__board[x][y] = piece
    


class Player:

    def __init__(self, board):
        self.__board = board
        self.__name = os.getenv("PLAYER_NAME")
        self.__piece = self.__assign_piece()
        self.__foe_addr = self.__get_foe_addr()

    def __assign_piece(self):
        if self.__name == "player1":
            return 'O'
        else:
            return 'X'
        
    def __get_foe_addr(self):
        players = os.getenv("PLAYER_HOSTS").split(',')
        return [p for p in players if not p.startswith(self.__name)]


    def set_piece(self, x, y):
        try:
            self.__board.place(x, y, self.__piece)
        except IndexError as e:
            print(e)

    def show_board(self):
        print(self.__board)


def main():
    player = Player(Board(3, 3))


if __name__ == "__main__":
    main()