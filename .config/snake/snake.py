import curses, random

def main(stdscr):
    curses.curs_set(0)
    h,w = stdscr.getmaxyx()
    snake = [[h//2, w//2]]
    food = [random.randint(1,h-2), random.randint(1,w-2)]
    d = [0,1]

    while True:
        stdscr.clear()
        key = stdscr.getch()
        if key == curses.KEY_UP: d=[-1,0]
        if key == curses.KEY_DOWN: d=[1,0]
        if key == curses.KEY_LEFT: d=[0,-1]
        if key == curses.KEY_RIGHT: d=[0,1]

        head = [snake[0][0]+d[0], snake[0][1]+d[1]]
        snake.insert(0, head)

        if head == food:
            food = [random.randint(1,h-2), random.randint(1,w-2)]
        else:
            snake.pop()

        stdscr.addch(food[0], food[1], '*')
        for s in snake:
            stdscr.addch(s[0], s[1], '#')

        stdscr.refresh()

curses.wrapper(main)
