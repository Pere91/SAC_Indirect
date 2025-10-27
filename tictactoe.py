from board import Board
from player import Player
from exceptions import StaleMateException

def main():
    player = Player(Board(3, 3))
    player.subscribe()

    while True:
        if player.turn:
            player.show_board()

            try:
                if player.check_end():
                    print("YOU LOSE...")
                    break
            except StaleMateException as e:
                print(e)
                break

            print("\nPlace your piece: ")

            while True:
                try:
                    box = input()
                    player.publish(box)
                    break
                except IndexError as e:
                    print(e)
                    print("Try again: ")

            try:
                if player.check_end():
                    player.show_board()
                    print("YOU WIN!")
                    break
            except StaleMateException as e:
                player.show_board()
                print(e)
                break


if __name__ == "__main__":
    main()