#!/usr/bin/env python

import requests
import json
import os
import sys
import time

baseurl = 'http://localhost:8000'
retries = 5


##############################################################################
def rmethod(url, method, data={}):
    for i in range(retries):
        try:
            if method.__name__ == 'delete':
                r = method(baseurl + url)
                if not r.ok:
                    sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
                return
            else:
                r = method(baseurl + url, json=data)
                if r.ok:
                    data = json.loads(r.content)
                    return data
                else:
                    sys.stderr.write("Error {}: {}\n".format(r.status_code, url))
                    sys.stderr.write("Content={}\n".format(r.content))
                    return
        except Exception as exc:
            sys.stderr.write("Retry {}: {}\n".format(i, exc))
            time.sleep(0.1)
    else:
        sys.stderr.write("Failed to {}: {}: {}\n".format(method.__name__, url, data))
        return


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
def get_character(name=''):
    data = rget('/character/?name={}'.format(name))
    if data:
        return data


##############################################################################
def get_monsters(enc_id):
    data = rget('/monster/state/?encounter={}'.format(enc_id))
    if data:
        return data


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
        "charclass": 'FG',
        "stat_str": 18,
        "name": name
        }
    resp = rpost('/character/', data)
    ls = get_weapon('Longsword')
    rget('/character/{}/equip/'.format(resp['id']))
    rpost('/character/{}/equip/{}'.format(resp['id'], ls['id']), data={'ready': True})
    return resp


##############################################################################
def make_rogue(world_id, name):
    data = {
        "world": world_id,
        "charclass": 'RO',
        "stat_dex": 18,
        "name": name
        }
    resp = rpost('/character/', data)
    lb = get_weapon('Long bow')
    rpost('/character/{}/equip/{}'.format(resp['id'], lb['id']), data={'ready': True})
    return resp


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
    return resp


##############################################################################
def place_monsters(enc_id):
    rpost('/encounter/{}/place_monsters/'.format(enc_id), data={})


##############################################################################
def start_encounter(enc_id):
    rpost('/encounter/{}/start_encounter/'.format(enc_id), data={})


##############################################################################
def get_arena(enc_id):
    ans = rget('/encounter/{}/arena/'.format(enc_id))
    return ans


##############################################################################
def get_encounter(enc_id):
    ans = rget('/encounter/{}/'.format(enc_id))
    return ans


##############################################################################
def get_messages(enc_id, max_num=None, delete=False):
    ans = []
    msglist = rget('/message/')
    if max_num:
        msglist = msglist[:max_num]
    for m in msglist:
        ans.append(m['msg'])
        if delete:
            rdelete('/message/{}/'.format(m['id']))
    return ans


##############################################################################
def delete_all_chars():
    ans = rget('/character/')
    for ch in ans:
        ans = delete_char(ch)


##############################################################################
def place_pcs(enc_id):
    rpost('/encounter/{}/place_pcs/'.format(enc_id), data={})


##############################################################################
def delete_char(ch):
    ans = rdelete('/character/{}/'.format(ch['id']))
    return(ans)


##############################################################################
def delete_encounter(enc_id):
    rdelete('/encounter/{}/'.format(enc_id))


##############################################################################
def delete_world(world_id, chars=[]):
    for ch in chars:
        delete_char(ch)
    rdelete('/world/{}/'.format(world_id))


##############################################################################
def combat_phase(enc_id):
    ans = rpost('/encounter/{}/combat_phase/'.format(enc_id), data={})
    return ans


##############################################################################
def initiate_session():
    global sess
    sess = requests.session()
    sess.trust_env = False
    return sess


##############################################################################
def main():
    initiate_session()
    delete_all_chars()
    world_id = get_world()
    print("world_id={}".format(world_id))
    make_rogue(world_id, "Tom")
    make_fighter(world_id, "Fez")
    encounter_id = make_encounter(world_id, 15, 15)
    print("encounter_id={}".format(encounter_id))
    place_pcs(encounter_id)
    add_monsters(encounter_id, 'Orc', number=4)
    place_monsters(encounter_id)
    start_encounter(encounter_id)

    while True:
        who = combat_phase(encounter_id)
        arena = get_arena(encounter_id)
        for y in range(15):
            for x in range(15):
                loc = "{} {}".format(x, y)
                if loc in arena:
                    sys.stdout.write("{:5}".format(arena[loc]['content']['name']))
                else:
                    sys.stdout.write("{:5}".format(". "))
            sys.stdout.write("\n")

        encounter = get_encounter(encounter_id)
        print("encounter={}".format(encounter))
        chars = get_character(encounter_id)
        print("chars")
        for ch in chars:
            print("  {}".format(ch))
        mons = get_monsters(encounter_id)
        print("monsters")
        for mo in mons:
            print("  {}".format(mo))
        print("Who: {}".format(who))
        msgs = get_messages(encounter_id, delete=True)
        for m in msgs:
            print("{}".format(m))
        input("--- Hit Return ---")

    delete_encounter(encounter_id)
    delete_world(world_id)


##############################################################################
if __name__ == "__main__":
    main()

# EOF
