import socket
import os
import json

PIECES = ['O', 'X']

class Player:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__piece = None
        self.__is_first = None
        self.__finished = False

    @property
    def is_first(self):
        return self.__is_first
    
    @property
    def finished(self):
        return self.__finished
    
    @property
    def piece(self):
        return self.__piece
    
    @piece.setter
    def piece(self, value):
        self.__piece = value

    def publish(self, box):
        while True:
            x, y = box.split(',')
            pub = {self.__piece: [int(x), int(y)]}
            self.__socket.send(json.dumps(pub).encode('utf-8'))
            resp = self.__socket.recv(1024).decode('utf-8')
            print(resp)

            if "WIN" in resp or "LOSE" in resp or "STALEMATE" in resp:
                self.__finished = True
                break
            
            if "OCCUPIED" not in resp and "OUT OF BOARD" not in resp:
                break
            box = input("Place your piece: ")

    def subscribe(self, piece):
        self.__socket.connect((os.getenv("SERVER_NAME"), int(os.getenv("SERVER_PORT"))))
        self.__socket.send(piece.encode('utf-8'))
        resp = self.__socket.recv(1024).decode('utf-8')
        msg, turn = resp.split(',')
        print(msg)
        self.__is_first = int(turn) == 0

    def wait(self):
        print("Waiting for adversary to play...")
        resp = self.__socket.recv(1024).decode('utf-8')
        print(resp)
        if "WIN" in resp or "LOSE" in resp or "STALEMATE" in resp:
            self.__finished = True


def main():
    player = Player()
    piece = input("Choose your piece: ['O' / 'X'] ")

    while piece not in PIECES:
        print("Piece must be either 'O' or 'X'")
        piece = input()

    player.piece = piece
    ad_piece = [p for p in PIECES if p != piece][0]
    player.subscribe(ad_piece)

    if player.is_first:
        box = input("Place your piece: ")
        player.publish(box)

    while True:
        player.wait()
        if player.finished:
            break

        box = input("Place your piece: ")
        player.publish(box)
        if player.finished:
            break

if __name__ == "__main__":
    main()