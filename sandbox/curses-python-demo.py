#!/usr/bin/env python3
# tui_demo_final.py
# DOS-style menu bar + dropdowns using curses, with robust geometry and clean redraws.

import curses
from curses import textpad

MENU = [
    ("&File", [
        ("&New", "NEW"),
        ("&Open…", "OPEN"),
        ("&Save", "SAVE"),
        ("Save &As…", "SAVEAS"),
        ("-", None),
        ("E&xit", "EXIT"),
    ]),
    ("&Edit", [
        ("&Undo", "UNDO"),
        ("&Redo", "REDO"),
        ("-", None),
        ("Cu&t", "CUT"),
        ("&Copy", "COPY"),
        ("&Paste", "PASTE"),
    ]),
    ("&Help", [
        ("&About", "ABOUT"),
    ]),
]

def _strip_amp(s): return s.replace("&", "")
def _hot_index(s): return s.find("&")

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # menu bar
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)    # dropdown highlight
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # normal text
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLUE)   # hotkey on bar
    curses.init_pair(5, curses.COLOR_YELLOW, -1)                  # hotkey in menu
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)   # status bar
    curses.init_pair(7, curses.COLOR_CYAN, -1)                    # accent

def draw_frame(stdscr):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Menu bar
    stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
    try: stdscr.hline(0, 0, " ", w)
    except curses.error: pass

    x = 1
    for label, _ in MENU:
        hi = _hot_index(label)
        clean = _strip_amp(label)
        for idx, ch in enumerate(clean):
            stdscr.attrset(curses.color_pair(4) | curses.A_BOLD if idx == hi else curses.color_pair(1) | curses.A_BOLD)
            if x < w:
                try: stdscr.addch(0, x, ch)
                except curses.error: pass
            x += 1
        stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
        if x + 1 < w:
            try: stdscr.addstr(0, x, "  ")
            except curses.error: pass
        x += 2

    # Status bar
    stdscr.attrset(curses.color_pair(6))
    try:
        stdscr.hline(h-1, 0, " ", w)
        stdscr.addstr(h-1, 1, "F9: Menu  F10/q: Quit  Arrows/Enter/Esc: Navigate")
    except curses.error:
        pass

    # Workspace box
    stdscr.attrset(curses.color_pair(3))
    if h >= 5 and w >= 10:
        try:
            textpad.rectangle(stdscr, 2, 1, h-3, w-2)
            stdscr.attrset(curses.color_pair(7) | curses.A_BOLD)
            stdscr.addstr(1, 2, " Demo workspace ")
        except curses.error:
            pass

    stdscr.attrset(curses.color_pair(3))
    stdscr.refresh()

def dropdown_geometry(stdscr, menu_index):
    """Top/left/width for dropdown, clipped with a 1-col right margin."""
    scr_h, scr_w = stdscr.getmaxyx()
    # X of menu label on the bar
    x = 1
    start_x = 1
    for i, (label, _) in enumerate(MENU):
        clean = _strip_amp(label)
        if i == menu_index:
            start_x = x
            break
        x += len(clean) + 2  # label + spacing

    items = MENU[menu_index][1]
    names = [_strip_amp(n) for n, _ in items]
    width = max((len(n) for n in names), default=0) + 4
    width = max(12, min(width, max(12, scr_w - 2)))  # leave 1-col outer margin

    top = 1  # under the menu bar
    left = max(1, min(start_x, scr_w - width - 1))   # keep fully on-screen

    return top, left, width

def draw_dropdown(stdscr, menu_index, sel_index):
    """Draws a clipped dropdown (no background erase)."""
    scr_h, scr_w = stdscr.getmaxyx()
    top, left, width = dropdown_geometry(stdscr, menu_index)
    items = MENU[menu_index][1]

    # Height: items + borders; leave 1 row margin at bottom
    desired = len(items) + 2
    height = max(3, min(desired, scr_h - top - 1))

    if height < 3 or width < 3 or top < 0 or left < 0:
        return None
    if top + height > scr_h or left + width > scr_w:
        return None

    win = curses.newwin(height, width, top, left)
    win.bkgd(" ", curses.color_pair(3))

    # Border (best-effort)
    try:
        textpad.rectangle(win, 0, 0, height - 1, width - 1)
    except curses.error:
        pass

    visible_rows = height - 2
    row = 1
    shown = 0

    for i, (label, _cmd) in enumerate(items):
        if shown >= visible_rows:
            break

        if label == "-":
            try:
                win.hline(row, 1, curses.ACS_HLINE, max(0, width - 2))
            except curses.error:
                pass
            row += 1
            shown += 1
            continue

        clean = _strip_amp(label)
        hoti = _hot_index(label)
        attr_line = curses.color_pair(2) | curses.A_BOLD if i == sel_index else curses.color_pair(3)

        try:
            win.attrset(attr_line)
            win.addstr(row, 1, " " * max(0, width - 2))
            for idx, ch in enumerate(clean[: max(0, width - 4)]):
                if idx == hoti:
                    win.attrset((attr_line & ~curses.A_BOLD) | curses.color_pair(5) | curses.A_BOLD)
                else:
                    win.attrset(attr_line)
                win.addch(row, 2 + idx, ch)
        except curses.error:
            pass

        row += 1
        shown += 1

    win.refresh()
    return win

def show_popup(stdscr, title, message):
    h, w = stdscr.getmaxyx()
    lines = message.splitlines() or [message]
    width = max(len(title) + 4, max((len(l) for l in lines), default=0) + 4, 24)
    width = min(width, max(24, w - 4))
    height = len(lines) + 5
    height = min(height, max(7, h - 2))
    y = max(1, (h - height) // 2)
    x = max(2, (w - width) // 2)

    try:
        win = curses.newwin(height, width, y, x)
    except curses.error:
        return

    win.bkgd(" ", curses.color_pair(3))
    try:
        textpad.rectangle(win, 0, 0, height - 1, width - 1)
    except curses.error:
        pass

    try:
        win.attrset(curses.A_BOLD | curses.color_pair(7))
        win.addstr(0, 2, f" {title} ")
        win.attrset(curses.color_pair(3))
        for i, line in enumerate(lines[: height - 5], start=2):
            win.addstr(i, 2, line[: width - 4])
        win.attrset(curses.A_BOLD | curses.color_pair(6))
        if height - 2 >= 0:
            win.addstr(height - 2, max(2, width // 2 - 5), "  OK  ")
        win.refresh()
    except curses.error:
        pass

    while True:
        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, 10, 13, 27, ord(" ")):
            break

def handle_command(stdscr, cmd):
    if cmd == "ABOUT":
        show_popup(stdscr, "About", "Curses TUI Demo\nDOS-style menus in Python.")
    elif cmd == "EXIT":
        return False
    else:
        show_popup(stdscr, "Command", f"Executed: {cmd}")
    return True

def event_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    init_colors()
    draw_frame(stdscr)

    menu_open = False
    active_menu = 0
    active_item = 0

    def clamp_item():
        nonlocal active_item
        items = MENU[active_menu][1]
        valid = [i for i, (n, _) in enumerate(items) if n != "-"]
        if not valid:
            active_item = 0
            return
        if items[active_item][0] == "-":
            for i in range(active_item + 1, len(items)):
                if items[i][0] != "-":
                    active_item = i; return
            for i in range(active_item - 1, -1, -1):
                if items[i][0] != "-":
                    active_item = i; return

    # Repaint control
    need_full_redraw = True
    last_menu_open = False
    last_active_menu = -1

    while True:
        # Redraw background when layout-affecting state changes
        if (need_full_redraw or
            menu_open != last_menu_open or
            active_menu != last_active_menu):
            draw_frame(stdscr)
            need_full_redraw = False
            last_menu_open = menu_open
            last_active_menu = active_menu

        # Draw dropdown AFTER the background (do not erase background)
        if menu_open:
            _ = draw_dropdown(stdscr, active_menu, active_item)

        ch = stdscr.getch()

        if ch in (ord('q'), ord('Q'), curses.KEY_F10):
            return

        if ch == curses.KEY_RESIZE:
            need_full_redraw = True
            continue

        if ch == curses.KEY_F9:
            menu_open = not menu_open
            if menu_open:
                active_item = 0
                clamp_item()
            need_full_redraw = True
            continue

        if not menu_open:
            if 32 <= ch <= 126:
                key = chr(ch).lower()
                for i, (label, _items) in enumerate(MENU):
                    hi = _hot_index(label)
                    if hi != -1 and _strip_amp(label)[hi].lower() == key:
                        menu_open = True
                        active_menu = i
                        active_item = 0
                        clamp_item()
                        need_full_redraw = True
                        break
            continue

        # Menu open: navigation
        if ch == curses.KEY_LEFT:
            active_menu = (active_menu - 1) % len(MENU)
            active_item = 0; clamp_item()
            need_full_redraw = True
            continue
        if ch == curses.KEY_RIGHT:
            active_menu = (active_menu + 1) % len(MENU)
            active_item = 0; clamp_item()
            need_full_redraw = True
            continue
        if ch == curses.KEY_UP:
            i = active_item - 1
            items = MENU[active_menu][1]
            while i >= 0 and items[i][0] == "-":
                i -= 1
            if i >= 0: active_item = i
            # same dropdown footprint — no full redraw required
            continue
        if ch == curses.KEY_DOWN:
            i = active_item + 1
            items = MENU[active_menu][1]
            while i < len(items) and items[i][0] == "-":
                i += 1
            if i < len(items): active_item = i
            continue
        if ch == 27:  # Esc
            menu_open = False
            need_full_redraw = True
            continue
        if ch in (curses.KEY_ENTER, 10, 13):
            name, cmd = MENU[active_menu][1][active_item]
            if cmd is None or name == "-":
                continue
            menu_open = False
            need_full_redraw = True
            draw_frame(stdscr)
            if not handle_command(stdscr, cmd):
                return
            need_full_redraw = True
            continue

def main():
    curses.wrapper(event_loop)

if __name__ == "__main__":
    main()

