#!/usr/bin/env python

import django
django.setup()

from world.models import World, Encounter
from character.models import Weapon, Fighter, Character, Thief

w = World()
w.save()
e = Encounter(w, 'Orc', number=9, arenasize=20)
ls = Weapon(name='Long Sword', damage='1d8')
ls.save()
lb = Weapon(name='Long Bow', damage='1d6', reach=20)
lb.save()

for i in range(4):
    f = Fighter(name='Bob{}'.format(i), world=w)
    f.generate_stats()
    f.save()
    f.equip(ls, ready=True)
for i in range(4):
    f = Thief(name='Tom{}'.format(i), world=w, stat_dex=18)
    f.generate_stats()
    f.save()
    f.equip(lb, ready=True)

e.place_pcs()
e.place_monsters()
e.print_arena()

while True:
    if not e.combat_round():
        break
    e.print_arena()

e.status()
e.close()

for f in Character.objects.filter(world=w):
    f.delete()
ls.delete()
w.delete()
