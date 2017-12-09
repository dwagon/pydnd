#!/usr/bin/env python

import requests
import json
import os
import sys

baseurl = 'http://localhost:8000'


##############################################################################
def rpost(url, data):
    r = requests.post(baseurl + url, json=data)
    if r.status_code in (200, 201):
        data = json.loads(r.content)
        return data
    else:
        sys.stderr.write("Error {}: {}".format(r.status_code, url))
        sys.exit(1)


##############################################################################
def rget(url):
    r = requests.get(baseurl + url)
    if r.status_code in (200, 201):
        data = json.loads(r.content)
        return data
    else:
        sys.stderr.write("Error {}: {}".format(r.status_code, url))
        sys.exit(1)


##############################################################################
def get_world():
    data = rget('/world/')
    if data:
        world_id = data[0]['id']
    else:
        data = rpost('/world/', {"name": "attack{}".format(os.getpid())})
        world_id = data['id']
    return world_id


##############################################################################
def make_fighter(world_id, name):
    data = {
        "world": world_id,
        "charclass": 'F',
        "stat_str": 18,
        "name": name
        }
    resp = rpost('/character/', data)
    return resp


##############################################################################
def make_thief(world_id, name):
    data = {
        "world": world_id,
        "charclass": 'T',
        "stat_dex": 18,
        "name": name
        }
    resp = rpost('/character/', data)
    return resp


##############################################################################
def make_chars(world_id):
    chars = []

    for i in range(4):
        chars.append(make_fighter(world_id, "Bob{}".format(i)))

    for i in range(4):
        chars.append(make_thief(world_id, "Tom{}".format(i)))
    return chars


##############################################################################
def main():
    world_id = get_world()
    chars = make_chars(world_id)
    print(chars)

# ls = Weapon(name='Long Sword', damage='1d8')
# ls.save()
# lb = Weapon(name='Long Bow', damage='1d6', reach=20)
# lb.save()

# #
#     f.equip(ls, ready=True)
# e = Encounter.create(size_x=20, size_y=20, world=w)
# e.save()
# e.add_monster_type('Orc', number=9)
#
# e.place_monsters()
# e.print_arena()
#
# while True:
#     if not e.combat_round():
#         break
#     e.print_arena()
#
# e.status()
# e.close()
#
# for f in Character.objects.all():
#     f.delete()
# ls.delete()

if __name__ == "__main__":
    main()

# EOF
