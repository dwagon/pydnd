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
    def obj_dead(self, obj):
        """ Object is no longer part of the living or unliving """
        print("{} has died".format(obj.name))
        del self.arena[(obj.x, obj.y)]

    ##########################################################################
    def obj_attack(self, obj):
        """ Move towards an enemy until one is range and then attack them """
        moves = obj.movement
        for _ in range(moves):
            targ_list = self.enemy_neighbours(obj)
            if not targ_list:
                self.move(obj)
                continue
            else:
                break
        else:
            return
        targ = random.choice(targ_list)
        dmg = obj.attack(targ)
        if dmg:
            print("{} hit {} for {} -> {}".format(obj.name, targ.name, dmg, targ.get_status_display()))
            if targ.status == MonsterState.DEAD:
                self.obj_dead(targ)
        else:
            print("{} missed {}".format(obj.name, targ.name))

    ##########################################################################
    def pc_attack(self):
        for pc in self.pcs:
            if pc.status == Character.OK:
                self.obj_attack(pc)

    ##########################################################################
    def monster_attack(self):
        for monster in self.monsters:
            if monster.status == MonsterState.OK:
                self.obj_attack(monster)

    ##########################################################################
    def dir_to_move(self, obj):
        ne = self.nearest_enemy(obj)
        if not ne:
            return
        if ne.x < obj.x:
            return 'W'
        if ne.x > obj.x:
            return 'E'
        if ne.y < obj.y:
            return 'S'
        if ne.y > obj.y:
            return 'N'

    ##########################################################################
    def move(self, obj):
        ne = self.nearest_enemy(obj)
        if not ne:
            return
        d = self.dir_to_move(obj)
        for delta in [0, 1, -1]:
            if d == 'N':
                targy = obj.y + 1
                targx = obj.x + delta
            elif d == 'S':
                targy = obj.y - 1
                targx = obj.x + delta
            elif d == 'E':
                targy = obj.x + 1
                targx = obj.y + delta
            elif d == 'W':
                targy = obj.x - 1
                targx = obj.y + delta
            if (targx, targy) in self.arena:
                continue
            break
        else:
            print("{} Movement toward {} blocked by {}".format(obj.name, ne.name, self.arena[(targx, targy)]))
            return

        del self.arena[(obj.x, obj.y)]
        obj.x = targx
        obj.y = targy
        obj.save()
        print("{} moved to {}, {}".format(obj.name, targx, targy))
        self.arena[(targx, targy)] = obj

# EOF
