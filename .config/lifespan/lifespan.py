import curses, time

def main(stdscr):
    curses.curs_set(0)
    total = 100
    for i in range(total+1):
        stdscr.clear()
        bar = int(i/total * 50)
        stdscr.addstr(0,0,f"Lifespan: [{'#'*bar}{' '*(50-bar)}] {i}%")
        stdscr.refresh()
        time.sleep(0.1)
    stdscr.getch()

curses.wrapper(main)
