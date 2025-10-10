from .slides import Slides

RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"
YELLOW = "\033[33m"
SPACE_HL = "\033[42m"
RESET = "\033[0m"


def fmt_ttt(
    boards_dict: dict[str, dict],
) -> str:
    def colorize(c, idx, hl_set):
        if idx in hl_set:
            if c == " ":
                return f"{SPACE_HL} {RESET}"
            return f"{YELLOW}{c}{RESET}"
        match c:
            case "X":
                return f"{RED}{c}{RESET}"
            case "O":
                return f"{CYAN}{c}{RESET}"
            case _:
                return c

    def fmt_single(board, hl):
        board = board.upper().ljust(9)
        hl_set = set(i for i in hl if i >= 0)
        rows = []
        for i in range(0, 9, 3):
            row = f" {GRAY}|{RESET} ".join(
                colorize(c, i + j, hl_set) for j, c in enumerate(board[i : i + 3])
            )
            rows.append(" " + row + " ")
            if i < 6:
                rows.append(f"{GRAY}---+---+---{RESET}")
        return rows

    formatted_boards = []
    arrowed_indices = []
    or_indices = []
    for idx, (board, meta) in enumerate(boards_dict.items()):
        hl = meta.get("hl", (-1,))
        if not (isinstance(hl, tuple) and all(isinstance(x, int) for x in hl)):
            hl = (hl,)
        rows = fmt_single(board, hl)
        formatted_boards.append(rows)

        match meta:
            case {"arrowed": True}:
                arrowed_indices.append(idx)
            case {"ored": True}:
                or_indices.append(idx)
            case _:
                pass

    # Pad boards to equal height
    max_lines = max(len(b) for b in formatted_boards)
    for b in formatted_boards:
        while len(b) < max_lines:
            b.append(" " * len(b[0]))

    # Combine boards side by side
    combined = []
    for i in range(max_lines):
        line = ""
        for idx, b in enumerate(formatted_boards):
            prefix = "  "
            if i == max_lines // 2:
                if idx in arrowed_indices:
                    prefix = "->"
                elif idx in or_indices:
                    prefix = "or"
            line += prefix + b[i]
        combined.append(line)
    return "\n".join(combined)


slides = [
    f"""
1. You start first. (you=X, opp=O)

If you're first to move, you should always
pick a corner as they give you the most
chances to create multiple threats.

{fmt_ttt({"x": {}})}

we'll stick with this for now..""",
    f"""
2. [CASE 1] SKIP TO STEP 3 SAME CASE

If your opponent picks a corner then choose either
of the 2 remaining corners.

{fmt_ttt({"x o   x x": {"hl": (6, 8)}, "x x   o x": {"hl": (2, 8)}, "x x   x o": {"hl": (2, 6)}})}""",
    f"""
2. [CASE 2] SKIP TO STEP 3 SAME CASE

If your opponent picks an edge cell then choose any
unoccupied corner that is not touching the opponent's
cell apart from the corner opposite to you and it mustn't
make it so that your opponent's cell is between 2 of your
cells.

{fmt_ttt({"x xo": {"hl": 2}, "x x   xo": {"hl": (2, 6)}, "x x  ox": {"hl": (2, 6)}, "xo    x": {"hl": 6}})}""",
    """
2. [CASE 3] 

If your opponent picks the center then...
throw a german stick grenade— just kidding.

Pick the opposite corner from the one you chose first.
From here, there is no forced win — if your opponent
plays correctly, the game will always end in a draw.

If your opponent makes a mistake, you can still set up
forks or traps by choosing corners that are not adjacent,
but against perfect play, every winning path will be blocked.""",
    f"""
3. [CASE 1] corner

{fmt_ttt({"x o   x": {}})}

Normally your opponent block with:

{fmt_ttt({"x oo  x": {}})}

so after that you have to pick the last corner to get a fork.

{fmt_ttt({"x oo  x x": {}, "x oox xox": {"arrowed": True}, "x ooo xxx": {"ored": True}})}
""",
    f"""
3. [CASE 2] edge

{fmt_ttt({"x xo": {}, "x x    o": {}})}

after that your opponent will block with

{fmt_ttt({"xoxo": {"hl": 1}, "xox    o": {"hl": 1}})}

then we can pick any of the moves
highlighted below so we get two winning
positions.

{fmt_ttt({"xoxox   x": {"hl": (4, 8)}, "xox x  o": {"hl": (4, 6, 8)}})}""",
    """
4. Opponent Starts first

Pick the center if your opponent didn't pick it, if they didn't
then pick a corner.

After all of that you still have to block their every move because you
can't win unless your opponent is clueless.
""",
]


def tut() -> None:
    Slides(
        slides,
        f"{YELLOW}xo{RESET} = different options\n{SPACE_HL} {RESET} = successor move",
    ).run()


if __name__ == "__main__":
    tut()
