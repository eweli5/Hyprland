#!/usr/bin/env python3
import curses
import os

BIN_DIR = "/usr/local/bin"

PINNED_APPS = [
    "kew",
    "fastfetch",
    "peaclock",
    "btop",
]


# ── scan ────────────────────────────────────────────────────

def scan_local_bin():
    if not os.path.isdir(BIN_DIR):
        return []

    return sorted([
        f for f in os.listdir(BIN_DIR)
        if os.path.isfile(os.path.join(BIN_DIR, f))
        and os.access(os.path.join(BIN_DIR, f), os.X_OK)
    ])


def build_menu():
    menu = []

    menu.append(("PINNED", None))
    for app in PINNED_APPS:
        menu.append(("PIN", app))

    menu.append(("LOCAL BIN", None))
    for app in scan_local_bin():
        menu.append(("BIN", app))

    return menu


# ── execution ───────────────────────────────────────────────

def run(app):
    curses.endwin()

    path = os.path.join(BIN_DIR, app)
    if os.path.exists(path) and os.access(path, os.X_OK):
        os.execv(path, [app])

    os.execvp(app, [app])


# ── drawing with scroll ─────────────────────────────────────

def draw(stdscr, menu, selectable_idx, top):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    stdscr.addstr(0, 0, "Launcher (scrollable)", curses.A_BOLD)

    visible_height = h - 2
    y = 1

    for i in range(top, len(menu)):
        if y >= h:
            break

        section, app = menu[i]

        if app is None:
            line = f"[ {section} ]"
            stdscr.addstr(y, 0, line[:w-1], curses.A_DIM | curses.A_BOLD)
        else:
            line = f"  {app}"
            if i == selectable_idx:
                stdscr.addstr(y, 0, line[:w-1], curses.A_REVERSE)
            else:
                stdscr.addstr(y, 0, line[:w-1])

        y += 1

    stdscr.refresh()


# ── main ────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(100)

    menu = build_menu()
    selectable = [i for i, m in enumerate(menu) if m[1] is not None]

    pos = 0
    top = 0

    while True:
        h, w = stdscr.getmaxyx()

        draw(stdscr, menu, selectable[pos], top)

        key = stdscr.getch()

        if key == -1:
            continue

        if key in (ord('q'), 27):
            break

        elif key == curses.KEY_UP:
            pos = max(0, pos - 1)

        elif key == curses.KEY_DOWN:
            pos = min(len(selectable) - 1, pos + 1)

        # ── scroll logic ──
        sel_screen_y = selectable[pos]

        if sel_screen_y < top:
            top = sel_screen_y

        elif sel_screen_y >= top + (h - 2):
            top = sel_screen_y - (h - 2) + 1

        elif key in (10, 13):
            idx = selectable[pos]
            run(menu[idx][1])


if __name__ == "__main__":
    curses.wrapper(main)
