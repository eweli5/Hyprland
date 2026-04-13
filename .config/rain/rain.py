#!/usr/bin/env python3
import curses, random, time

def main(stdscr):
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()
    drops = []

    while True:
        stdscr.clear()
        if random.random() < 0.3:
            drops.append([0, random.randint(0,w-1)])

        for d in drops:
            stdscr.addch(d[0], d[1], '|')
            d[0] += 1

        drops = [d for d in drops if d[0] < h]
        stdscr.refresh()
        time.sleep(0.05)

curses.wrapper(main)
