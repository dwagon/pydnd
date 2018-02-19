#!/usr/bin/env python

import curses
import pydnd
from collections import deque

msg_win_height = 6


##############################################################################
class Screen(object):
    def __init__(self, screen):
        self.encounter_id = None
        self.msgbuf = deque([], msg_win_height)
        self.screen = screen
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.arena_x = int((self.screen_width * 2)/(3 * 5))
        self.arena_y = int((self.screen_height - msg_win_height + 2) / 2) - 3
        self.phase = 'unknown'
        self.turn = 'unknown'
        self.init_windows()
        self.encounter_id = self.init_game()

    #########################################################################
    def init_windows(self):
        third = int(self.screen_width / 3)
        self.message_win = self.screen.subwin(msg_win_height + 2, self.screen_width, self.screen_height-msg_win_height-2, 0)
        self.message_win.border()
        self.message_win.addstr(1, 1, "message_win")

        self.map_win = self.screen.subwin(self.screen_height-msg_win_height-2, third*2, 0, 0)
        self.map_win.border()
        self.map_win.addstr(1, 1, "map_win")

        self.detail_win = self.screen.subwin(self.screen_height-msg_win_height-2, third, 0, third*2)
        self.detail_win.border()
        self.detail_win.addstr(1, 1, "detail_win")
        self.screen.refresh()

    #########################################################################
    def init_game(self):
        pydnd.initiate_session()
        world_id = pydnd.get_world()
        pydnd.delete_all_chars()
        self.add_msg('Making Chars', refresh=True)
        pydnd.make_thief(world_id, "Tom")
        pydnd.make_fighter(world_id, "Fin")
        self.add_msg('Making Encounter', refresh=True)
        encounter_id = pydnd.make_encounter(world_id, self.arena_x, self.arena_y)
        self.add_msg('Placing PCs', refresh=True)
        pydnd.place_pcs(encounter_id)
        self.add_msg('Adding Monsters', refresh=True)
        pydnd.add_monsters(encounter_id, 'Orc', number=15)
        self.add_msg('Placing Monsters', refresh=True)
        pydnd.place_monsters(encounter_id)
        return encounter_id

    #########################################################################
    def add_msg(self, msg, refresh=False):
        self.msgbuf.append(msg)
        if refresh:
            self.display_messages()

    #########################################################################
    def display_messages(self):
        if self.encounter_id:
            msgs = pydnd.get_messages(self.encounter_id, max_num=msg_win_height, delete=True)
            self.msgbuf.extend(msgs)
            self.msgbuf.append("--- Press Return ---")
        self.message_win.erase()
        self.message_win.border()
        self.message_win.addstr(0, 1, " Turn: {} Phase {} ".format(self.turn, self.phase))
        for num, mesg in enumerate(self.msgbuf):
            self.message_win.addstr(num+1, 1, mesg)
        self.message_win.refresh()

    #########################################################################
    def get_encounter(self):
        enc = pydnd.get_encounter(self.encounter_id)
        self.phase = enc['phase']
        self.turn = enc['turn']

    #########################################################################
    def loop(self):
        while True:
            self.get_encounter()
            self.draw_map(self.map_win, self.encounter_id)
            finished = pydnd.combat_phase(self.encounter_id)
            self.display_messages()
            self.screen.refresh()
            self.screen.getch()
            if finished:
                break

    ##########################################################################
    def draw_map(self, win, eid):
        win.clear()
        win.border()
        arena = pydnd.get_arena(eid)
        for x in range(self.arena_x):
            for y in range(self.arena_y):
                win.addstr(y*2+1, x*5+1, '.')
        for loc in arena:
            x_str, y_str = loc.split()
            x, y = int(x_str), int(y_str)
            win.addnstr(y*2+1, x*5+1, arena[loc]['content']['name'], 5)
        win.refresh()


##############################################################################
def main(stdscr):
    s = Screen(stdscr)
    s.loop()


##############################################################################
if __name__ == "__main__":
    curses.wrapper(main)

# EOF
