#!/usr/bin/env python

import django
django.setup()

from world.models import World, Encounter
from character.models import Equipment, Weapon, Fighter

w = World()
w.save()
e = Encounter(w, 'Orc', number=10)
ls = Weapon(name='Long Sword', damage='1d8')
ls.save()
sp = Equipment(name='Iron Spikes')
sp.save()

for i in range(10):
    f = Fighter(name='Bob{}'.format(i), world=w)
    f.save()

    f.equip(sp)
    f.equip(ls, ready=True)

while True:
    if not e.combat_round():
        break

e.status()
e.close()

f.delete()
sp.delete()
ls.delete()
w.delete()
