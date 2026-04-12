#!/usr/bin/env python3
"""
statusboard.py — terminal service monitor
pip install requests pyyaml
python3 statusboard.py [config.yaml]
"""

import curses, threading, time, sys, os
from datetime import datetime
from collections import deque

try:
    import requests
except ImportError:
    sys.exit("missing: pip install requests")

try:
    import yaml
except ImportError:
    sys.exit("missing: pip install pyyaml")

DEFAULT_CONFIG = {
    "title": "statusboard",
    "interval": 30,
    "timeout": 8,
    "history": 20,
    "services": [
        {"name": "homepage",   "url": "https://example.com"},
        {"name": "api",        "url": "https://example.com/api/health"},
        {"name": "login",      "url": "https://example.com/login"},
    ]
}

# ── state ─────────────────────────────────────────────────────────────────────

class Svc:
    def __init__(self, name, url, hlen):
        self.name = name
        self.url  = url
        self.ok   = None
        self.code = None
        self.ms   = None
        self.err  = None
        self.when = None
        self.hist = deque(maxlen=hlen)
        self.lock = threading.Lock()

    def record(self, ok, code, ms, err=None):
        with self.lock:
            self.ok, self.code, self.ms, self.err = ok, code, ms, err
            self.when = datetime.now()
            self.hist.append(ok)

    @property
    def uptime(self):
        if not self.hist: return None
        return 100 * sum(self.hist) / len(self.hist)

# ── polling ───────────────────────────────────────────────────────────────────

def poll(svc, timeout):
    try:
        t = time.monotonic()
        r = requests.get(svc.url, timeout=timeout,
                         headers={"User-Agent": "statusboard/1.0"},
                         allow_redirects=True)
        ms = int((time.monotonic() - t) * 1000)
        svc.record(200 <= r.status_code < 400, r.status_code, ms)
    except requests.exceptions.Timeout:
        svc.record(False, None, None, "timeout")
    except requests.exceptions.ConnectionError:
        svc.record(False, None, None, "conn refused")
    except Exception as e:
        svc.record(False, None, None, str(e)[:24])

# ── colors ────────────────────────────────────────────────────────────────────

GREEN=1; RED=2; YELLOW=3; CYAN=4; DIM=5; BOLD_W=6

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(GREEN,  curses.COLOR_GREEN,  -1)
    curses.init_pair(RED,    curses.COLOR_RED,    -1)
    curses.init_pair(YELLOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(CYAN,   curses.COLOR_CYAN,   -1)
    curses.init_pair(DIM,    8,                   -1)
    curses.init_pair(BOLD_W, curses.COLOR_WHITE,  -1)

def c(pair): return curses.color_pair(pair)

# ── draw ──────────────────────────────────────────────────────────────────────

def draw(scr, svcs, cfg, nxt):
    scr.erase()
    H, W = scr.getmaxyx()
    title = cfg.get("title", "statusboard")
#    now   = datetime.now().strftime("%H:%M:%S")
    secs  = max(0, int(nxt[0] - time.monotonic()))

    try:
        scr.addstr(0, 0, "─" * W, c(CYAN))
        scr.addstr(0, 2, f" {title} ", c(CYAN) | curses.A_BOLD)
        right = f" {now} "
        scr.addstr(0, W - len(right) - 1, right, c(DIM))
    except curses.error: pass

    row = 2
    try:
        scr.addstr(row, 2,  "name",    c(DIM))
        scr.addstr(row, 26, "status",  c(DIM))
        scr.addstr(row, 35, "code",    c(DIM))
        scr.addstr(row, 41, "latency", c(DIM))
        scr.addstr(row, 51, "uptime",  c(DIM))
        scr.addstr(row, 59, "history", c(DIM))
        scr.addstr(row + 1, 0, "─" * min(W, 90), c(DIM))
    except curses.error: pass

    row = 4
    for svc in svcs:
        if row >= H - 3: break
        with svc.lock:
            ok, code, ms, err = svc.ok, svc.code, svc.ms, svc.err
            up   = svc.uptime
            hist = list(svc.hist)

        if ok is None:  dot, dcol = "?", YELLOW
        elif ok:        dot, dcol = "●", GREEN
        else:           dot, dcol = "●", RED

        try:
            scr.addch(row, 1, dot, c(dcol))
            scr.addstr(row, 3, f"{svc.name[:20]:<22}", c(BOLD_W))

            if ok is None:  scr.addstr(row, 26, f"{'pending':<8}", c(YELLOW))
            elif ok:        scr.addstr(row, 26, f"{'up':<8}",      c(GREEN))
            else:           scr.addstr(row, 26, f"{'DOWN':<8}",    c(RED) | curses.A_BOLD)

            if code:
                scr.addstr(row, 35, f"{code:<5}", c(GREEN if 200 <= code < 400 else RED))
            else:
                scr.addstr(row, 35, f"{'─':<5}", c(DIM))

            if ms is not None:
                lcol = GREEN if ms < 300 else (YELLOW if ms < 800 else RED)
                scr.addstr(row, 41, f"{ms}ms".ljust(9), c(lcol))
            elif err:
                scr.addstr(row, 41, f"{err[:9]:<9}", c(RED))
            else:
                scr.addstr(row, 41, "─        ", c(DIM))

            if up is not None:
                ucol = GREEN if up >= 90 else (YELLOW if up >= 50 else RED)
                scr.addstr(row, 51, f"{up:.0f}%".ljust(7), c(ucol))
            else:
                scr.addstr(row, 51, "─      ", c(DIM))

            for i, h in enumerate(hist[-20:]):
                scr.addch(row, 59 + i, "▪" if h else "╌",
                          c(GREEN) if h else c(RED))

        except curses.error: pass
        row += 1

    try:
        scr.addstr(H - 2, 0, "─" * W, c(CYAN))
        scr.addstr(H - 1, 0, f"  q quit   r refresh   next check: {secs}s", c(DIM))
    except curses.error: pass

    scr.refresh()

# ── main ──────────────────────────────────────────────────────────────────────

def load_cfg(path):
    if path and os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f)
 default = os.path.expanduser("~/.config/statusboard/config.yaml")
    if os.path.exists(default):
        with open(default) as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG

def main(scr):
    cfg  = load_cfg(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
    svcs = [Svc(s["name"], s["url"], cfg.get("history", 20))
            for s in cfg["services"]]
    ivl  = cfg.get("interval", 30)
    tout = cfg.get("timeout",  8)

    curses.curs_set(0)
    scr.nodelay(True)
    scr.timeout(500)
    init_colors()

    stop = threading.Event()
    nxt  = [time.monotonic() + ivl]

    def run_poller():
        while not stop.is_set():
            ts = [threading.Thread(target=poll, args=(s, tout), daemon=True) for s in svcs]
            for t in ts: t.start()
            for t in ts: t.join()
            nxt[0] = time.monotonic() + ivl
            stop.wait(ivl)

    threading.Thread(target=run_poller, daemon=True).start()

    while True:
        draw(scr, svcs, cfg, nxt)
        key = scr.getch()
        if key in (ord('q'), ord('Q'), 27):
            break
        if key in (ord('r'), ord('R')):
            for s in svcs:
                threading.Thread(target=poll, args=(s, tout), daemon=True).start()
            nxt[0] = time.monotonic() + ivl

    stop.set()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
