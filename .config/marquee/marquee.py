import curses, time

def main(stdscr):
    curses.curs_set(0)
    text = \"HELLO TERMINAL \"
    w = stdscr.getmaxyx()[1]
    pos = w

    while True:
        stdscr.clear()
        stdscr.addstr(0, pos, text)
        pos -= 1
        if pos < -len(text): pos = w
        stdscr.refresh()
        time.sleep(0.05)

curses.wrapper(main)
