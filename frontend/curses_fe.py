#!/usr/bin/env python

import curses
import pydnd
from collections import deque

arena_x = 10
arena_y = 20

msg_win_height = 8


##############################################################################
class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.init_windows()
        self.msgbuf = deque([], msg_win_height)
        self.encounter_id = self.init_game()

    #########################################################################
    def init_windows(self):
        third = int(self.screen_width / 3)
        self.message_win = self.screen.subwin(msg_win_height, self.screen_width, self.screen_height-msg_win_height, 0)
        self.message_win.border()
        self.message_win.addstr(1, 1, "message_win")
        self.map_win = self.screen.subwin(self.screen_height-msg_win_height, third*2+1, 0, 0)
        self.map_win.border()
        self.map_win.addstr(1, 1, "map_win")
        self.detail_win = self.screen.subwin(self.screen_height-msg_win_height, third, 0, third*2)
        self.detail_win.border()
        self.detail_win.addstr(1, 1, "detail_win")
        self.screen.refresh()

    #########################################################################
    def init_game(self):
        pydnd.initiate_session()
        world_id = pydnd.get_world()
        self.add_msg('Making Chars')
        pydnd.make_chars(world_id)
        self.add_msg('Making Encounter')
        encounter_id = pydnd.make_encounter(world_id, arena_x, arena_y)
        self.add_msg('Placing PCs')
        pydnd.place_pcs(encounter_id)
        self.add_msg('Adding Monsters')
        pydnd.add_monsters(encounter_id, 'Orc', number=15)
        self.add_msg('Placing Monsters')
        pydnd.place_monsters(encounter_id)
        return encounter_id

    #########################################################################
    def add_msg(self, msg=''):
        if isinstance(msg, str):
            self.msgbuf.append(msg)
        if not msg:
            msgs = pydnd.get_messages(self.encounter_id, max_num=msg_win_height, delete=True)
            self.msgbuf.extend(msgs)
        for num, mesg in enumerate(self.msgbuf):
            self.message_win.addstr(num+1, 1, mesg)
        self.message_win.refresh()

    #########################################################################
    def loop(self):
        self.draw_map(self.map_win, self.encounter_id)
        self.screen.refresh()
        self.screen.getch()

    ##########################################################################
    def draw_map(self, win, eid):
        win.clear()
        win.border()
        arena = pydnd.get_arena(eid)
        for x in range(arena_x):
            for y in range(arena_y):
                win.addstr(y+1, x*5+1, '.')
        for loc in arena:
            x_str, y_str = loc.split()
            x, y = int(x_str), int(y_str)
            win.addnstr(y+1, x*5+1, arena[loc]['content']['name'], 5)
        win.refresh()


##############################################################################
def main(stdscr):
    s = Screen(stdscr)
    s.loop()


##############################################################################
if __name__ == "__main__":
    curses.wrapper(main)

# EOF
