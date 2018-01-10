#!/usr/bin/env python

import requests
import json
import os
import sys

baseurl = 'http://localhost:8000'
retries = 5


##############################################################################
def rmethod(url, method, data={}):
    for i in range(retries):
        try:
            r = method(baseurl + url, json=data)
            if r.status_code in (200, 201):
                data = json.loads(r.content)
                return data
            else:
                sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
                sys.stderr.write("Content={}\n".format(r.content))
                sys.exit(1)
        except Exception as exc:
            sys.stderr.write("Retry {}: {}\n".format(i, exc))
    else:
        sys.stderr.write("Failed to {}: {}: {}\n".format(method.__name__, url, data))
        sys.exit(1)


##############################################################################
def rpost(url, data):
    return rmethod(url, sess.post, data)


##############################################################################
def rget(url):
    return rmethod(url, sess.get)


##############################################################################
def rdelete(url):
    return rmethod(url, sess.delete)


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
        sys.stderr.write("Creating world\n")
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
    return resp


##############################################################################
def place_monsters(enc_id):
    rpost('/encounter/{}/place_monsters/'.format(enc_id), data={})


##############################################################################
def print_arena(enc_id):
    ans = rget('/encounter/{}/arena/'.format(enc_id))
    print(ans['map'])
    print("")


##############################################################################
def get_messages(enc_id):
    msglist = rget('/message/')
    for m in msglist:
        print(m['msg'])
        rdelete('/message/{}/'.format(m['id']))


##############################################################################
def place_pcs(enc_id):
    rpost('/encounter/{}/place_pcs/'.format(enc_id), data={})


##############################################################################
def delete_char(ch):
    sys.stderr.write("Deleting {}\n".format(ch['name']))
    rdelete('/character/{}/'.format(ch['id']))


##############################################################################
def delete_encounter(enc_id):
    sys.stderr.write("Deleting encounter\n")
    rdelete('/encounter/{}/'.format(enc_id))


##############################################################################
def delete_world(world_id, chars):
    for ch in chars:
        delete_char(ch)
    sys.stderr.write("Deleting world\n")
    rdelete('/world/{}/'.format(world_id))


##############################################################################
def combat_round(enc_id):
    ans = rpost('/encounter/{}/combat_round/'.format(enc_id), data={})
    return ans['finished']


##############################################################################
def main():
    global sess
    sess = requests.session()
    sess.trust_env = False
    world_id = get_world()
    chars = make_chars(world_id)
    encounter_id = make_encounter(world_id, 15, 15)
    place_pcs(encounter_id)
    add_monsters(encounter_id, 'Orc', number=15)
    place_monsters(encounter_id)
    print_arena(encounter_id)

    while True:
        finished = combat_round(encounter_id)
        if finished:
            break
        print_arena(encounter_id)
        get_messages(encounter_id)

    print_arena(encounter_id)
    delete_encounter(encounter_id)
    delete_world(world_id, chars)


##############################################################################
if __name__ == "__main__":
    main()

# EOF
