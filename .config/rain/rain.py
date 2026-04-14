#!/usr/bin/env python3
import curses
import random
import time

# Each drop: [y, x, length, speed]
def create_drop(H, W):
    return [
        random.randint(0, H - 1),
        random.randint(0, W - 1),
        random.randint(3, 8),
        random.randint(1, 2)
    ]

def safe_add(stdscr, y, x, ch):
    try:
        stdscr.addch(y, x, ch)
    except curses.error:
        pass

def main(stdscr):
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.timeout(0)

    drops = []
    frame = 0

    while True:
        frame += 1

        key = stdscr.getch()
        if key in (ord('q'), 27):
            break

        if key == curses.KEY_RESIZE:
            stdscr.erase()

        H, W = stdscr.getmaxyx()

        if H < 3 or W < 3:
            stdscr.erase()
            safe_add(stdscr, 0, 0, 'T')
            safe_add(stdscr, 0, 1, 'O')
            safe_add(stdscr, 0, 2, 'O')
            safe_add(stdscr, 1, 0, 'S')
            safe_add(stdscr, 1, 1, 'M')
            safe_add(stdscr, 1, 2, 'A')
            safe_add(stdscr, 1, 3, 'L')
            safe_add(stdscr, 1, 4, 'L')
            stdscr.refresh()
            time.sleep(0.1)
            continue

        target = max(10, W // 3)

        while len(drops) < target:
            drops.append(create_drop(H, W))

        stdscr.erase()

        for d in drops:
            y, x, length, speed = d

            # move
            if frame % speed == 0:
                y += 1

            # reset
            if y >= H:
                y = 0
                x = random.randint(0, W - 1)
                length = random.randint(3, 8)
                speed = random.randint(1, 2)

            d[0], d[1], d[2], d[3] = y, x, length, speed

            # draw trail (fading effect)
            for i in range(length):
                ty = y - i
                if 0 <= ty < H:
                    ch = '|' if i == 0 else '.'
                    safe_add(stdscr, ty, x, ch)

        stdscr.refresh()
        time.sleep(0.03)

if __name__ == "__main__":
    curses.wrapper(main)
