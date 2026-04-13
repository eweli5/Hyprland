import curses, random, time

def main(stdscr):
    curses.curs_set(0)
    h,w = stdscr.getmaxyx()
    arr = [random.randint(1,h-1) for _ in range(w//2)]

    for i in range(len(arr)):
        for j in range(len(arr)-i-1):
            stdscr.clear()
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
            for x,v in enumerate(arr):
                for y in range(v):
                    stdscr.addch(h-y-1, x, '|')
            stdscr.refresh()
            time.sleep(0.01)

    stdscr.getch()

curses.wrapper(main)
