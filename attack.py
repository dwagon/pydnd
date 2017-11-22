#!/usr/bin/env python

import django
django.setup()

from world.models import World, Encounter
from character.models import Equipment, Weapon, Fighter, Character

w = World()
w.save()
e = Encounter(w, 'Orc', number=5, arenasize=20)
ls = Weapon(name='Long Sword', damage='1d8')
ls.save()
sp = Equipment(name='Iron Spikes')
sp.save()

for i in range(4):
    f = Fighter(name='Bob{}'.format(i), world=w)
    f.generate_stats()
    f.save()

    f.equip(sp)
    f.equip(ls, ready=True)
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
sp.delete()
ls.delete()
w.delete()
