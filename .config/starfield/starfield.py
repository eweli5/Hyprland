import curses, random, time

def main(stdscr):
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()
    stars = [[random.randint(0,h-1), random.randint(0,w-1)] for _ in range(120)]

    while True:
        stdscr.clear()
        for s in stars:
            stdscr.addch(s[0], s[1], '.')
            s[1] -= 1
            if s[1] < 0:
                s[0] = random.randint(0,h-1)
                s[1] = w-1
        stdscr.refresh()
        time.sleep(0.03)

curses.wrapper(main)
