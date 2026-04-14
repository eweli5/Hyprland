#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║           ABYSSAL DEPTHS — Terminal Dungeon Crawler      ║
║         Infinite generation · Items · Accounts · RPG     ║
╚══════════════════════════════════════════════════════════╝
"""

import curses
import json
import os
import random
import hashlib
import time
import math
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

# ──────────────────────────────────────────────────────────
# SAVE / DATA PATHS
# ──────────────────────────────────────────────────────────
SAVE_DIR = Path.home() / ".abyssal_depths"
SAVE_DIR.mkdir(exist_ok=True)
ACCOUNTS_FILE = SAVE_DIR / "accounts.json"
SCORES_FILE   = SAVE_DIR / "scores.json"

# ──────────────────────────────────────────────────────────
# COLOURS  (pair index → description)
# ──────────────────────────────────────────────────────────
C_WALL    = 1
C_FLOOR   = 2
C_PLAYER  = 3
C_ENEMY   = 4
C_ITEM    = 5
C_STAIRS  = 6
C_UI_BOX  = 7
C_TITLE   = 8
C_GOLD    = 9
C_RED     = 10
C_GREEN   = 11
C_CYAN    = 12
C_MAGENTA = 13
C_WHITE   = 14
C_DARK    = 15
C_FIRE    = 16
C_ICE     = 17
C_POISON  = 18
C_HOLY    = 19

# ──────────────────────────────────────────────────────────
# DATA: ITEMS
# ──────────────────────────────────────────────────────────
ITEM_DB = {
    # Weapons
    "rusty_dagger":    {"name": "Rusty Dagger",    "type": "weapon", "glyph": "†", "atk": 2,  "val": 5,   "rarity": "common",    "desc": "A corroded blade."},
    "shortsword":      {"name": "Shortsword",      "type": "weapon", "glyph": "†", "atk": 5,  "val": 20,  "rarity": "common",    "desc": "A reliable blade."},
    "longsword":       {"name": "Longsword",       "type": "weapon", "glyph": "†", "atk": 9,  "val": 60,  "rarity": "uncommon",  "desc": "Well-balanced steel."},
    "greataxe":        {"name": "Greataxe",        "type": "weapon", "glyph": "†", "atk": 14, "val": 120, "rarity": "rare",      "desc": "Heavy but devastating."},
    "shadow_blade":    {"name": "Shadow Blade",    "type": "weapon", "glyph": "†", "atk": 18, "val": 300, "rarity": "epic",      "desc": "Drinks the light itself.", "bonus": "crit+15"},
    "soul_reaper":     {"name": "Soul Reaper",     "type": "weapon", "glyph": "†", "atk": 25, "val": 800, "rarity": "legendary", "desc": "Harvests essence of the dead.", "bonus": "lifesteal+10"},
    "void_shard":      {"name": "Void Shard",      "type": "weapon", "glyph": "†", "atk": 35, "val": 2000,"rarity": "mythic",    "desc": "A splinter of un-creation.", "bonus": "crit+25"},
    # Armour
    "leather_tunic":   {"name": "Leather Tunic",   "type": "armour", "glyph": "[", "def": 2,  "val": 10,  "rarity": "common",    "desc": "Basic protection."},
    "chainmail":       {"name": "Chainmail",        "type": "armour", "glyph": "[", "def": 5,  "val": 50,  "rarity": "uncommon",  "desc": "Interlocked rings."},
    "plate_armour":    {"name": "Plate Armour",     "type": "armour", "glyph": "[", "def": 10, "val": 180, "rarity": "rare",      "desc": "Heavy full-body steel."},
    "dragon_scale":    {"name": "Dragon Scale",     "type": "armour", "glyph": "[", "def": 18, "val": 500, "rarity": "epic",      "desc": "Scales of the ancient wyrm.", "bonus": "fire_resist"},
    "void_plate":      {"name": "Void Plate",       "type": "armour", "glyph": "[", "def": 28, "val": 1500,"rarity": "mythic",    "desc": "Armour of the outer dark.", "bonus": "regen+2"},
    # Potions
    "health_potion":   {"name": "Health Potion",   "type": "potion", "glyph": "!", "hp": 25,  "val": 15,  "rarity": "common",    "desc": "Restores 25 HP."},
    "big_health":      {"name": "Big Health Pot",  "type": "potion", "glyph": "!", "hp": 60,  "val": 40,  "rarity": "uncommon",  "desc": "Restores 60 HP."},
    "elixir":          {"name": "Elixir of Life",  "type": "potion", "glyph": "!", "hp": 150, "val": 120, "rarity": "rare",      "desc": "Restores 150 HP.", "bonus": "max_hp+10"},
    "str_potion":      {"name": "Strength Brew",   "type": "potion", "glyph": "!", "atk": 3,  "val": 80,  "rarity": "rare",      "desc": "+3 ATK permanently."},
    "def_potion":      {"name": "Iron Skin Brew",  "type": "potion", "glyph": "!", "def_up": 2,"val": 70, "rarity": "rare",      "desc": "+2 DEF permanently."},
    "xp_tonic":        {"name": "XP Tonic",        "type": "potion", "glyph": "!", "xp": 200, "val": 200, "rarity": "epic",      "desc": "Grants 200 XP."},
    # Accessories
    "lucky_ring":      {"name": "Lucky Ring",      "type": "accessory","glyph":"=","val": 90,  "rarity": "uncommon",  "desc": "Luck +5.", "bonus": "luck+5"},
    "power_amulet":    {"name": "Power Amulet",    "type": "accessory","glyph":"=","val": 200, "rarity": "rare",      "desc": "ATK +4, DEF +2.", "bonus": "atk+4,def+2"},
    "vampiric_ring":   {"name": "Vampiric Ring",   "type": "accessory","glyph":"=","val": 400, "rarity": "epic",      "desc": "Lifesteal +8%.", "bonus": "lifesteal+8"},
    "philosophers_stone":{"name":"Philosopher's Stone","type":"accessory","glyph":"=","val":2000,"rarity":"mythic","desc":"All stats +5.","bonus":"all+5"},
    # Gold piles
    "gold_pile":       {"name": "Gold Pile",       "type": "gold",   "glyph": "$", "gold": 30, "val": 30,  "rarity": "common",    "desc": "Shiny coins."},
    "gold_hoard":      {"name": "Gold Hoard",      "type": "gold",   "glyph": "$", "gold": 120,"val": 120, "rarity": "uncommon",  "desc": "A sizeable stash."},
}

RARITY_COLOUR = {
    "common":    C_WHITE,
    "uncommon":  C_GREEN,
    "rare":      C_CYAN,
    "epic":      C_MAGENTA,
    "legendary": C_GOLD,
    "mythic":    C_FIRE,
}

RARITY_WEIGHT = {
    "common": 55, "uncommon": 25, "rare": 12, "epic": 5, "legendary": 2, "mythic": 1
}

# ──────────────────────────────────────────────────────────
# DATA: ENEMIES
# ──────────────────────────────────────────────────────────
ENEMY_DB = {
    "rat":        {"name":"Giant Rat",      "glyph":"r","hp":8,  "atk":3, "def":0,"xp":10,"gold":2, "colour":C_DARK,   "floor_min":1},
    "goblin":     {"name":"Goblin",         "glyph":"g","hp":14, "atk":5, "def":1,"xp":20,"gold":5, "colour":C_GREEN,  "floor_min":1},
    "skeleton":   {"name":"Skeleton",       "glyph":"s","hp":18, "atk":6, "def":2,"xp":30,"gold":8, "colour":C_WHITE,  "floor_min":2},
    "zombie":     {"name":"Zombie",         "glyph":"z","hp":28, "atk":7, "def":2,"xp":35,"gold":6, "colour":C_DARK,   "floor_min":2},
    "orc":        {"name":"Orc Warrior",    "glyph":"o","hp":40, "atk":10,"def":4,"xp":60,"gold":15,"colour":C_GREEN,  "floor_min":3},
    "spider":     {"name":"Cave Spider",    "glyph":"S","hp":22, "atk":9, "def":3,"xp":45,"gold":10,"colour":C_POISON, "floor_min":3, "poison":True},
    "troll":      {"name":"Stone Troll",    "glyph":"T","hp":80, "atk":14,"def":6,"xp":120,"gold":30,"colour":C_CYAN, "floor_min":5},
    "wraith":     {"name":"Wraith",         "glyph":"W","hp":55, "atk":16,"def":5,"xp":150,"gold":25,"colour":C_ICE,   "floor_min":6},
    "demon":      {"name":"Demon",          "glyph":"D","hp":100,"atk":20,"def":8,"xp":250,"gold":60,"colour":C_FIRE,  "floor_min":8},
    "lich":       {"name":"Lich",           "glyph":"L","hp":130,"atk":24,"def":10,"xp":400,"gold":100,"colour":C_MAGENTA,"floor_min":10},
    "dragon":     {"name":"Dragon",         "glyph":"d","hp":300,"atk":35,"def":18,"xp":1000,"gold":500,"colour":C_FIRE,"floor_min":15},
    "void_titan": {"name":"Void Titan",     "glyph":"V","hp":500,"atk":50,"def":25,"xp":3000,"gold":1000,"colour":C_DARK,"floor_min":20},
}

# ──────────────────────────────────────────────────────────
# XP TABLE
# ──────────────────────────────────────────────────────────
def xp_for_level(lvl: int) -> int:
    return int(100 * (lvl ** 1.5))

# ──────────────────────────────────────────────────────────
# DATACLASSES
# ──────────────────────────────────────────────────────────
@dataclass
class Item:
    key: str
    x: int = 0
    y: int = 0

    def data(self):
        return ITEM_DB[self.key]

@dataclass
class Enemy:
    key: str
    x: int
    y: int
    hp: int = 0
    max_hp: int = 0
    status: str = ""          # poison / burn / freeze
    status_turns: int = 0

    def __post_init__(self):
        if self.hp == 0:
            self.hp = self.max_hp = ENEMY_DB[self.key]["hp"]

    def data(self):
        return ENEMY_DB[self.key]

@dataclass
class Player:
    name: str = "Hero"
    hp: int = 100
    max_hp: int = 100
    atk: int = 5
    def_: int = 2
    level: int = 1
    xp: int = 0
    gold: int = 0
    floor: int = 1
    kills: int = 0
    steps: int = 0
    luck: int = 0
    crit_chance: int = 5      # %
    lifesteal: int = 0        # %
    regen: int = 0            # HP per turn
    inventory: list = field(default_factory=list)   # list of item keys (max 10)
    equipped_weapon: str = ""
    equipped_armour: str = ""
    equipped_accessory: str = ""
    status: str = ""
    status_turns: int = 0
    deepest_floor: int = 1
    total_gold_earned: int = 0

    def effective_atk(self):
        bonus = 0
        if self.equipped_weapon and self.equipped_weapon in ITEM_DB:
            bonus += ITEM_DB[self.equipped_weapon].get("atk", 0)
        return self.atk + bonus

    def effective_def(self):
        bonus = 0
        if self.equipped_armour and self.equipped_armour in ITEM_DB:
            bonus += ITEM_DB[self.equipped_armour].get("def", 0)
        return self.def_

    def xp_needed(self):
        return xp_for_level(self.level + 1)

    def is_alive(self):
        return self.hp > 0

# ──────────────────────────────────────────────────────────
# DUNGEON GENERATOR  (BSP rooms + corridors)
# ──────────────────────────────────────────────────────────
TILE_WALL  = "#"
TILE_FLOOR = "."
TILE_STAIR = ">"
TILE_DOOR  = "+"

class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)
    def overlaps(self, other, margin=2):
        return (self.x - margin < other.x + other.w and
                self.x + self.w + margin > other.x and
                self.y - margin < other.y + other.h and
                self.y + self.h + margin > other.y)

def generate_dungeon(width: int, height: int, floor_num: int, seed: int):
    rng = random.Random(seed)
    grid = [[TILE_WALL] * width for _ in range(height)]

    # Carve rooms
    rooms: list[Room] = []
    num_rooms = rng.randint(8, 16)
    for _ in range(200):
        if len(rooms) >= num_rooms:
            break
        w = rng.randint(5, 14)
        h = rng.randint(4, 10)
        x = rng.randint(1, width  - w - 2)
        y = rng.randint(1, height - h - 2)
        r = Room(x, y, w, h)
        if any(r.overlaps(other) for other in rooms):
            continue
        rooms.append(r)
        for ry in range(r.y, r.y + r.h):
            for rx in range(r.x, r.x + r.w):
                grid[ry][rx] = TILE_FLOOR

    # Connect rooms with L-shaped corridors
    rng.shuffle(rooms)
    for i in range(len(rooms) - 1):
        (x1, y1) = rooms[i].center()
        (x2, y2) = rooms[i + 1].center()
        if rng.random() < 0.5:
            for cx in range(min(x1,x2), max(x1,x2)+1): grid[y1][cx] = TILE_FLOOR
            for cy in range(min(y1,y2), max(y1,y2)+1): grid[cy][x2] = TILE_FLOOR
        else:
            for cy in range(min(y1,y2), max(y1,y2)+1): grid[cy][x1] = TILE_FLOOR
            for cx in range(min(x1,x2), max(x1,x2)+1): grid[y2][cx] = TILE_FLOOR

    # Place stairs in last room
    sx, sy = rooms[-1].center()
    grid[sy][sx] = TILE_STAIR

    # Collect floor tiles
    floor_tiles = [(rx, ry) for ry in range(height) for rx in range(width) if grid[ry][rx] == TILE_FLOOR]

    # Spawn enemies
    enemies: list[Enemy] = []
    eligible = [k for k, v in ENEMY_DB.items() if v["floor_min"] <= floor_num]
    if not eligible:
        eligible = ["rat"]
    enemy_count = rng.randint(4, 8 + floor_num // 2)
    used_tiles = {(sx, sy)}
    for _ in range(enemy_count):
        if not floor_tiles:
            break
        t = rng.choice(floor_tiles)
        if t in used_tiles:
            continue
        used_tiles.add(t)
        key = rng.choices(eligible, weights=[1/(1+abs(v["floor_min"]-floor_num)) for k,v in ENEMY_DB.items() if k in eligible])[0]
        e = Enemy(key=key, x=t[0], y=t[1])
        enemies.append(e)

    # Spawn items
    items: list[Item] = []
    item_keys = list(ITEM_DB.keys())
    item_weights = [RARITY_WEIGHT[ITEM_DB[k]["rarity"]] for k in item_keys]
    item_count = rng.randint(3, 6)
    for _ in range(item_count):
        if not floor_tiles:
            break
        t = rng.choice(floor_tiles)
        if t in used_tiles:
            continue
        used_tiles.add(t)
        chosen = rng.choices(item_keys, weights=item_weights)[0]
        items.append(Item(key=chosen, x=t[0], y=t[1]))

    # Player start: first room center
    px, py = rooms[0].center()

    return grid, rooms, enemies, items, px, py

# ──────────────────────────────────────────────────────────
# ACCOUNT MANAGEMENT
# ──────────────────────────────────────────────────────────
def load_accounts() -> dict:
    if ACCOUNTS_FILE.exists():
        try:
            return json.loads(ACCOUNTS_FILE.read_text())
        except Exception:
            pass
    return {}

def save_accounts(data: dict):
    ACCOUNTS_FILE.write_text(json.dumps(data, indent=2))

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def load_scores() -> list:
    if SCORES_FILE.exists():
        try:
            return json.loads(SCORES_FILE.read_text())
        except Exception:
            pass
    return []

def save_score(username: str, player: Player):
    scores = load_scores()
    scores.append({
        "username": username,
        "name": player.name,
        "floor": player.deepest_floor,
        "kills": player.kills,
        "gold": player.total_gold_earned,
        "level": player.level,
        "date": time.strftime("%Y-%m-%d"),
    })
    scores.sort(key=lambda s: (s["floor"], s["level"], s["gold"]), reverse=True)
    SCORES_FILE.write_text(json.dumps(scores[:50], indent=2))

# ──────────────────────────────────────────────────────────
# COMBAT
# ──────────────────────────────────────────────────────────
def player_attack(player: Player, enemy: Enemy, rng: random.Random) -> tuple[int, bool, bool]:
    """Returns (damage, is_crit, is_kill)"""
    crit = rng.randint(1, 100) <= (player.crit_chance + player.luck // 2)
    raw = player.effective_atk()
    dmg = max(1, raw - enemy.data()["def"] + rng.randint(-1, 2))
    if crit:
        dmg = int(dmg * 1.8)
    enemy.hp -= dmg
    # lifesteal
    if player.lifesteal > 0:
        heal = max(1, int(dmg * player.lifesteal / 100))
        player.hp = min(player.max_hp, player.hp + heal)
    # apply weapon bonus status
    w = player.equipped_weapon
    if w and "shadow_blade" in w:
        if rng.random() < 0.15:
            enemy.status = "poison"
            enemy.status_turns = 3
    if w and "soul_reaper" in w:
        if rng.random() < 0.1:
            enemy.status = "burn"
            enemy.status_turns = 3
    killed = enemy.hp <= 0
    return dmg, crit, killed

def enemy_attack(enemy: Enemy, player: Player, rng: random.Random) -> int:
    edata = enemy.data()
    raw = edata["atk"]
    dmg = max(1, raw - player.effective_def() + rng.randint(-1, 2))
    # Enemy status effects
    if edata.get("poison") and rng.random() < 0.25:
        player.status = "poison"
        player.status_turns = 4
    player.hp -= dmg
    return dmg

def tick_status(entity, rng: random.Random) -> int:
    """Applies status effect, returns damage dealt. Clears if expired."""
    dmg = 0
    if entity.status and entity.status_turns > 0:
        if entity.status == "poison":
            dmg = rng.randint(2, 5)
            entity.hp -= dmg
        elif entity.status == "burn":
            dmg = rng.randint(3, 8)
            entity.hp -= dmg
        entity.status_turns -= 1
        if entity.status_turns <= 0:
            entity.status = ""
    return dmg

# ──────────────────────────────────────────────────────────
# GAME STATE
# ──────────────────────────────────────────────────────────
class Game:
    def __init__(self, stdscr, username: str, player: Player):
        self.stdscr = stdscr
        self.username = username
        self.player = player
        self.rng = random.Random()
        self.messages: list[str] = []
        self.max_messages = 8

        # Map dimensions (safe area within terminal)
        self.map_h = 26
        self.map_w = 70
        self.map_x = 0        # map panel left x
        self.map_y = 2        # map panel top y (row 0-1 is title bar)

        self._init_floor()
        self.run()

    # ── floor init ──
    def _init_floor(self):
        seed = int(time.time() * 1000) ^ (self.player.floor * 7919)
        self.grid, self.rooms, self.enemies, self.items, px, py = generate_dungeon(
            self.map_w, self.map_h, self.player.floor, seed)
        self.player_x = px
        self.player_y = py
        self.camera_x = 0
        self.camera_y = 0
        self.level_up_pending = False
        self.in_inventory = False
        self.log(f"~~ Floor {self.player.floor} ~~  Descend deeper…")

    # ── logging ──
    def log(self, msg: str, colour: int = C_WHITE):
        self.messages.append((msg, colour))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    # ── curses helpers ──
    def addstr_safe(self, y, x, text, attr=0):
        try:
            h, w = self.stdscr.getmaxyx()
            if 0 <= y < h and 0 <= x < w:
                max_len = w - x
                self.stdscr.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    def hline_safe(self, y, x, ch, n):
        try:
            h, w = self.stdscr.getmaxyx()
            n = min(n, w - x)
            if 0 <= y < h and n > 0:
                self.stdscr.hline(y, x, ch, n)
        except curses.error:
            pass

    # ── main loop ──
    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)

        while True:
            self.draw()
            if self.level_up_pending:
                self.do_level_up()
                continue

            key = self.stdscr.getch()

            if self.in_inventory:
                result = self.handle_inventory_input(key)
                if result == "quit_inventory":
                    self.in_inventory = False
                continue

            # Movement
            dx, dy = 0, 0
            if   key in (curses.KEY_UP,    ord('w'), ord('k')): dy = -1
            elif key in (curses.KEY_DOWN,  ord('s'), ord('j')): dy =  1
            elif key in (curses.KEY_LEFT,  ord('a'), ord('h')): dx = -1
            elif key in (curses.KEY_RIGHT, ord('d'), ord('l')): dx =  1
            elif key in (ord('i'), ord('I')): self.in_inventory = True; continue
            elif key in (ord('q'), ord('Q')): self.quit_game(); return
            elif key == ord('?'): self.show_help(); continue
            elif key == ord('H'): self.show_highscores(); continue
            elif key == ord('.'): self.wait_turn(); continue
            else: continue

            if dx != 0 or dy != 0:
                self.try_move(dx, dy)

            if not self.player.is_alive():
                self.game_over()
                return

    # ── movement / interaction ──
    def try_move(self, dx, dy):
        nx = self.player_x + dx
        ny = self.player_y + dy
        p = self.player

        if not (0 <= nx < self.map_w and 0 <= ny < self.map_h):
            return
        tile = self.grid[ny][nx]
        if tile == TILE_WALL:
            return

        # Attack enemy?
        target = self._enemy_at(nx, ny)
        if target:
            dmg, crit, killed = player_attack(p, target, self.rng)
            crit_str = " ★CRIT★" if crit else ""
            self.log(f"You hit {target.data()['name']} for {dmg} dmg.{crit_str}", C_GOLD if crit else C_WHITE)
            if killed:
                edata = target.data()
                p.xp += edata["xp"]
                gold_gain = self.rng.randint(edata["gold"]//2, edata["gold"])
                p.gold += gold_gain
                p.total_gold_earned += gold_gain
                p.kills += 1
                self.enemies.remove(target)
                self.log(f"{target.data()['name']} slain!  +{edata['xp']}xp  +{gold_gain}g", C_GOLD)
                self._check_level_up()
            else:
                # Enemy counter-attacks
                enemy_dmg = enemy_attack(target, p, self.rng)
                self.log(f"{target.data()['name']} hits you for {enemy_dmg}.", C_RED)
            self._end_of_turn()
            return

        # Move
        self.player_x = nx
        self.player_y = ny
        p.steps += 1

        # Pick up item?
        item = self._item_at(nx, ny)
        if item:
            self._pick_up_item(item)

        # Stairs?
        if tile == TILE_STAIR:
            self.descend()
            return

        self._end_of_turn()

    def _end_of_turn(self):
        p = self.player
        # Status ticks
        if p.status:
            dmg = tick_status(p, self.rng)
            if dmg > 0:
                self.log(f"You take {dmg} {p.status} damage!", C_POISON if p.status=="poison" else C_FIRE)
        # Regen
        if p.regen > 0 and p.hp < p.max_hp:
            p.hp = min(p.max_hp, p.hp + p.regen)
        # Enemy turns
        for e in list(self.enemies):
            # Status tick
            if e.status:
                tick_status(e, self.rng)
                if e.hp <= 0:
                    edata = e.data()
                    p.xp += edata["xp"] // 2
                    p.kills += 1
                    self.enemies.remove(e)
                    self.log(f"{edata['name']} dies from {e.status}!", C_POISON)
                    continue
            # Enemy moves toward player
            self._enemy_ai(e)

    def _enemy_ai(self, e: Enemy):
        p = self.player
        dist = abs(e.x - p.x if hasattr(p,'x') else self.player_x - e.x) + abs(e.y - p.y if hasattr(p,'y') else self.player_y - e.y)
        dx = self.player_x - e.x
        dy = self.player_y - e.y
        dist = abs(dx) + abs(dy)

        if dist > 10:
            # Wander randomly
            if self.rng.random() < 0.3:
                rdx, rdy = self.rng.choice([(1,0),(-1,0),(0,1),(0,-1)])
                nx2, ny2 = e.x + rdx, e.y + rdy
                if 0 <= nx2 < self.map_w and 0 <= ny2 < self.map_h and self.grid[ny2][nx2] != TILE_WALL:
                    if not self._enemy_at(nx2, ny2):
                        e.x, e.y = nx2, ny2
            return

        if dist == 1:
            # Attack
            edamage = enemy_attack(e, p, self.rng)
            self.log(f"{e.data()['name']} strikes you for {edamage}!", C_RED)
            return

        # Move toward player
        step_x = (1 if dx > 0 else -1) if dx != 0 else 0
        step_y = (1 if dy > 0 else -1) if dy != 0 else 0
        # Try x first then y
        moved = False
        for sx, sy in [(step_x, 0), (0, step_y), (step_x, step_y)]:
            nx2, ny2 = e.x + sx, e.y + sy
            if (0 <= nx2 < self.map_w and 0 <= ny2 < self.map_h
                    and self.grid[ny2][nx2] != TILE_WALL
                    and not self._enemy_at(nx2, ny2)
                    and not (nx2 == self.player_x and ny2 == self.player_y)):
                e.x, e.y = nx2, ny2
                moved = True
                break

    def _enemy_at(self, x, y) -> Optional[Enemy]:
        for e in self.enemies:
            if e.x == x and e.y == y:
                return e
        return None

    def _item_at(self, x, y) -> Optional[Item]:
        for it in self.items:
            if it.x == x and it.y == y:
                return it
        return None

    def _pick_up_item(self, item: Item):
        p = self.player
        data = item.data()
        self.items.remove(item)

        if data["type"] == "gold":
            g = data["gold"]
            p.gold += g
            p.total_gold_earned += g
            self.log(f"Picked up {data['name']}! (+{g}g)", C_GOLD)
            return

        if data["type"] == "potion":
            # Auto-use
            if "hp" in data:
                heal = data["hp"]
                p.hp = min(p.max_hp, p.hp + heal)
                self.log(f"Used {data['name']}! (+{heal} HP)", C_GREEN)
            if "atk" in data:
                p.atk += data["atk"]
                self.log(f"Used {data['name']}! (+{data['atk']} ATK)", C_GREEN)
            if "def_up" in data:
                p.def_ += data["def_up"]
                self.log(f"Used {data['name']}! (+{data['def_up']} DEF)", C_GREEN)
            if "xp" in data:
                p.xp += data["xp"]
                self.log(f"Used {data['name']}! (+{data['xp']} XP)", C_CYAN)
                self._check_level_up()
            if "max_hp" in data.get("bonus",""):
                p.max_hp += 10; p.hp = min(p.max_hp, p.hp + 10)
            return

        # Equipment / accessories: add to inventory
        if len(p.inventory) < 10:
            p.inventory.append(item.key)
            rarity = data["rarity"]
            col = RARITY_COLOUR.get(rarity, C_WHITE)
            self.log(f"Found [{rarity.upper()}] {data['name']}! (press i)", col)
        else:
            self.log("Inventory full! Drop something.", C_RED)
            p.inventory.append(item.key)   # force-add; UI will manage

    def _apply_accessory_bonus(self, bonus: str, sign: int = 1):
        p = self.player
        if not bonus:
            return
        for part in bonus.split(","):
            if "luck+" in part:
                p.luck += sign * int(part.split("+")[1])
            elif "atk+" in part:
                p.atk += sign * int(part.split("+")[1])
            elif "def+" in part:
                p.def_ += sign * int(part.split("+")[1])
            elif "lifesteal+" in part:
                p.lifesteal += sign * int(part.split("+")[1])
            elif "regen+" in part:
                p.regen += sign * int(part.split("+")[1])
            elif "all+" in part:
                v = sign * int(part.split("+")[1])
                p.atk += v; p.def_ += v; p.luck += v
                p.max_hp += v * 10; p.hp = min(p.max_hp, p.hp + v*10)
            elif "crit+" in part:
                p.crit_chance += sign * int(part.split("+")[1])

    def _check_level_up(self):
        p = self.player
        if p.xp >= p.xp_needed():
            p.xp -= p.xp_needed()
            p.level += 1
            self.level_up_pending = True
            self.log(f"✦ LEVEL UP! You are now level {p.level}! ✦", C_GOLD)

    def do_level_up(self):
        self.level_up_pending = False
        p = self.player
        # Stats boost
        p.max_hp += 15
        p.hp = min(p.max_hp, p.hp + 15)
        p.atk += 1
        p.def_ += 1
        if p.level % 3 == 0:
            p.crit_chance = min(50, p.crit_chance + 1)
        self.draw_level_up_screen()

    def draw_level_up_screen(self):
        s = self.stdscr
        h, w = s.getmaxyx()
        p = self.player
        s.clear()
        banner = [
            "╔══════════════════════════════╗",
            "║      ✦  LEVEL  UP  ✦         ║",
            f"║   You reached Level {p.level:>2}!     ║",
            "╠══════════════════════════════╣",
            "║  +15 Max HP                  ║",
            "║  +1 ATK                      ║",
            "║  +1 DEF                      ║",
            "║                              ║",
            "║  Press any key to continue   ║",
            "╚══════════════════════════════╝",
        ]
        sy = h // 2 - len(banner) // 2
        sx = w // 2 - 17
        for i, line in enumerate(banner):
            self.addstr_safe(sy + i, sx, line, curses.color_pair(C_GOLD) | curses.A_BOLD)
        s.refresh()
        s.getch()

    # ── descend floor ──
    def descend(self):
        p = self.player
        p.floor += 1
        if p.floor > p.deepest_floor:
            p.deepest_floor = p.floor
        self.log(f"You descend to floor {p.floor}…", C_CYAN)
        self._save_progress()
        self._init_floor()

    def wait_turn(self):
        p = self.player
        if p.hp < p.max_hp:
            p.hp = min(p.max_hp, p.hp + 3 + p.regen)
            self.log("You rest briefly. (+HP)", C_GREEN)
        self._end_of_turn()

    # ── inventory screen ──
    def handle_inventory_input(self, key):
        if key in (ord('i'), ord('I'), 27, ord('q')):
            return "quit_inventory"
        p = self.player
        idx = key - ord('a')
        if 0 <= idx < len(p.inventory):
            item_key = p.inventory[idx]
            data = ITEM_DB[item_key]
            if data["type"] == "weapon":
                if p.equipped_weapon == item_key:
                    p.equipped_weapon = ""
                    self.log(f"Unequipped {data['name']}.", C_WHITE)
                else:
                    p.equipped_weapon = item_key
                    self.log(f"Equipped {data['name']}! (+{data.get('atk',0)} ATK)", C_GREEN)
            elif data["type"] == "armour":
                if p.equipped_armour == item_key:
                    p.equipped_armour = ""
                    self.log(f"Unequipped {data['name']}.", C_WHITE)
                else:
                    p.equipped_armour = item_key
                    self.log(f"Equipped {data['name']}! (+{data.get('def',0)} DEF)", C_GREEN)
            elif data["type"] == "accessory":
                if p.equipped_accessory == item_key:
                    self._apply_accessory_bonus(data.get("bonus",""), sign=-1)
                    p.equipped_accessory = ""
                    self.log(f"Removed {data['name']}.", C_WHITE)
                else:
                    if p.equipped_accessory:
                        old = ITEM_DB.get(p.equipped_accessory, {})
                        self._apply_accessory_bonus(old.get("bonus",""), sign=-1)
                    p.equipped_accessory = item_key
                    self._apply_accessory_bonus(data.get("bonus",""), sign=1)
                    self.log(f"Equipped {data['name']}!", C_GOLD)
        elif key == ord('d'):
            self.log("Press a-j then 'd' to drop. (not yet implemented)", C_DARK)
        return None

    # ── DRAW ──
    def draw(self):
        s = self.stdscr
        s.erase()
        h, w = s.getmaxyx()
        p = self.player

        # Camera centering
        view_w = min(self.map_w, w - 22)
        view_h = min(self.map_h, h - 12)
        self.camera_x = max(0, min(self.player_x - view_w // 2, self.map_w - view_w))
        self.camera_y = max(0, min(self.player_y - view_h // 2, self.map_h - view_h))

        # ─ Title bar ─
        title = " ABYSSAL DEPTHS "
        self.addstr_safe(0, 0, "─" * min(w, 120), curses.color_pair(C_UI_BOX))
        self.addstr_safe(0, max(0, w//2 - len(title)//2), title, curses.color_pair(C_TITLE) | curses.A_BOLD)
        floor_str = f" Floor {p.floor} "
        self.addstr_safe(0, w - len(floor_str) - 1, floor_str, curses.color_pair(C_CYAN) | curses.A_BOLD)

        # ─ Map ─
        for sy in range(view_h):
            my = sy + self.camera_y
            for sx in range(view_w):
                mx = sx + self.camera_x
                if mx == self.player_x and my == self.player_y:
                    attr = curses.color_pair(C_PLAYER) | curses.A_BOLD
                    self.addstr_safe(sy + 2, sx, "@", attr)
                    continue
                # enemy?
                e = self._enemy_at(mx, my)
                if e:
                    attr = curses.color_pair(e.data()["colour"]) | curses.A_BOLD
                    self.addstr_safe(sy + 2, sx, e.data()["glyph"], attr)
                    continue
                # item?
                it = self._item_at(mx, my)
                if it:
                    col = RARITY_COLOUR.get(it.data()["rarity"], C_ITEM)
                    self.addstr_safe(sy + 2, sx, it.data()["glyph"], curses.color_pair(col))
                    continue
                # tile
                tile = self.grid[my][mx]
                if tile == TILE_WALL:
                    self.addstr_safe(sy + 2, sx, "█", curses.color_pair(C_WALL))
                elif tile == TILE_FLOOR:
                    self.addstr_safe(sy + 2, sx, "·", curses.color_pair(C_FLOOR))
                elif tile == TILE_STAIR:
                    self.addstr_safe(sy + 2, sx, ">", curses.color_pair(C_STAIRS) | curses.A_BOLD)

        # ─ Right panel ─
        px2 = view_w + 1
        py2 = 2

        def panel(y, label, value, col=C_WHITE):
            self.addstr_safe(py2 + y, px2, f"{label:<9}", curses.color_pair(C_DARK))
            self.addstr_safe(py2 + y, px2 + 9, str(value), curses.color_pair(col) | curses.A_BOLD)

        self.addstr_safe(py2,   px2, f"┌─ {p.name[:10]} ─", curses.color_pair(C_UI_BOX))
        self.addstr_safe(py2+1, px2, f"  Lv.{p.level:<3} {p.xp}/{p.xp_needed()}xp", curses.color_pair(C_CYAN))

        # HP bar
        bar_w = 16
        hp_frac = p.hp / p.max_hp
        filled = int(hp_frac * bar_w)
        bar = "█" * filled + "░" * (bar_w - filled)
        hp_col = C_GREEN if hp_frac > 0.6 else (C_GOLD if hp_frac > 0.3 else C_RED)
        self.addstr_safe(py2+2, px2, f"  HP {p.hp:>4}/{p.max_hp:<4}", curses.color_pair(hp_col))
        self.addstr_safe(py2+3, px2, f"  [{bar}]", curses.color_pair(hp_col))

        # XP bar
        xp_frac = min(1.0, p.xp / p.xp_needed())
        xp_filled = int(xp_frac * bar_w)
        xp_bar = "▪" * xp_filled + "·" * (bar_w - xp_filled)
        self.addstr_safe(py2+4, px2, f"  XP [{xp_bar}]", curses.color_pair(C_CYAN))

        panel(5, "ATK", p.effective_atk(), C_RED)
        panel(6, "DEF", p.effective_def(), C_CYAN)
        panel(7, "GOLD", f"{p.gold}g", C_GOLD)
        panel(8, "KILLS", p.kills, C_RED)
        panel(9, "STEPS", p.steps, C_DARK)
        if p.crit_chance > 5:
            panel(10, "CRIT", f"{p.crit_chance}%", C_MAGENTA)
        if p.lifesteal > 0:
            panel(10, "LEECH", f"{p.lifesteal}%", C_POISON)

        # Equipped
        self.addstr_safe(py2+11, px2, "─ Equipped ─", curses.color_pair(C_UI_BOX))
        weap_name = ITEM_DB[p.equipped_weapon]["name"][:14] if p.equipped_weapon else "─ none ─"
        armo_name = ITEM_DB[p.equipped_armour]["name"][:14] if p.equipped_armour else "─ none ─"
        acc_name  = ITEM_DB[p.equipped_accessory]["name"][:14] if p.equipped_accessory else "─ none ─"
        self.addstr_safe(py2+12, px2, f"W:{weap_name}", curses.color_pair(C_RED))
        self.addstr_safe(py2+13, px2, f"A:{armo_name}", curses.color_pair(C_CYAN))
        self.addstr_safe(py2+14, px2, f"R:{acc_name}",  curses.color_pair(C_GOLD))

        # Status effect
        if p.status:
            status_col = C_POISON if p.status == "poison" else C_FIRE
            self.addstr_safe(py2+15, px2, f"⚠ {p.status.upper()} ({p.status_turns})", curses.color_pair(status_col) | curses.A_BLINK)

        # Controls hint
        ctrl_y = py2 + 17
        self.addstr_safe(ctrl_y,   px2, "─ Keys ─", curses.color_pair(C_UI_BOX))
        self.addstr_safe(ctrl_y+1, px2, "wasd/arrows move", curses.color_pair(C_DARK))
        self.addstr_safe(ctrl_y+2, px2, "i  inventory", curses.color_pair(C_DARK))
        self.addstr_safe(ctrl_y+3, px2, ".  wait/rest", curses.color_pair(C_DARK))
        self.addstr_safe(ctrl_y+4, px2, "H  highscores", curses.color_pair(C_DARK))
        self.addstr_safe(ctrl_y+5, px2, "?  help", curses.color_pair(C_DARK))
        self.addstr_safe(ctrl_y+6, px2, "q  quit+save", curses.color_pair(C_DARK))

        # ─ Inventory popup ─
        if self.in_inventory:
            self.draw_inventory_panel()

        # ─ Message log ─
        log_y = view_h + 2 + 1
        self.addstr_safe(log_y, 0, "─" * min(w, px2 - 1), curses.color_pair(C_UI_BOX))
        for i, (msg, col) in enumerate(self.messages[-6:]):
            self.addstr_safe(log_y + 1 + i, 1, msg[:px2 - 2], curses.color_pair(col))

        s.refresh()

    def draw_inventory_panel(self):
        p = self.player
        h, w = self.stdscr.getmaxyx()
        iw = 44
        ih = 18
        ix = max(0, w // 2 - iw // 2)
        iy = max(0, h // 2 - ih // 2)

        # Draw box
        for y in range(ih):
            for x in range(iw):
                self.addstr_safe(iy + y, ix + x, " ", curses.color_pair(C_UI_BOX))
        self.addstr_safe(iy,    ix, "╔" + "═"*(iw-2) + "╗", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
        self.addstr_safe(iy+ih-1,ix,"╚" + "═"*(iw-2) + "╝", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
        for y in range(1, ih-1):
            self.addstr_safe(iy+y, ix,      "║", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
            self.addstr_safe(iy+y, ix+iw-1, "║", curses.color_pair(C_UI_BOX) | curses.A_BOLD)

        title = " INVENTORY  (a-j equip/use · i close) "
        self.addstr_safe(iy, ix + 2, title, curses.color_pair(C_TITLE) | curses.A_BOLD)

        if not p.inventory:
            self.addstr_safe(iy + 2, ix + 2, "Empty.", curses.color_pair(C_DARK))
        else:
            for idx, key in enumerate(p.inventory[:10]):
                data = ITEM_DB.get(key, {})
                label = chr(ord('a') + idx)
                equipped = key in (p.equipped_weapon, p.equipped_armour, p.equipped_accessory)
                eq_mark = "E" if equipped else " "
                rarity_col = RARITY_COLOUR.get(data.get("rarity","common"), C_WHITE)
                name = data.get("name", key)[:22]
                typ  = data.get("type","?")[:8]
                line = f" {label}) {eq_mark} {name:<22} {typ:<8}"
                self.addstr_safe(iy + 2 + idx, ix + 1, line, curses.color_pair(rarity_col) | (curses.A_BOLD if equipped else 0))

        # Stats summary
        self.addstr_safe(iy + 14, ix + 2, f"Gold: {p.gold}g   ATK:{p.effective_atk()}  DEF:{p.effective_def()}", curses.color_pair(C_GOLD))
        self.addstr_safe(iy + 15, ix + 2, f"Luck: {p.luck}  Crit: {p.crit_chance}%  Lifesteal: {p.lifesteal}%", curses.color_pair(C_CYAN))

    # ── highscores ──
    def show_highscores(self):
        s = self.stdscr
        scores = load_scores()
        s.clear()
        h, w = s.getmaxyx()
        self.addstr_safe(1, w//2 - 10, "═══ HIGH SCORES ═══", curses.color_pair(C_TITLE) | curses.A_BOLD)
        headers = f"  {'PLAYER':<14} {'CHAR':<12} {'LV':>3} {'FL':>4} {'KILLS':>6} {'GOLD':>7}  DATE"
        self.addstr_safe(3, 2, headers, curses.color_pair(C_GOLD) | curses.A_BOLD)
        self.addstr_safe(4, 2, "─" * (len(headers)+2), curses.color_pair(C_UI_BOX))
        for i, sc in enumerate(scores[:15]):
            line = f"  {sc['username']:<14} {sc['name']:<12} {sc['level']:>3} {sc['floor']:>4} {sc['kills']:>6} {sc['gold']:>7}  {sc['date']}"
            col = C_GOLD if i == 0 else (C_GREEN if i < 3 else C_WHITE)
            self.addstr_safe(5 + i, 2, line, curses.color_pair(col))
        self.addstr_safe(h-2, 2, "Press any key to return.", curses.color_pair(C_DARK))
        s.refresh()
        s.getch()

    # ── help ──
    def show_help(self):
        s = self.stdscr
        s.clear()
        lines = [
            ("╔══════════════════════════════╗", C_UI_BOX),
            ("║      ABYSSAL DEPTHS — HELP    ║", C_TITLE),
            ("╠══════════════════════════════╣", C_UI_BOX),
            ("║  MOVEMENT                    ║", C_GOLD),
            ("║  WASD / Arrow keys / hjkl    ║", C_WHITE),
            ("║                              ║", C_WHITE),
            ("║  KEYS                        ║", C_GOLD),
            ("║  i  — open inventory         ║", C_WHITE),
            ("║  .  — wait / rest (+3 HP)    ║", C_WHITE),
            ("║  H  — high scores            ║", C_WHITE),
            ("║  ?  — this help screen       ║", C_WHITE),
            ("║  q  — quit & save            ║", C_WHITE),
            ("╠══════════════════════════════╣", C_UI_BOX),
            ("║  SYMBOLS                     ║", C_GOLD),
            ("║  @  you  #  wall  ·  floor   ║", C_WHITE),
            ("║  >  stairs down              ║", C_STAIRS),
            ("║  !  potion  †  weapon        ║", C_ITEM),
            ("║  [  armour  =  accessory     ║", C_ITEM),
            ("║  $  gold                     ║", C_GOLD),
            ("╠══════════════════════════════╣", C_UI_BOX),
            ("║  Fight enemies to gain XP.   ║", C_WHITE),
            ("║  Find > to descend deeper.   ║", C_WHITE),
            ("║  Equip gear via inventory.   ║", C_WHITE),
            ("╚══════════════════════════════╝", C_UI_BOX),
            ("", C_WHITE),
            ("  Press any key…", C_DARK),
        ]
        h, w = s.getmaxyx()
        sy = max(0, h // 2 - len(lines) // 2)
        sx = max(0, w // 2 - 18)
        for i, (ln, col) in enumerate(lines):
            self.addstr_safe(sy + i, sx, ln, curses.color_pair(col) | curses.A_BOLD)
        s.refresh()
        s.getch()

    # ── save / quit ──
    def _save_progress(self):
        accounts = load_accounts()
        if self.username in accounts:
            accounts[self.username]["save"] = asdict(self.player)
            save_accounts(accounts)

    def quit_game(self):
        self._save_progress()
        save_score(self.username, self.player)
        self.draw_quit_screen()

    def draw_quit_screen(self):
        s = self.stdscr
        s.clear()
        p = self.player
        h, w = s.getmaxyx()
        msg = [
            "╔══════════════════════════╗",
            "║     GAME SAVED  ✓        ║",
            "╠══════════════════════════╣",
            f"║  Floor reached:  {p.deepest_floor:<6}  ║",
            f"║  Level:          {p.level:<6}  ║",
            f"║  Kills:          {p.kills:<6}  ║",
            f"║  Gold earned:    {p.total_gold_earned:<6}  ║",
            "╚══════════════════════════╝",
            "",
            "  See you in the Depths…",
        ]
        sy = h // 2 - len(msg) // 2
        sx = w // 2 - 15
        for i, ln in enumerate(msg):
            self.addstr_safe(sy + i, sx, ln, curses.color_pair(C_GOLD) | curses.A_BOLD)
        s.refresh()
        time.sleep(2)

    def game_over(self):
        save_score(self.username, self.player)
        s = self.stdscr
        s.clear()
        p = self.player
        h, w = s.getmaxyx()
        msg = [
            "████████████████████████████████",
            "█                              █",
            "█       YOU HAVE PERISHED      █",
            "█                              █",
            "████████████████████████████████",
            "",
            f"  Floor:  {p.deepest_floor}",
            f"  Level:  {p.level}",
            f"  Kills:  {p.kills}",
            f"  Gold:   {p.total_gold_earned}",
            "",
            "  Score saved to leaderboard.",
            "",
            "  Press any key…",
        ]
        sy = h // 2 - len(msg) // 2
        sx = w // 2 - 18
        for i, ln in enumerate(msg):
            col = C_RED if i < 5 else C_WHITE
            self.addstr_safe(sy + i, sx, ln, curses.color_pair(col) | curses.A_BOLD)
        s.refresh()
        s.getch()


# ──────────────────────────────────────────────────────────
# MAIN MENU / AUTH
# ──────────────────────────────────────────────────────────
LOGO = r"""
    ___    __________  _____ _____ ___    __       ____  ____  ____  ______  __  _______
   /   |  / __ ) __ \/ ___// ___//   |  / /      / __ \/ __ \/ __ \/_  __/ / / / / ___/
  / /| | / __  / / / \__ \ \__ \/ /| | / /      / / / / / / / /_/ / / /   / /_/ /\__ \ 
 / ___ |/ /_/ / /_/ /___/ /___/ / ___ |/ /___  / /_/ / /_/ / ____/ / /   / __  /___/ / 
/_/  |_/_____/\____//____//____/_/  |_/_____/  /_____/_____/_/     /_/   /_/ /_//____/  
"""

def draw_main_menu(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Background grid effect
    for y in range(0, h, 4):
        for x in range(0, w, 8):
            try:
                stdscr.addstr(y, x, "·", curses.color_pair(C_WALL))
            except curses.error:
                pass

    # Logo
    logo_lines = LOGO.strip("\n").split("\n")
    ly = max(1, h // 2 - len(logo_lines) // 2 - 5)
    for i, line in enumerate(logo_lines):
        lx = max(0, w // 2 - len(line) // 2)
        try:
            stdscr.addstr(ly + i, lx, line, curses.color_pair(C_TITLE) | curses.A_BOLD)
        except curses.error:
            pass

    subtitle = "∙  An Infinite Terminal Dungeon  ∙"
    sy = ly + len(logo_lines) + 1
    try:
        stdscr.addstr(sy, w // 2 - len(subtitle)//2, subtitle, curses.color_pair(C_GOLD))
    except curses.error:
        pass

    menu_items = [
        ("1", "New Game / Login"),
        ("2", "Create Account"),
        ("3", "High Scores"),
        ("4", "Quit"),
    ]
    my = sy + 3
    for key, label in menu_items:
        line = f"  [{key}]  {label}"
        mx = w // 2 - len(line) // 2
        try:
            stdscr.addstr(my, mx, f"  [{key}]", curses.color_pair(C_CYAN) | curses.A_BOLD)
            stdscr.addstr(my, mx + 5, f"  {label}", curses.color_pair(C_WHITE))
        except curses.error:
            pass
        my += 2

    version = "v2.0  |  WASD to move · i inventory · ? help · q quit"
    try:
        stdscr.addstr(h - 2, w // 2 - len(version) // 2, version, curses.color_pair(C_DARK))
    except curses.error:
        pass

    stdscr.refresh()


def input_box(stdscr, prompt: str, y: int, x: int, max_len: int = 20, secret: bool = False) -> str:
    """Simple single-line text input."""
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    try:
        stdscr.addstr(y, x, prompt + " " * (max_len + 2), curses.color_pair(C_WHITE))
        stdscr.addstr(y, x, prompt, curses.color_pair(C_GOLD) | curses.A_BOLD)
        stdscr.refresh()
        if secret:
            curses.noecho()
            result = []
            input_x = x + len(prompt)
            while True:
                ch = stdscr.getch()
                if ch in (10, 13):
                    break
                elif ch in (127, curses.KEY_BACKSPACE, 8):
                    if result:
                        result.pop()
                        stdscr.addstr(y, input_x + len(result), " ")
                        stdscr.move(y, input_x + len(result))
                        stdscr.refresh()
                elif 32 <= ch <= 126 and len(result) < max_len:
                    result.append(chr(ch))
                    stdscr.addstr(y, input_x + len(result) - 1, "*")
                    stdscr.refresh()
            curses.echo()
            curses.curs_set(0)
            return "".join(result)
        else:
            raw = stdscr.getstr(y, x + len(prompt), max_len)
            curses.noecho()
            curses.curs_set(0)
            return raw.decode("utf-8", errors="ignore").strip()
    except curses.error:
        curses.noecho()
        curses.curs_set(0)
        return ""


def show_message(stdscr, msg: str, col: int = C_RED):
    h, w = stdscr.getmaxyx()
    try:
        stdscr.addstr(h - 4, w // 2 - len(msg) // 2, " " * len(msg))
        stdscr.addstr(h - 4, w // 2 - len(msg) // 2, msg, curses.color_pair(col) | curses.A_BOLD)
    except curses.error:
        pass
    stdscr.refresh()
    time.sleep(1.5)


def auth_screen(stdscr) -> tuple[Optional[str], Optional[Player]]:
    """Login screen. Returns (username, player) or (None, None)."""
    h, w = stdscr.getmaxyx()
    cx = w // 2 - 15
    cy = h // 2 - 4

    stdscr.clear()
    stdscr.addstr(cy - 2, cx, "╔═══════════════════════════╗", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
    stdscr.addstr(cy - 1, cx, "║       LOGIN / RESUME      ║", curses.color_pair(C_TITLE) | curses.A_BOLD)
    stdscr.addstr(cy,     cx, "╚═══════════════════════════╝", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
    stdscr.refresh()

    username = input_box(stdscr, "Username: ", cy + 2, cx)
    if not username:
        return None, None
    password = input_box(stdscr, "Password: ", cy + 4, cx, secret=True)

    accounts = load_accounts()
    if username not in accounts:
        show_message(stdscr, "Account not found. Create one first.", C_RED)
        return None, None
    if accounts[username]["password"] != hash_password(password):
        show_message(stdscr, "Wrong password!", C_RED)
        return None, None

    # Load or new player
    saved = accounts[username].get("save")
    if saved:
        try:
            p = Player(**saved)
            show_message(stdscr, f"Welcome back, {p.name}! Floor {p.floor}.", C_GREEN)
            return username, p
        except Exception:
            pass

    # New char
    char_name = input_box(stdscr, "Character name: ", cy + 6, cx)
    if not char_name:
        char_name = username
    p = Player(name=char_name[:16])
    show_message(stdscr, f"Welcome, {p.name}!  Into the depths…", C_GOLD)
    return username, p


def create_account_screen(stdscr) -> bool:
    h, w = stdscr.getmaxyx()
    cx = w // 2 - 15
    cy = h // 2 - 4

    stdscr.clear()
    stdscr.addstr(cy - 2, cx, "╔═══════════════════════════╗", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
    stdscr.addstr(cy - 1, cx, "║      CREATE ACCOUNT       ║", curses.color_pair(C_TITLE) | curses.A_BOLD)
    stdscr.addstr(cy,     cx, "╚═══════════════════════════╝", curses.color_pair(C_UI_BOX) | curses.A_BOLD)
    stdscr.refresh()

    username = input_box(stdscr, "Username (max 16): ", cy + 2, cx)
    if not username or len(username) < 2:
        show_message(stdscr, "Username too short.", C_RED)
        return False
    password = input_box(stdscr, "Password:          ", cy + 4, cx, secret=True)
    if len(password) < 3:
        show_message(stdscr, "Password too short (min 3).", C_RED)
        return False

    accounts = load_accounts()
    if username in accounts:
        show_message(stdscr, "Username already taken.", C_RED)
        return False
    accounts[username] = {"password": hash_password(password), "save": None}
    save_accounts(accounts)
    show_message(stdscr, f"Account '{username}' created! You can now login.", C_GREEN)
    return True


def highscores_screen(stdscr):
    scores = load_scores()
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "═══  ABYSSAL DEPTHS — HALL OF FAME  ═══"
    stdscr.addstr(2, max(0, w//2 - len(title)//2), title, curses.color_pair(C_TITLE) | curses.A_BOLD)
    if not scores:
        stdscr.addstr(5, w//2 - 10, "No scores yet. Be the first!", curses.color_pair(C_DARK))
    else:
        header = f"  {'#':>2}  {'PLAYER':<14} {'CHAR':<12} {'LV':>3} {'FLOOR':>5} {'KILLS':>6} {'GOLD':>8}  DATE"
        stdscr.addstr(4, 3, header, curses.color_pair(C_GOLD) | curses.A_BOLD)
        stdscr.addstr(5, 3, "─" * len(header), curses.color_pair(C_UI_BOX))
        for i, sc in enumerate(scores[:20]):
            line = f"  {i+1:>2}  {sc['username']:<14} {sc['name']:<12} {sc['level']:>3} {sc['floor']:>5} {sc['kills']:>6} {sc['gold']:>8}  {sc['date']}"
            col = C_GOLD if i == 0 else (C_GREEN if i < 3 else (C_CYAN if i < 10 else C_WHITE))
            stdscr.addstr(6 + i, 3, line, curses.color_pair(col) | (curses.A_BOLD if i < 3 else 0))
    stdscr.addstr(h - 2, w//2 - 12, "Press any key to return.", curses.color_pair(C_DARK))
    stdscr.refresh()
    stdscr.getch()


# ──────────────────────────────────────────────────────────
# CURSES INIT
# ──────────────────────────────────────────────────────────
def init_colors():
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(C_WALL,    curses.COLOR_WHITE,   bg)
    curses.init_pair(C_FLOOR,   curses.COLOR_BLACK,   bg)
    curses.init_pair(C_PLAYER,  curses.COLOR_YELLOW,  bg)
    curses.init_pair(C_ENEMY,   curses.COLOR_RED,     bg)
    curses.init_pair(C_ITEM,    curses.COLOR_CYAN,    bg)
    curses.init_pair(C_STAIRS,  curses.COLOR_YELLOW,  bg)
    curses.init_pair(C_UI_BOX,  curses.COLOR_BLUE,    bg)
    curses.init_pair(C_TITLE,   curses.COLOR_MAGENTA, bg)
    curses.init_pair(C_GOLD,    curses.COLOR_YELLOW,  bg)
    curses.init_pair(C_RED,     curses.COLOR_RED,     bg)
    curses.init_pair(C_GREEN,   curses.COLOR_GREEN,   bg)
    curses.init_pair(C_CYAN,    curses.COLOR_CYAN,    bg)
    curses.init_pair(C_MAGENTA, curses.COLOR_MAGENTA, bg)
    curses.init_pair(C_WHITE,   curses.COLOR_WHITE,   bg)
    curses.init_pair(C_DARK,    curses.COLOR_BLACK,   bg)   # Note: shows as grey on most terms
    curses.init_pair(C_FIRE,    curses.COLOR_RED,     bg)
    curses.init_pair(C_ICE,     curses.COLOR_CYAN,    bg)
    curses.init_pair(C_POISON,  curses.COLOR_GREEN,   bg)
    curses.init_pair(C_HOLY,    curses.COLOR_YELLOW,  bg)


def main(stdscr):
    init_colors()
    curses.curs_set(0)

    while True:
        draw_main_menu(stdscr)
        key = stdscr.getch()

        if key == ord('1'):
            username, player = auth_screen(stdscr)
            if username and player:
                Game(stdscr, username, player)

        elif key == ord('2'):
            create_account_screen(stdscr)

        elif key == ord('3'):
            highscores_screen(stdscr)

        elif key in (ord('4'), ord('q'), 27):
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing ABYSSAL DEPTHS!")
