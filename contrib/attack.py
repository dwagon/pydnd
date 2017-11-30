#!/usr/bin/env python

import django
django.setup()

from world.models import Encounter
from character.models import Weapon, Fighter, Character, Thief

ls = Weapon(name='Long Sword', damage='1d8')
ls.save()
lb = Weapon(name='Long Bow', damage='1d6', reach=20)
lb.save()

for i in range(4):
    f = Fighter(name='Bob{}'.format(i), stat_str=18)
    f.save()
    f.equip(ls, ready=True)
for i in range(4):
    f = Thief(name='Tom{}'.format(i), stat_dex=18)
    f.save()
    f.equip(lb, ready=True)
e = Encounter.create(arena_x=20, arena_y=20)
e.save()
e.add_monster_type('Orc', number=9)

e.place_monsters()
e.print_arena()

while True:
    if not e.combat_round():
        break
    e.print_arena()

e.status()
e.close()

for f in Character.objects.all():
    f.delete()
ls.delete()
