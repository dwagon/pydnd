from monster.models import Monster, MonsterState
from character.models import Character
from utils import roll
import random


##############################################################################
class Encounter(object):
    def __init__(self, world, monstername, **kwargs):
        self.world = world
        self.round = 0
        self.monsters = []
        self.m = Monster.objects.get(name=monstername)
        if 'number' in kwargs:
            num = kwargs['number']
        else:
            num = roll(self.m.numappearing)
        for _ in range(num):
            m = MonsterState(monster=self.m)
            m.save()
            self.monsters.append(m)

    def status(self):
        pcs = Character.objects.filter(world=self.world)
        for pc in pcs:
            print(pc)
        for mon in self.monsters:
            print(mon)

    def combat_round(self):
        self.round += 1
        print("\nRound {}".format(self.round))
        pcs = Character.objects.filter(world=self.world)
        m_targets = [_ for _ in self.monsters if _.status == MonsterState.OK]
        if not m_targets:
            return False
        pc_targets = [_ for _ in pcs if _.status == Character.OK]
        if not pc_targets:
            return False
        # TODO: Initiative
        for pc in pcs:
            if pc.status != Character.OK:
                continue
            targ = random.choice(m_targets)
            dmg = pc.attack(targ)
            if dmg:
                print("{} hit {} for {} -> {}".format(pc.name, targ.name, dmg, targ.get_status_display()))
            else:
                print("{} missed".format(pc.name))
        for monster in self.monsters:
            if monster.status != MonsterState.OK:
                continue
            targ = random.choice(pc_targets)
            dmg = monster.attack(targ)
            if dmg:
                print("{} hit {} for {} -> {}".format(monster.name, targ.name, dmg, targ.get_status_display()))
            else:
                print("{} missed".format(monster.name))
        return True

# EOF
