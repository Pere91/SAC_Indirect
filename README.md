# SAC_Indirect
A publisher-subscriber TicTacToe game implemented with sockets.

Indirect group communication assignment for Sistemes Actuals de Computació.

## Use
This application is designed to be launched in Docker containers, so please
follow the instructions carefully:

1. Create the containers' environment

> docker compose -up --build

2. Open three terminals and run one of the following commands on each one

> docker exec -it board sh
> docker exec -it player1 sh
> docker exec -it player2 sh

To make this process easier, you can run the bash script attached

> ./run.bash

3. Once inside each Docker container, run the Python scripts on them

Board terminal: > python3 board.py
Player terminals: > python3 player.py

4. Play the game on both player terminals; the board terminal shows the board:
    - Choose a piece, either 'O' or 'X' (capital letters)
    - Respecting the turns, enter box coordinates in this format: X,Y
    - Enjoy the game!

! A running Docker Engine is required.

Should someone prefer to run the app outside a container environment, mind that
the host addresses and ports should be adapted in the code.

## Introduction
This repository contains a version of the popular TicTacToe game implemented
following a publisher-subscriber design. 
All communication between the game's agents is handled with sockets. There are
three agents:

- Two players that play against each other, each one with a piece of its own.
- One board that contains the layout of the game area and the current state of
  the game.

The players act as clients to a server, which is the board. The pieces are the
identifiers for the tokens which the players subscribe and publish to. Each
player is subscribed to the other's piece and publishes to its own. The board
manages updates on the topics which affect the game state and the notifications
to the players, as well as the end game conditions: win, lose or stalemate.

## Design decisions
For the development of this project, the following decisions were made:

- The programming language used is Python, because it is the language the
  author has more experience with in socket related applications.
- The transport layer protocol chosen for this project is TCP, for it is
  connection oriented and ensures the data exchange consistency between the
  entities. Since this app is a turn based game between two players, this
  characteristics seemed fitting for maintaining a long term session between the
  two without risking packet loss.
- The deployment is done via Docker containers to provide a simulation of three
  different distributed systems.
- Both players are identical except for the piece they use. Besides, the piece
  is chosen by the players themselves, although only the first to arrive has a
  choice. This keeps a simplistic design that ensures an unbiased approach to
  the game.
- The dimension of the board is set by default to 3x3, although the app is
  design to work on any NxN layout. It may be modified within the Board class.


## Communication process

### Architecture
As mentioned earlier, each player acts both as publisher and subscriber,
depending on the piece it has: publishes to its own piece topic and is
subscribed to the adversary's piece topic. All publishing and subscribing goes
through the board, which acts as the broker and is responsible for notifying
the publishes on one topic to the player subscribed to it. The architecture is
shown in the following diagram:

tictactoe_architecture.png

### The Broker
The board operations are encapsulated into the Board class. Its serve() method
manages the connection to the players and all message exchange through the
topics. Thanks to this broker behavior, the players never need to contact each
other, not even know each other's addresses or information whatsoever.

All the board.py program does in its main() function is create the Board object
and call its serve() method. All other methods in this class are accessed via
serve().

The actions performed by the board are the following:

1. Bind the socket the the board's host address and port and put it to listen.
2. Accept two connections, which are the two players. The board gives the first
   connected player the starting turn.
3. Game loop: 
    - Receive a publish to the topic matching the current turn player's piece.
    - Try to place the piece on the board: if not possible (box occupied or out
      of board) notify the player to try another box; if possible, update the
      board and notify the adversary, which is subscribed to the piece's topic.
    - Check end game condition: if so, notify either win, lose or stalemate;
      otherwise, give the turn to the other player.


### Publishers
Publishing to topics is done via the publish() method of class Player. In this
method, the player proceeds as follows: 
1. Sends a message to the board which contains a dictionary
   with the player's piece (the topic) as key and a list with the X and Y
   coordinates of the box where to place it as value.
2. Waits for the server response. If the box is available, checks end game
   condition and if it is the case, exits the game.
3. If the box isn't available, it is prompted to choose another one.

### Subscribers
The subscribe() method of class Player is responsible for both the connection
to the server, i.e. the board, and the subscription to topics:
1. The player connects to the server, since it's host address and port are
   known thanks to the environment variables in the docker-compose.yml file.
2. Sends a message containing the adversary's piece to indicate that it wants
   to subscribe to that topic.
3. Awaits server confirmation.

### Program flow
The game flow takes place in the main() function of the player.py program. It
goes through the following steps:




## Final considerations

## Bonus: *Brokerless* version
An early version of the game have been preserved on a separate branch since it
presents an, although fully functional, entirely different approach to the same
problem: an implementation with no broker, e.i. only the two players to manage
the communication.
In this case, the control layer protocol used is UDP since it better simulates
a *careless* message publishing or subscribing in an architecture where both
agents are directly connected to each other. This direct connection was the
reason this approach was finally discarded.
Should anyone want to test it, please check the version/No_Broker branch on
this same repository.