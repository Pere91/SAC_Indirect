import socket
import os
import json

class Player:

    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def turn(self):
        return self.__turn

    def publish(self, box):
        x, y = box.split(',')
        pub = {self.__piece: [int(x), int(y)]}
        self.__socket.send(json.dumps(pub).encode('utf-8'))
        resp = self.__socket.recv(1024).decode('utf-8')
        print(resp)

    def subscribe(self, piece):
        self.__piece = piece
        self.__socket.connect((os.getenv("SERVER_NAME"), int(os.getenv("SERVER_PORT"))))
        self.__socket.send(self.__piece.encode('utf-8'))


def main():
    player = Player()
    piece = input("Choose your piece: ['O' / 'X'] ")
    player.subscribe(piece)

    while True:
        box = input("Place you piece: ")
        player.publish(box)


if __name__ == "__main__":
    main()