import curses, random, time

chars = " .:-=+*#%@"

def main(stdscr):
    curses.curs_set(0)
    h,w = stdscr.getmaxyx()

    while True:
        stdscr.clear()
        for y in range(h):
            for x in range(w):
                v = random.random()
                stdscr.addch(y,x,chars[int(v*len(chars))])
        stdscr.refresh()
        time.sleep(0.05)

curses.wrapper(main)
