#!/usr/bin/env python3
import curses
import random
import time
import math

# ── Algorithms ─────────────────────────────────────────

def bubble(a):
    for i in range(len(a)):
        for j in range(len(a)-i-1):
            yield a, j, j+1
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                yield a, j, j+1

def insertion(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            yield a, j, j+1
            a[j+1] = a[j]
            j -= 1
        a[j+1] = key
        yield a, j+1, i

def selection(a):
    for i in range(len(a)):
        m = i
        for j in range(i+1, len(a)):
            yield a, j, m
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
        yield a, i, m

def quick(a, l=0, r=None):
    if r is None: r = len(a)-1
    if l < r:
        pivot = a[r]
        i = l
        for j in range(l, r):
            yield a, j, r
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                yield a, i, j
                i += 1
        a[i], a[r] = a[r], a[i]
        yield a, i, r
        yield from quick(a, l, i-1)
        yield from quick(a, i+1, r)

def shell(a):
    gap = len(a)//2
    while gap:
        for i in range(gap, len(a)):
            j = i
            while j >= gap and a[j-gap] > a[j]:
                yield a, j, j-gap
                a[j], a[j-gap] = a[j-gap], a[j]
                j -= gap
        gap //= 2

def comb(a):
    gap = len(a)
    shrink = 1.3
    sorted_flag = False
    while not sorted_flag:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True
        i = 0
        while i + gap < len(a):
            yield a, i, i+gap
            if a[i] > a[i+gap]:
                a[i], a[i+gap] = a[i+gap], a[i]
                sorted_flag = False
            i += 1

def gnome(a):
    i = 0
    while i < len(a):
        if i == 0 or a[i] >= a[i-1]:
            i += 1
        else:
            yield a, i, i-1
            a[i], a[i-1] = a[i-1], a[i]
            i -= 1

def cocktail(a):
    start, end = 0, len(a)-1
    while start < end:
        for i in range(start, end):
            yield a, i, i+1
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
        end -= 1
        for i in range(end, start, -1):
            yield a, i, i-1
            if a[i] < a[i-1]:
                a[i], a[i-1] = a[i-1], a[i]
        start += 1

def odd_even(a):
    sorted_flag = False
    while not sorted_flag:
        sorted_flag = True
        for i in range(1, len(a)-1, 2):
            yield a, i, i+1
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                sorted_flag = False
        for i in range(0, len(a)-1, 2):
            yield a, i, i+1
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                sorted_flag = False

def bogo(a):
    while a != sorted(a):
        random.shuffle(a)
        yield a, None, None

# ── Colors (rainbow) ───────────────────────────────────

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, 8):
        curses.init_pair(i, i, -1)

def rainbow(val, max_val, offset):
    ratio = val / max_val
    index = int((ratio * 6 + offset) % 6) + 1
    return curses.color_pair(index)

# ── Draw ───────────────────────────────────────────────

def draw(stdscr, arr, i=None, j=None, name="", delay=0, frame=0):
    stdscr.erase()
    H, W = stdscr.getmaxyx()

    usable = H - 4
    max_val = max(arr)
    scale = usable / max_val if max_val else 1

    for x, val in enumerate(arr):
        height = int(val * scale)
        color = rainbow(val, max_val, frame * 0.2)

        for y in range(height):
            try:
                if x == i or x == j:
                    stdscr.addch(H-2-y, x, "█", curses.color_pair(7) | curses.A_BOLD)
                else:
                    stdscr.addch(H-2-y, x, "█", color)
            except:
                pass

    stdscr.addstr(0, 0, f"{name} | +/- speed | r reshuffle | q quit", curses.A_BOLD)
    stdscr.refresh()

# ── Main ───────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    init_colors()

    H, W = stdscr.getmaxyx()
    size = min(W-2, 140)

    algos = {
        "1": ("Bubble", bubble),
        "2": ("Insertion", insertion),
        "3": ("Selection", selection),
        "4": ("Quick", quick),
        "5": ("Shell", shell),
        "6": ("Comb", comb),
        "7": ("Gnome", gnome),
        "8": ("Cocktail", cocktail),
        "9": ("Odd-Even", odd_even),
        "0": ("Bogo (chaos)", bogo),
    }

    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, "Choose algorithm:")
        for k, (n, _) in algos.items():
            stdscr.addstr(int(k)+1, 0, f"{k}: {n}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            time.sleep(0.01)
            continue

        if key == ord('q'):
            return

        if key in map(ord, algos.keys()):
            name, algo = algos[chr(key)]
            break

    arr = list(range(1, size))
    random.shuffle(arr)

    sorter = algo(arr)
    delay = 0.01
    frame = 0

    while True:
        try:
            arr, i, j = next(sorter)
        except StopIteration:
            draw(stdscr, arr, name=name, delay=delay, frame=frame)
            stdscr.addstr(1, 0, "Sorted! r reshuffle | q quit")
            stdscr.refresh()
            break

        draw(stdscr, arr, i, j, name, delay, frame)
        frame += 1

        key = stdscr.getch()
        if key == ord('q'):
            return
        elif key == ord('r'):
            random.shuffle(arr)
            sorter = algo(arr)
        elif key == ord('+'):
            delay = max(0.001, delay - 0.002)
        elif key == ord('-'):
            delay += 0.002

        time.sleep(delay)

    while True:
        if stdscr.getch() == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
