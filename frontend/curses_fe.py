#!/usr/bin/env python

import curses
import pydnd

arena_x = 10
arena_y = 20


##############################################################################
class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.init_windows()
        self.encounter_id = self.init_game()

    #########################################################################
    def init_windows(self):
        third = int(self.screen_width / 3)
        self.message_win = self.screen.subwin(5, self.screen_width, self.screen_height-5, 0)
        self.message_win.border()
        self.map_win = self.screen.subwin(self.screen_height-4, third*2+1, 0, 0)
        self.map_win.border()
        self.detail_win = self.screen.subwin(self.screen_height-4, third, 0, third*2)
        self.detail_win.border()
        self.screen.refresh()

    #########################################################################
    def init_game(self):
        pydnd.initiate_session()
        world_id = pydnd.get_world()
        pydnd.make_chars(world_id)
        encounter_id = pydnd.make_encounter(world_id, arena_x, arena_y)
        pydnd.place_pcs(encounter_id)
        pydnd.add_monsters(encounter_id, 'Orc', number=15)
        pydnd.place_monsters(encounter_id)
        return encounter_id

    #########################################################################
    def loop(self):
        self.draw_map(self.map_win, self.encounter_id)
        self.screen.refresh()
        self.screen.getch()

    ##########################################################################
    def draw_map(self, win, eid):
        arena = pydnd.get_arena(eid)
        win.border()
        win.addstr(0, 0, "Testing")
        win.bkgd('.')
        for loc in arena:
            x_str, y_str = loc.split()
            x, y = int(x_str), int(y_str)
            win.addnstr(y, x*4, arena[loc]['content']['name'], 4)
        win.refresh()


##############################################################################
def main(stdscr):
    s = Screen(stdscr)
    s.loop()


##############################################################################
if __name__ == "__main__":
    curses.wrapper(main)

# EOF
