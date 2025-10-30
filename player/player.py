import socket
import os
import json
import logger_config
from datetime import datetime

PIECES = ['O', 'X']
LOG_FILE_PATH = f"/tmp/{os.getenv("PLAYER_NAME")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log" 

flog = logger_config.get_file_logger(LOG_FILE_PATH, logger_config.logging.DEBUG)
clog = logger_config.get_console_logger(logger_config.logging.DEBUG)

class Player:
    """
    Represents a player of the TicTacToe game. Acts as a client that
    publishes to the topic labeled with the piece it uses and is subscribed to
    the piece used by its adversary.

    Attributes:
        name (str): Name of the player from the environment variables.
        socket (socket.socket): Socket for communication with the board server.
        piece (char): Piece used by the player.
        is_first (bool): Whether the player if first to play or not.
        finished (bool): Whether the player has finished the game or not.
    """

    def __init__(self):
        """
        Initialize the Player.
        """
        self.__name = os.getenv("PLAYER_NAME")
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__piece = None
        self.__is_first = None
        self.__finished = False


    @property
    def name(self):
        """
        Getter for name attribute.

        Returns:
            str: Name of the player.
        """
        return self.__name
    

    @property
    def is_first(self):
        """
        Getter for is_first attribute.

        Returns:
            bool: True if player is first to play; False otherwise.
        """
        return self.__is_first
    
    
    @property
    def finished(self):
        """
        Getter for finished attribute.

        Returns:
            bool: True if player has finished the game; False otherwise.
        """
        return self.__finished
    
    
    @property
    def piece(self):
        """
        Getter for piece attribute.

        Returns:
            char: Piece used by the player.
        """
        return self.__piece
    

    @piece.setter
    def piece(self, value):
        """Setter for piece attribute.

        Args:
            value (char): New value for the piece attribute.
        """
        self.__piece = value


    def publish(self, box):
        """
        Publish a message to the topic labeled with the player's piece.
        Message contains a dictionary with the player's piece as key and
        a list with the box coordinates as value: {'piece': [x, y]}.

        Args:
            box (str): Coordinates of the box chosen by the player, separated
                       by a comma: X,Y.
        """

        # Keep retrying while the player input is incorrect
        while True:
            # Format and send the message to the server
            x, y = box.split(',')
            pub = {self.__piece: [int(x), int(y)]}
            self.__socket.send(json.dumps(pub).encode('utf-8'))
            clog.debug(f"Attempt to place piece at {[x, y]}")
            flog.debug(f"Attempt to place piece at {[x, y]}")

            # Await server response
            resp = self.__socket.recv(1024).decode('utf-8')
            clog.info(resp)
            flog.info(resp)

            # Check if end game condition is achieved
            if "WIN" in resp or "LOSE" in resp or "STALEMATE" in resp:
                self.__finished = True
                break
            
            # Check if box is available
            if "OCCUPIED" not in resp and "OUT OF BOARD" not in resp:
                break

            # Repeat if box was unavailable
            box = input("Place your piece: ")


    def subscribe(self, piece):
        """
        Subscribe to the topic labeled with a given piece (ideally the
        adversary's piece). Used to establish connection with the server.

        Args:
            piece (char): Label of the topic to be subscribed to.
        """

        # Connect to the server
        self.__socket.connect((os.getenv("SERVER_NAME"), int(os.getenv("SERVER_PORT"))))

        # Send the piece to be subscribed to
        self.__socket.send(piece.encode('utf-8'))
        clog.debug(f"Attempt to subscribe to topic {piece}")
        flog.debug(f"Attempt to subscribe to topic {piece}")

        # Await server response
        resp = self.__socket.recv(1024).decode('utf-8')

        # Parse server response to get the starting turn
        msg, turn = resp.split(',')
        clog.info(msg)
        flog.info(msg)
        self.__is_first = int(turn) == 0


    def wait(self):
        """
        Wait for the other player to make its move. Thus, the player is
        blocked while it's not its turn.
        """

        # Await server notification with the update caused by the adversary
        # move.
        clog.info("Waiting for adversary to play...")
        resp = self.__socket.recv(1024).decode('utf-8')
        clog.info(resp)
        flog.info(resp)

        # Check jf end game condition is achieved
        if "WIN" in resp or "LOSE" in resp or "STALEMATE" in resp:
            self.__finished = True
            clog.debug("[DEBUG]: Game end condition achieved")
            flog.debug("[DEBUG]: Game end condition achieved")


def main():
    """
    Main program. Create the player and guide it through the game's stages
    by prompting it.
    """

    # Ask player to choose a piece
    player = Player()
    piece = input("Choose your piece: ['O' / 'X'] ")
    clog.debug(f"[DEBUG]: Piece input: {piece}")
    flog.debug(f"[DEBUG]: Piece input: {piece}")

    # If the piece selected is incorrect, keep asking
    while piece not in PIECES:
        clog.info("Piece must be either 'O' or 'X'")
        piece = input()
        clog.debug(f"[DEBUG]: Piece input: {piece}")
        flog.debug(f"[DEBUG]: Piece input: {piece}")

    clog.info(f"Chose piece: {piece}")
    flog.info(f"Chose piece: {piece}")

    # Based on the piece selected, subscribe to adversary's piece
    player.piece = piece
    ad_piece = [p for p in PIECES if p != piece][0]
    player.subscribe(ad_piece)
    clog.debug(f"[DEBUG]: Request sent for subscribe to topic: {ad_piece}")
    flog.debug(f"[DEBUG]: Request sent for subscribe to topic: {ad_piece}")

    # The first player to connect to the server makes the first move
    if player.is_first:
        box = input("Place your piece: ")
        player.publish(box)

    # Game loop: player waits for its turn to publish. After both the player's
    #            and the adversary's turn the end game condition is checked.
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