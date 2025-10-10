import msvcrt
import os
import random
import time
from dataclasses import dataclass

from pyfiglet import figlet_format

from .tut import tut
from .utils import WRandom


@dataclass
class C:
    RESET = "\033[0m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    CYAN = "\033[96m"


EMPTY = " "
WIN_COMBOS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def clsscr() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def display_winner(winner: str) -> None:
    match winner:
        case "Draw":
            print("draw...")
        case "X":
            print(f"{C.RED}YOU{C.RESET} won!")
        case "O":
            print(f"The {C.CYAN}AI{C.RESET} won!")


class Board:
    def __init__(self) -> None:
        self.reset()

    def __str__(self) -> str:
        def colorize(cell) -> str:
            match cell:
                case "X":
                    return C.RED + "X" + C.RESET
                case "O":
                    return C.CYAN + "O" + C.RESET
                case _:
                    return EMPTY

        b = [colorize(c) for c in self.board]
        g, r = C.GRAY, C.RESET
        return "\n".join(
            [
                f" {b[0]} {g}|{r} {b[1]} {g}|{r} {b[2]} ",
                f"{g}---+---+---{r}",
                f" {b[3]} {g}|{r} {b[4]} {g}|{r} {b[5]} ",
                f"{g}---+---+---{r}",
                f" {b[6]} {g}|{r} {b[7]} {g}|{r} {b[8]} ",
            ]
        )

    def __getitem__(self, position: int) -> str:
        return self.board[position]

    def reset(self):
        self.round = 1
        self.board = [EMPTY] * 9

    def update(self, position: int, player: str) -> bool:
        idx = position - 1
        if self.board[idx] == EMPTY:
            self.board[idx] = player
            self.round += 1
            return True
        return False

    @staticmethod
    def is_winner(board_state, mark):
        positions = {i for i, v in enumerate(board_state) if v == mark}
        return any(combo <= positions for combo in map(set, WIN_COMBOS))


def menu():
    options = [
        ("h", "Play TicTacToe"),
        ("j", "How to Win Every Time"),
        ("q", "Quit"),
    ]
    key_to_index = {k: i for i, (k, _) in enumerate(options)}
    while True:
        clsscr()
        figlet = figlet_format("TicTacToe")
        print(f"{C.GRAY}{figlet}\naka tcubed{C.RESET}\n")
        for key, label in options:
            print(f"{C.GRAY}[{key}]{C.RESET} {label}")

        key = msvcrt.getch().decode().lower()
        if key in key_to_index:
            return key_to_index[key]


class TicTacToe:
    keymap = {
        b"q": 1,
        b"w": 2,
        b"e": 3,
        b"a": 4,
        b"s": 5,
        b"d": 6,
        b"z": 7,
        b"x": 8,
        b"c": 9,
    }
    revmap = {v: k.decode() for k, v in keymap.items()}

    def __init__(self) -> None:
        self.running = True
        self.winner = None
        self.board = Board()

    def _draw_board(self) -> None:
        clsscr()
        g, r = C.GRAY, C.RESET
        print("Tic-Tac-Toe\n")
        print(self.board)
        print("\nControls:\n")

        keys = [EMPTY] * 9
        for k, v in self.keymap.items():
            keys[v - 1] = k.decode()
        for row in range(3):
            line = " {} {}|{} {} {}|{} {} ".format(
                keys[row * 3], g, r, keys[row * 3 + 1], g, r, keys[row * 3 + 2]
            )
            print(line)
            if row < 2:
                print(f"{g}-----------{r}")
        print(f"\n({C.RED}X{r}=You, {C.CYAN}O{r}=Computer, f=quit, r=restart)\n")

    def _reset_game(self, nodraw: bool = False) -> None:
        self.board.reset()
        self.winner = None
        self.running = True
        if nodraw:
            self._draw_board()

    def _get_human_move(self) -> str | None:
        while True:
            if not msvcrt.kbhit():
                time.sleep(0.01)
                continue
            key = msvcrt.getch()
            if key == b"\x03":  # Ctrl+C
                self.running = False
                return
            match key:
                case k if k in self.keymap:
                    move = self.keymap[k]
                    if self.board[move - 1] == EMPTY:
                        self.board.update(move, "X")
                        return
                case k if k in (b"f", b"F"):
                    self.running = False
                    return "quit"
                case k if k in (b"r", b"R"):
                    time.sleep(0.05)
                    self._reset_game(True)
                    return "reset"

    def _get_ai_move(self) -> None:
        board = self.board.board
        free = [i + 1 for i, v in enumerate(board) if v == EMPTY]
        if not free:
            return

        # 1. Win if possible
        for pos in free:
            temp = board[:]
            temp[pos - 1] = "O"
            if Board.is_winner(temp, "O"):
                self.board.update(pos, "O")
                return

        # 2. Block player win
        for pos in free:
            temp = board[:]
            temp[pos - 1] = "X"
            if Board.is_winner(temp, "X"):
                self.board.update(pos, "O")
                return

        corners = [p for p in [1, 2, 3, 4, 6, 7, 8, 9] if p in free]
        if corners:
            self.board.update(random.choice(corners), "O")
            return

        if 5 in free:
            self.board.update(5, "O")
            return

        # Pick random
        self.board.update(random.choice(free), "O")

    def _check_winner(self, symbol) -> bool:
        return Board.is_winner(self.board.board, symbol)

    def _update_game_state(self):
        for mark, winner in (("X", "X"), ("O", "O")):
            if self._check_winner(mark):
                self.winner = winner
                self.running = False
                return
        if EMPTY not in self.board.board:
            self.winner = "Draw"
            self.running = False

    def __call__(self):
        while True:
            choice = menu()
            match choice:
                case 0:
                    self._play_game()
                case 1:
                    tut()
                case _:
                    break

    def _post_game_menu(self):
        g, c, r = C.GRAY, C.CYAN, C.RESET
        print(f"\n{g}What would you like to do next?{r}")
        print(f"{c}[h]{r} {g}Rematch{r}")
        print(f"{c}[j]{r} {g}Return to main menu{r}")
        print(f"{c}[k]{r} {g}Exit game{r}")
        while True:
            key = msvcrt.getch()
            match key:
                case k if k in (b"h",):
                    return "rematch"
                case k if k in (b"j",):
                    return "menu"
                case k if k in (b"k", b"q", b"Q"):
                    return "exit"

    def _play_game(self):
        while True:
            self._draw_board()
            self._reset_game(True)
            if WRandom([("X", 3), ("O", 1)]).choice() == "O":
                self._get_ai_move()
                self._draw_board()
            while self.running:
                match self._get_human_move():
                    case "reset":
                        continue
                    case "quit":
                        exit(0)
                self._update_game_state()
                if not self.running:
                    break
                self._get_ai_move()
                self._draw_board()
                self._update_game_state()

            display_winner(self.winner or " ")

            clsscr()
            print(self.board)
            display_winner(self.winner or " ")
            match self._post_game_menu():
                case "rematch":
                    self.board.reset()
                    continue
                case "menu":
                    break
                case "exit":
                    exit(0)


def main():
    game = TicTacToe()
    game()


if __name__ == "__main__":
    main()
