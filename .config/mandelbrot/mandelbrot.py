import curses

def mandelbrot(x,y):
    c = complex(x,y)
    z = 0
    for i in range(30):
        z = z*z + c
        if abs(z) > 2:
            return i
    return 30

def main(stdscr):
    h,w = stdscr.getmaxyx()
    for y in range(h):
        for x in range(w):
            mx = (x/w)*3.5 - 2.5
            my = (y/h)*2.0 - 1.0
            val = mandelbrot(mx,my)
            ch = " .:-=+*#%@"[val//3]
            stdscr.addch(y,x,ch)
    stdscr.getch()

curses.wrapper(main)
