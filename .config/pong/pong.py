import curses, time

def main(stdscr):
    curses.curs_set(0)
    h,w = stdscr.getmaxyx()
    ball = [h//2, w//2]
    vel = [1,1]
    paddle = h//2

    while True:
        stdscr.clear()
        key = stdscr.getch()
        if key == curses.KEY_UP: paddle -= 1
        if key == curses.KEY_DOWN: paddle += 1

        ball[0] += vel[0]
        ball[1] += vel[1]

        if ball[0] <= 0 or ball[0] >= h-1:
            vel[0] *= -1
        if ball[1] == w-2 and abs(ball[0]-paddle) < 2:
            vel[1] *= -1

        stdscr.addch(ball[0], ball[1], 'O')
        for i in range(-1,2):
            stdscr.addch(paddle+i, w-1, '|')

        stdscr.refresh()
        time.sleep(0.03)

curses.wrapper(main)
