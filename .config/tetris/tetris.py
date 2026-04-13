import curses, time

def main(stdscr):
    curses.curs_set(0)
    h,w = stdscr.getmaxyx()
    x = w//2
    y = 0

    while True:
        stdscr.clear()
        stdscr.addch(y,x,'#')
        y += 1
        if y >= h-1:
            y = 0
        stdscr.refresh()
        time.sleep(0.05)

curses.wrapper(main)
