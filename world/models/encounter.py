from monster.models import Monster, MonsterState
from character.models import Character
from utils import roll
import math
import random
import sys


##############################################################################
class Encounter(object):
    MONSTER = 'M'
    PC = 'P'

    def __init__(self, world, monstername, **kwargs):
        self.world = world
        self.round = 0
        self.arenasize = kwargs['arenasize'] if 'arenasize' in kwargs else 40
        self.arena = {}
        self.monsters = []
        self.m = Monster.objects.get(name=monstername)
        self.pcs = Character.objects.filter(world=self.world)
        num = kwargs['number'] if 'number' in kwargs else roll(self.m.numappearing)
        for _ in range(num):
            m = MonsterState(monster=self.m)
            m.name = "{}{}".format(self.m.name, _)
            m.save()
            self.monsters.append(m)

    ##########################################################################
    def place_pcs(self):
        for pc in self.pcs:
            x = int(self.arenasize / 2)
            y = int(self.arenasize / 2)
            while (x, y) in self.arena:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.arena[(x, y)] = pc
            pc.x = x
            pc.y = y
            pc.save()

    ##########################################################################
    def place_monsters(self):
        for monster in self.monsters:
            x = random.randint(0, self.arenasize)
            y = random.randint(0, self.arenasize)
            while (x, y) in self.arena:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.arena[(x, y)] = monster
            monster.x = x
            monster.y = y
            monster.save()

    ##########################################################################
    def print_arena(self, out=sys.stdout):
        for x in range(self.arenasize):
            for y in range(self.arenasize):
                if (x, y) in self.arena:
                    out.write("{:5}".format(self.arena[(x, y)].name[:5]))
                else:
                    out.write("{:5}".format(". "))
            out.write("\n")
        out.write("\n")

    ##########################################################################
    def neighbours(self, obj):
        n = []
        objx = obj.x
        objy = obj.y
        for x in [objx-1, objx, objx+1]:
            for y in [objy-1, objy, objy+1]:
                if (x, y) in self.arena:
                    n.append(self.arena[(x, y)])
        return n

    ##########################################################################
    def objtype(self, obj):
        if isinstance(obj, Character):
            return self.PC
        else:
            return self.MONSTER

    ##########################################################################
    def enemy_neighbours(self, obj):
        """ Return a list of valid targets for obj (PC or Monster)"""
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        ns = self.neighbours(obj)
        badns = []
        for n in ns:
            if self.objtype(n) == self.PC and enemy == self.PC and n.status != Character.DEAD:
                badns.append(n)
            if self.objtype(n) == self.MONSTER and enemy == self.MONSTER and n.status != MonsterState.DEAD:
                badns.append(n)
        return badns

    ##########################################################################
    def nearest_enemy(self, obj):
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        min_dist = 99999
        min_obj = None
        if enemy == self.PC:
            targets = [_ for _ in self.pcs if _.status == Character.OK]
        else:
            targets = [_ for _ in self.monsters if _.status == MonsterState.OK]
        for t in targets:
            d = self.distance(obj, t)
            if d < min_dist:
                min_dist = d
                min_obj = t
        return min_obj

    ##########################################################################
    def distance(self, a, b):
        dist = math.sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2))
        return dist

    ##########################################################################
    def status(self):
        for pc in self.pcs:
            print(pc)
        for mon in self.monsters:
            print(mon)

    ##########################################################################
    def close(self):
        xp = 0
        for monster in self.monsters[:]:
            xp + monster.xp
            monster.delete()
        survivors = [_ for _ in self.pcs if _.status != Character.DEAD]
        for surv in survivors:
            surv.earnXp(xp / len(survivors))

    ##########################################################################
    def combat_round(self):
        self.round += 1
        print("\nRound {}".format(self.round))
        m_targets = [_ for _ in self.monsters if _.status == MonsterState.OK]
        if not m_targets:
            return False
        pc_targets = [_ for _ in self.pcs if _.status == Character.OK]
        if not pc_targets:
            return False
        # TODO: Initiative
        self.pc_attack()
        self.monster_attack()

        return True

    ##########################################################################
    def pc_attack(self):
        for pc in self.pcs:
            if pc.status != Character.OK:
                continue
            targ_list = self.enemy_neighbours(pc)
            if not targ_list:
                self.move(pc)
                continue
            targ = random.choice(targ_list)
            dmg = pc.attack(targ)
            if dmg:
                print("{} hit {} for {} -> {}".format(pc.name, targ.name, dmg, targ.get_status_display()))
                if targ.status == MonsterState.DEAD:
                    del self.arena[(targ.x, targ.y)]
            else:
                print("{} missed {}".format(pc.name, targ.name))

    ##########################################################################
    def monster_attack(self):
        for monster in self.monsters:
            if monster.status != MonsterState.OK:
                continue
            targ_list = self.enemy_neighbours(monster)
            if not targ_list:
                self.move(monster)
                continue
            targ = random.choice(targ_list)
            dmg = monster.attack(targ)
            if dmg:
                print("{} hit {} for {} -> {}".format(monster.name, targ.name, dmg, targ.get_status_display()))
                if targ.status == Character.DEAD:
                    del self.arena[(targ.x, targ.y)]
            else:
                print("{} missed {}".format(monster.name, targ.name))

    ##########################################################################
    def move(self, obj):
        ne = self.nearest_enemy(obj)
        if not ne:
            return
        targx = obj.x
        targy = obj.y
        if ne.x < obj.x:
            targx -= 1
        elif ne.x > obj.x:
            targx += 1
        if ne.y < obj.y:
            targy -= 1
        elif ne.y > obj.y:
            targy += 1
        if (targx, targy) in self.arena:
            print("{} Movement toward {} blocked by {}".format(obj.name, ne.name, self.arena[(targx, targy)]))
            return
        del self.arena[(obj.x, obj.y)]
        obj.x = targx
        obj.y = targy
        obj.save()
        print("{} moved to {}, {}".format(obj.name, targx, targy))
        self.arena[(targx, targy)] = obj

# EOF
