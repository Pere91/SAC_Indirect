import socket
import os
import threading
import time

class Board:
    def __init__(self, rows, cols):
        self.__rows = rows
        self.__cols = cols
        self.__board = [[' ' for i in range(0, self.__cols)] for i in range(0, self.__rows)]
    
    def __str__(self):
        return '\n'.join('|'.join(row) for row in self.__board)
    
    def __out(self, x, y):
        return x >= self.__cols or y >= self.__rows
    
    def __empty(self, x, y):
        if self.__out(x, y):
            raise IndexError(f"Position [{x},{y}]: OUT OF BOARD")
        return self.__board[x][y] == ' '
    
    def __check_horizontal_vertical(self):
        for i in range(0, self.__rows):
            if all(x == self.__board[i][0] and x != ' ' for x in self.__board[i]) \
            or all(y == self.__board[i][0] and y != ' ' for y in [row[i] for row in self.__board]):
               return True
        return False
            
    @property
    def rows(self):
        return self.__rows
    
    @property
    def cols(self):
        return self.__cols
    
    def place(self, x, y, piece):
        if not self.__empty(x, y):
            raise IndexError(f"Position [{x},{y}]: OCCUPIED")
        self.__board[x][y] = piece

    def check_end(self):
        return self.__check_horizontal_vertical()
    

def main():
    board = Board(3, 3)
    board.place(0, 0, 'O')
    board.place(1, 0, 'O')
    board.place(2, 0, 'O')
    print(board.check_end())

if __name__ == "__main__":
    main()