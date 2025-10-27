import socket
import os
import threading
from board import Board

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

    def check_end(self):
        return self.__board.check_end()

    def publish(self, box):
        self_piece = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        x, y = box.split(',')
        self.set_piece(int(x), int(y), self.__piece)
        data = self.__piece + ":" + box
        self_piece.sendto(data.encode('utf-8'), self.__foe_addr)
        self.__turn = False

    def subscribe(self):
        threading.Thread(target=self.__subscribe_worker, daemon=True).start()