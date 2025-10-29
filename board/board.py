import socket
import select
import os
import json
from exceptions import StaleMateException

class Board():
    def __init__(self, rows, cols):
        self.__rows = rows
        self.__cols = cols
        self.__board = [[' ' for i in range(0, self.__cols)] for i in range(0, self.__rows)]
        self.__topics = {} # {'O': [], 'X': []}
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def __str__(self):
        s = ""
        for row in range(self.__rows):
            hor_div = "\n-" + "----" * self.__cols + "\n"
            s += hor_div + "| "
            for col in range(self.__cols):
                s += self.__board[row][col] + " | "
        s += hor_div
        return s
    
    def __out(self, x, y):
        return x >= self.__cols or y >= self.__rows
    
    def __empty(self, x, y):
        if self.__out(x, y):
            raise IndexError(f"Position [{x},{y}]: OUT OF BOARD")
        return self.__board[x][y] == ' '
    
    def __check_horizontal_vertical(self):
        for i in range(0, self.__rows):
            # Horizontal check
            if not self.__empty(i, 0) and all(x == self.__board[i][0] for x in self.__board[i]):
                return True
            
            # Vertical check
            col = [row[i] for row in self.__board]
            if not self.__empty(0, i) and all(x == col[0] for x in col):
               return True
        return False
    
    def __check_main_diagonal(self):
        return self.__board[0][0] != ' ' and all(self.__board[0][0] == self.__board[i][i] for i in range (1, self.__rows))
    
    def __check_anti_diagonal(self):
        if self.__empty(0, self.__cols - 1):
            return False
        
        piece = self.__board[0][self.__cols - 1]
        j = self.__cols - 1
        for i in range(self.__rows):
            if self.__board[i][j] != piece:
                return False
            j -= 1
        return True
            
    @property
    def rows(self):
        return self.__rows
    
    @property
    def cols(self):
        return self.__cols
    
    def __place(self, x, y, piece):
        if not self.__empty(x, y):
            raise IndexError(f"Position [{x},{y}]: OCCUPIED")
        self.__board[x][y] = piece

    def check_end(self):
        if all(not self.__empty(i, j) for i in range(0, self.__rows) for j in range(self.__cols)):
            raise StaleMateException("STALEMATE: END OF GAME")

        return self.__check_horizontal_vertical() or self.__check_main_diagonal() \
            or self.__check_anti_diagonal()
    
    def serve(self):
        self.__socket.bind((os.getenv("SERVER_NAME"), int(os.getenv("SERVER_PORT"))))
        self.__socket.listen(2)

        print("The server is running...")

        conns = []
        for i in range(2):
            conn, addr = self.__socket.accept()
            print(f"Connected to {addr}")
            conns.append(conn)
            sub = conn.recv(1024).decode('utf-8')
            self.__topics[sub] = conn
        
        while True:
            pubs, _, _ = select.select(conns, [], [])

            for pub in pubs:
                data = json.loads(pub.recv(1024).decode('utf-8'))
                piece, position = next(iter(data.items()))
                print(f"Received: {position}, type: {type(position)}")
                self.__place(position[0], position[1], piece)
                print(self)
                self.__topics[piece].send(str(position).encode('utf-8'))


def main():
    board = Board(3, 3)
    board.serve()

if __name__ == "__main__":
    main()



        
        

        


