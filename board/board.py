import socket
import os
import json
import logger_config
from exceptions import StaleMateException
from datetime import datetime

LOG_FILE_PATH = f"/tmp/{os.getenv("SERVER_NAME")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"

flog = logger_config.get_file_logger(LOG_FILE_PATH, logger_config.logging.DEBUG)
clog = logger_config.get_console_logger(logger_config.logging.DEBUG)

class Board():
    """
    Represents the board of the TicTacToe game. Acts as a broker server for
    the players after a publisher-subscriber fashion.

    Parameters:
        rows (int): Number of rows of the board.
        cols (int): Number of columns of the board.

    Attributes:
        rows (int): Number of rows of the board.
        cols (int): Number of columns of the board.
        board (2D char list (rows x cols)): Matrix-like structure that holds
                                            the current state of the game.

        topics (dict {'char': tuple(str, str)}): Topics which the players may
                                                 publish or subscribe to. The 
                                                 keys are the pieces used by 
                                                 each player and the values the
                                                 addresses of the players 
                                                 subscribed to each piece.

        socket (socket.socket): Socket for communication with the players.
    """

    def __init__(self, rows, cols):
        """
        Initialize the Board with its dimension, with all boxes empty and
        create the socket.

        Args:
            rows (int): Number of rows.
            cols (int): Number of columns.
        """
        self.__rows = rows
        self.__cols = cols
        self.__board = [[' ' for i in range(0, self.__cols)] for i in range(0, self.__rows)]
        self.__topics = {}
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    def __str__(self):
        """
        String representation of the board.

        Returns:
            str: Basic but useful graphic interface for the terminal.
        """
        s = ""
        for row in range(self.__rows):
            hor_div = "\n-" + "----" * self.__cols + "\n"
            s += hor_div + "| "
            for col in range(self.__cols):
                s += self.__board[row][col] + " | "
        s += hor_div
        return s
    
    
    def __out(self, x, y):
        """
        Check if a position is outside of the board.

        Args:
            x (int): Horizontal coordinate.
            y (int): Vertical coordinate.

        Returns:
            bool: True if the position is outside the board; False otherwise.
        """
        return x >= self.__cols or y >= self.__rows
    
    
    def __empty(self, x, y):
        """
        Check whether a box is empty or not.

        Args:
            x (int): Horizontal coordinate.
            y (int): Vertical coordinate.

        Raises:
            IndexError: If the box is outside the board.

        Returns:
            bool: True if the character in the box is ' '; False otherwise.
        """
        if self.__out(x, y):
            raise IndexError(f"[BOARD]: Position [{x},{y}]: OUT OF BOARD")
        return self.__board[x][y] == ' '
    
    
    def __check_horizontal_vertical(self):
        """
        Check victory condition based on row or column completion,
        but no diagonal.

        Returns:
            bool: True if a row or column is completely filled with the same
                  kind of piece; False otherwise.
        """
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
        """
        Check victory condition based on main diagonal completion.

        Returns:
            bool: True if the main diagonal is completely filled with the same
                  kind of piece; False otherwise.
        """
        return self.__board[0][0] != ' ' and all(self.__board[0][0] == self.__board[i][i] for i in range (1, self.__rows))
    
    
    def __check_anti_diagonal(self):
        """
        Check victory condition based on anti diagonal completion.

        Returns:
            bool: True if the anti diagonal is completely filled with the same
                  kind of piece; False otherwise.
        """
        if self.__empty(0, self.__cols - 1):
            return False
        
        # Start on top-right corner
        j = self.__cols - 1
        piece = self.__board[0][j]

        # Each iteration increase row by one and decrease column by one
        for i in range(self.__rows):
            if self.__board[i][j] != piece:
                return False
            j -= 1
        return True
    
    
    def __place(self, x, y, piece):
        """
        Place a piece in a certain box on the board.

        Args:
            x (int): Horizontal coordinate.
            y (int): Vertical coordinate.
            piece (char): Piece symbol.

        Raises:
            IndexError: If the box is already occupied.
        """
        if not self.__empty(x, y):
            raise IndexError(f"[BOARD]: Position [{x},{y}]: OCCUPIED")
        self.__board[x][y] = piece


    def __end_condition(self):
        """
        Check all victory or stalemate conditions to determine whether the
        game has ended.

        Raises:
            StaleMateException: If all boxes are filled but no victory
                                condition has been achieved.

        Returns:
            bool: True if victory condition is achieved; False otherwise.
        """
        if all(not self.__empty(i, j) for i in range(0, self.__rows) for j in range(self.__cols)):
            raise StaleMateException("[BOARD]: STALEMATE: END OF GAME")

        return self.__check_horizontal_vertical() or self.__check_main_diagonal() \
            or self.__check_anti_diagonal()
    
    
    def serve(self):
        """
        Act as a broker for the players while the game is on course. Manage
        the flow of the game by handling connection and message exchange.
        """
        # Initialize socket
        self.__socket.bind((os.getenv("SERVER_NAME"), int(os.getenv("SERVER_PORT"))))
        self.__socket.listen(2)
        clog.info("The server is running...")
        flog.info("Server start")

        # Wait for both players to be connected. Store socket connections
        # and initialize token subscriptions and give the players starting
        # turns based on who connected first.
        conns = []
        for i in range(2):
            conn, addr = self.__socket.accept()
            clog.info(f"Connected to {addr}")
            flog.info(f"Connected to {addr}")

            conns.append(conn)
            sub = conn.recv(1024).decode('utf-8')
            clog.info(f"[{addr}]: Subscribe request to topic {sub}")
            flog.info(f"[{addr}]: Subscribe request to topic {sub}")

            conn.send(f"[BOARD]: Subscribed to piece {sub},{i}".encode('utf-8'))
            self.__topics[sub] = conn
            clog.debug(f"[DEBUG]: Added topic {sub}")
            flog.debug(f"[DEBUG]: Added topic {sub}")
            clog.info(f"Subscribed {addr} to topic {sub}")
            flog.info(f"Subscribed {addr} to topic {sub}")


        pieces = [key for key in self.__topics.keys()]
        turn = 0
        
        # Serve until the game is over
        while True:
            # Receive piece and position from the player who have the turn
            data = json.loads(conns[turn].recv(1024).decode('utf-8'))
            piece, position = next(iter(data.items()))

            # Try to place the piece checking all possible restrictions
            try:
                self.__place(position[0], position[1], piece)
                print(self)
    
                # Check if the game is over
                if self.__end_condition():
                    conns[turn].send(f"[BOARD]: YOU WIN!".encode('utf-8'))
                    self.__topics[piece].send(f"[BOARD]: YOU LOSE...".encode('utf-8'))
                    clog.debug(f"[DEBUG]: Winner: {pieces[turn]}")
                    flog.debug(f"[DEBUG]: Winner: {pieces[turn]}")
                    return

                # If successful, inform both players of the changes and update turn
                conns[turn].send(f"[BOARD]: Piece placed at {position}".encode('utf-8'))
                self.__topics[piece].send(f"[BOARD]: Adversary move: {position}".encode('utf-8'))
                clog.debug(f"[DEBUG]: Piece {pieces[turn]} placed at {position}")
                flog.debug(f"[DEBUG]: Piece {pieces[turn]} placed at {position}")
                turn = (turn + 1) % len(pieces)
                clog.debug(f"[DEBUG]: Next turn: {pieces[turn]}")
                flog.debug(f"[DEBUG]: Next turn: {pieces[turn]}")

            except IndexError as e:
                conns[turn].send(str(e).encode('utf-8'))
                clog.debug(f"[DEBUG]: {e}")
                flog.debug(f"[DEBUG]: {e}")
            except StaleMateException as sm:
                conns[turn].send(str(sm).encode('utf-8'))
                self.__topics[piece].send(str(sm).encode('utf-8'))
                clog.debug(f"[DEBUG]: {sm}")
                flog.debug(f"[DEBUG]: {sm}")
                return


def main():
    """
    Main program. Simply create the board server and launch it.
    """

    board = Board(3, 3)
    board.serve()
    clog.info("END OF THE GAME")
    flog.info("Server shut down")

if __name__ == "__main__":
    main()



        
        

        


