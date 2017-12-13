#!/usr/bin/env python

import requests
import json
import os
import sys

baseurl = 'http://localhost:8000'


##############################################################################
def rpost(url, data):
    r = sess.post(baseurl + url, json=data)
    if r.status_code in (200, 201):
        data = json.loads(r.content)
        return data
    else:
        sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
        sys.stderr.write("Content={}\n".format(r.content))
        sys.exit(1)


##############################################################################
def rget(url):
    r = sess.get(baseurl + url)
    if r.status_code in (200, 201):
        data = json.loads(r.content)
        return data
    else:
        sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
        sys.exit(1)


##############################################################################
def rdelete(url):
    r = sess.delete(baseurl + url)
    if r.status_code in (200, 204):
        return
    else:
        sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
        sys.exit(1)


##############################################################################
def get_weapon(wname):
    data = rget('/equipment/?name={}'.format(wname))
    if data:
        return data[0]


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
    ls = get_weapon('Long Sword')
    rget('/character/{}/equip/'.format(resp['id']))
    rpost('/character/{}/equip/{}'.format(resp['id'], ls['id']), data={'ready': True})
    sys.stderr.write("Created {}\n".format(resp['name']))
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
    lb = get_weapon('Long Bow')
    rpost('/character/{}/equip/{}'.format(resp['id'], lb['id']), data={'ready': True})
    sys.stderr.write("Created {}\n".format(resp['name']))
    return resp


##############################################################################
def make_chars(world_id):
    chars = []

    for i in range(4):
        chars.append(make_fighter(world_id, "Fez{}".format(i)))

    for i in range(4):
        chars.append(make_thief(world_id, "Tom{}".format(i)))
    return chars


##############################################################################
def make_encounter(world_id, size_x, size_y):
    data = {'world': world_id, 'size_x': size_x, 'size_y': size_y, 'turn': 0}
    resp = rpost('/encounter/', data)
    return resp['id']


##############################################################################
def add_monsters(enc_id, monname, number=None):
    m = rget('/monster/?name={}'.format(monname))
    data = {'number': number}
    resp = rpost('/encounter/{}/monster/{}'.format(enc_id, m[0]['id']), data)
    sys.stderr.write("Added {} {}\n".format(len(resp), m[0]['name']))


##############################################################################
def place_monsters(enc_id):
    rpost('/encounter/{}/place_monsters/'.format(enc_id), data={})


##############################################################################
def print_arena(enc_id):
    ans = rget('/encounter/{}/arena/'.format(enc_id))
    print(ans['map'])


##############################################################################
def place_pcs(enc_id):
    rpost('/encounter/{}/place_pcs/'.format(enc_id), data={})


##############################################################################
def delete_char(ch):
    sys.stderr.write("Deleting {}\n".format(ch['name']))
    rdelete('/character/{}'.format(ch['id']))


##############################################################################
def main():
    global sess
    sess = requests.session()
    sess.trust_env = False
    world_id = get_world()
    chars = make_chars(world_id)
    encounter_id = make_encounter(world_id, 15, 15)
    place_pcs(encounter_id)
    add_monsters(encounter_id, 'Orc', number=9)
    place_monsters(encounter_id)
    print_arena(encounter_id)

# while True:
#     if not e.combat_round():
#         break
#     e.print_arena()
#
# e.status()
# e.close()

    for ch in chars:
        delete_char(ch)

##############################################################################
if __name__ == "__main__":
    main()

# EOF
