import socket
import os
import threading
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
        self.__port = int(os.getenv("PLAYER_PORT"))
        self.__piece = self.__assign_piece()
        self.__turn = self.__piece == 'O'
        self.__foe_addr = self.__get_foe_addr()

    def __assign_piece(self):
        if self.__name == "player1":
            return 'O'
        else:
            return 'X'
        
    def __get_foe_addr(self):
        players = os.getenv("PLAYER_HOSTS").split(',')
        foe = [p for p in players if not p.startswith(self.__name)]
        ip, port = foe[0].split(':')
        return (ip, int(port))
    
    def __subscribe_worker(self):
        foe_piece = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        foe_piece.bind(("0.0.0.0", self.__port))

        while True:
            data, _ = foe_piece.recvfrom(1024)
            piece, coord = data.decode('utf-8').split(':')
            x, y = coord.split(',')
            self.set_piece(int(x), int(y), piece)
            self.__turn = True

    @property
    def turn(self):
        return self.__turn

    def set_piece(self, x, y, piece):
        self.__board.place(x, y, piece)


    def show_board(self):
        print(self.__board)

    def publish(self, box):
        self_piece = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        x, y = box.split(',')
        self.set_piece(int(x), int(y), self.__piece)
        data = self.__piece + ":" + box
        self_piece.sendto(data.encode('utf-8'), self.__foe_addr)
        self.__turn = False

    def subscribe(self):
        threading.Thread(target=self.__subscribe_worker, daemon=True).start()

def main():
    player = Player(Board(3, 3))

    player.subscribe()

    while True:
        if player.turn:
            print("\n")
            player.show_board()
            print("\nPlace your piece: ")
            while True:
                try:
                    box = input()
                    player.publish(box)
                    break
                except IndexError as e:
                    print(e)
                    print("Try again: ")


if __name__ == "__main__":
    main()