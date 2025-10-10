import os
import shutil
from msvcrt import getch

DARKGRAY = "\033[90m"
RESET = "\033[0m"


class Slides:
    def __init__(self, slides: list[str], footer: str = "") -> None:
        self.slides = slides
        self.index = 0
        self.offset = 0  # track scroll offset
        self.footer = footer

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def show_slide(self) -> None:
        if not self.slides:
            return
        self.clear()
        try:
            height = shutil.get_terminal_size().lines
        except Exception:
            height = 24
        controls_height = 3  # Number of lines for controls/info
        footer_height = 1 if self.footer else 0
        reserved_height = controls_height + footer_height
        visible_height = height - reserved_height

        lines = self.slides[self.index].splitlines()
        total_lines = len(lines)
        # Clamp offset
        self.offset = max(0, min(self.offset, max(0, total_lines - visible_height)))
        # Print visible lines
        for line in lines[self.offset : self.offset + visible_height]:
            print(line)
        # Fill remaining space if slide is short
        for _ in range(visible_height - min(visible_height, total_lines - self.offset)):
            print()

        # Move cursor to bottom left
        print()
        print(f"\033[{height - controls_height - footer_height + 1};1H", end="")
        print(
            f"{DARKGRAY}[{RESET}{self.index + 1}{DARKGRAY}/{RESET}{len(self.slides)}{DARKGRAY}]{RESET}"
        )
        if self.footer:
            print(f"{self.footer}")
        print(
            f"{DARKGRAY}[n] Next  [p] Prev  [j] ↓  [k] ↑  [q] Quit{RESET}",
            end="",
            flush=True,
        )

    def run(self) -> None:
        if not self.slides:
            return

        size = len(self.slides)
        l_idx = -1
        while True:
            if self.index != l_idx:
                self.offset = 0  # Reset scroll on slide change
                self.show_slide()
                l_idx = self.index

            key = getch()
            lines = self.slides[self.index].splitlines()
            try:
                height = shutil.get_terminal_size().lines
            except Exception:
                height = 24
            controls_height = 3
            visible_height = height - controls_height
            max_offset = max(0, len(lines) - visible_height)

            if key in (b"\x00", b"\xe0"):
                getch()
                continue

            match key.decode().lower():
                case "n" if self.index < size - 1:
                    self.index += 1
                case "p" if self.index > 0:
                    self.index -= 1
                case "j":
                    if self.offset < max_offset:
                        self.offset += 1
                        self.show_slide()
                case "k":
                    if self.offset > 0:
                        self.offset -= 1
                        self.show_slide()
                case "q":
                    break
