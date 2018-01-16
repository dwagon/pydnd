#!/usr/bin/env python

import curses
import pydnd


##############################################################################
def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    return stdscr


##############################################################################
def draw_map(scr, eid):
    arena = pydnd.get_arena(eid)
    scr.border()
    for loc in arena:
        x_str, y_str = loc.split()
        x, y = int(x_str), int(y_str)
        f = open('/tmp/foo.2', 'a')
        try:
            f.write("{} {} {} {}\n".format(y, x, loc, arena[loc]))
        except Exception as exc:
            f.write("exc={}\n".format(exc))
        f.close()
        y = min(y, 0)
        x = min(x, 0)
        scr.addnstr(y, x, arena[loc]['content']['name'], 5)
    scr.refresh()


##############################################################################
def end_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


##############################################################################
def main(stdscr):
    pydnd.initiate_session()
    world_id = pydnd.get_world()
    chars = pydnd.make_chars(world_id)
    encounter_id = pydnd.make_encounter(world_id, 15, 15)
    pydnd.place_pcs(encounter_id)
    pydnd.add_monsters(encounter_id, 'Orc', number=15)
    pydnd.place_monsters(encounter_id)
    draw_map(stdscr, encounter_id)
    len(chars)


##############################################################################
if __name__ == "__main__":
    curses.wrapper(main)

# EOF
