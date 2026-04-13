#!/usr/bin/env python3
import curses, random, time

chars = " .:-=+*#%@"

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.erase()

        for y in range(h - 1):          # avoid last row
            for x in range(w - 1):      # avoid last col
                v = random.random()
                idx = int(v * (len(chars) - 1))  # FIX index
                try:
                    stdscr.addch(y, x, chars[idx])
                except curses.error:
                    pass  # ignore edge glitches

        stdscr.refresh()
        time.sleep(0.05)

curses.wrapper(main)
