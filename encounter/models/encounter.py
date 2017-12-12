import math
import random
import status
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .map_bits import Wall
from character.models import Character
from .location import Location
from monster.models import Monster, MonsterState
from utils import roll


##############################################################################
class Encounter(models.Model):
    MONSTER = 'M'
    PC = 'P'

    turn = models.IntegerField(default=0)
    world = models.ForeignKey('world.World', on_delete=models.CASCADE)
    size_x = models.IntegerField(default=0)
    size_y = models.IntegerField(default=0)

    ##########################################################################
    @classmethod
    def create(cls, *args, **kwargs):
        if 'place_pcs' in kwargs:
            place_pcs = kwargs['place_pcs']
            del kwargs['place_pcs']
        else:
            place_pcs = True

        enc = cls(*args, **kwargs)
        enc.save()
        if place_pcs:
            enc.place_pcs()
        return enc

    ##########################################################################
    def add_monster_type(self, monstername, number=0):
        m = Monster.objects.get(name=monstername)
        num = number if number else roll(m.numappearing)
        for _ in range(num):
            ms = MonsterState(encounter=self, monster=m)
            ms.name = "{}{}".format(m.name, _)
            ms.save()

    ##########################################################################
    def place_pcs(self):
        """ Put all PCs in this world in the arena clustered around the middle """
        for pc in self.world.all_pcs():
            x = int(self.size_x / 2)
            y = int(self.size_y / 2)
            while self[(x, y)]:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.set_location(pc, x, y)

    ##########################################################################
    def place_monsters(self):
        for monster in MonsterState.objects.filter(encounter=self):
            x = random.randint(0, self.size_x-1)
            y = random.randint(0, self.size_y-1)
            while self[(x, y)]:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.set_location(monster, x, y)
            monster.x = x
            monster.y = y
            monster.save()

    ##########################################################################
    def neighbours(self, obj):
        assert obj.x >= 0
        assert obj.y >= 0
        arena = {}
        for i in self.all_animate():
            arena[(i.x, i.y)] = i
        n = []
        objx = obj.x
        objy = obj.y
        for x in [objx-1, objx, objx+1]:
            for y in [objy-1, objy, objy+1]:
                if (x, y) in arena:
                    n.append(arena[(x, y)])
        n.remove(obj)
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
            if self.objtype(n) == self.PC and enemy == self.PC and n.status == status.OK:
                badns.append(n)
            if self.objtype(n) == self.MONSTER and enemy == self.MONSTER and n.status == status.OK:
                badns.append(n)
        return badns

    ##########################################################################
    def enemy_in_reach(self, obj, reach):
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        in_reach = set()
        if enemy == self.PC:
            targets = [_ for _ in self.world.all_pcs() if _.status == status.OK]
        else:
            targets = [_ for _ in self.monsters.all() if _.status == status.OK]
        for t in targets:
            d = self.distance(obj, t)
            if d < reach:
                in_reach.add(t)
        return list(in_reach)

    ##########################################################################
    def nearest_enemy(self, obj):
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        min_dist = 99999
        min_obj = None
        if enemy == self.PC:
            targets = [_ for _ in self.world.all_pcs() if _.status == status.OK]
        else:
            targets = [_ for _ in self.monsters.all() if _.status == status.OK]
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
        for pc in self.world.all_pcs():
            print(pc)
        for mon in self.encounter.all_monsters():
            print(mon)

    ##########################################################################
    def close(self):
        xp = 0
        for monster in self.encounter.all_monsters():
            xp + monster.xp
            monster.delete()
        survivors = [_ for _ in self.world.all_pcs() if _.status != status.DEAD]
        for surv in survivors:
            surv.earnXp(xp / len(survivors))

    ##########################################################################
    def combat_round(self):
        self.turn += 1
        print("\nTurn {}".format(self.turn))
        m_targets = [_ for _ in self.encounter.all_monsters() if _.status == status.OK]
        if not m_targets:
            return False
        pcs = self.world.all_pcs()
        pc_targets = [_ for _ in pcs if _.status == status.OK]
        if not pc_targets:
            return False
        # TODO: Initiative
        self.pc_action()
        self.monster_action()

        return True

    ##########################################################################
    def obj_dead(self, obj):
        """ Object is no longer part of the living or unliving """
        print("{} has died".format(obj.name))
        l = Location.objects.get(encounter=self, x=obj.x, y=obj.y)
        l.delete()

    ##########################################################################
    def obj_action(self, obj):
        """ Move towards an enemy until one is range and then attack them """
        moves = obj.movement
        for _ in range(moves):
            reach = obj.get_reach()
            if reach:
                targ_list = self.enemy_in_reach(obj, reach)
            else:
                targ_list = self.enemy_neighbours(obj)
            if targ_list:
                break
            else:
                ne = self.nearest_enemy(obj)
                if not ne:
                    return
                dirn = self.dir_to_move(obj)
                self.move(obj, dirn)
        else:
            return
        targ = random.choice(targ_list)
        dmg = obj.attack(targ)
        if dmg:
            if hasattr(obj, 'equipped_weapon'):
                weap = "with {} ".format(obj.equipped_weapon().name)
            else:
                weap = ""
            print("{} hit {} {}for {} -> {}".format(obj.name, targ.name, weap, dmg, targ.get_status_display()))
            if targ.status == status.DEAD:
                self.obj_dead(targ)
        else:
            print("{} missed {}".format(obj.name, targ.name))

    ##########################################################################
    def pc_action(self):
        for pc in self.world.all_pcs():
            if pc.status == status.OK:
                self.obj_action(pc)
            else:
                print("{} is {}".format(pc.name, pc.get_status_display()))

    ##########################################################################
    def monster_action(self):
        for monster in self.encounter.all_monsters():
            if monster.status == status.OK:
                self.obj_action(monster)
            else:
                print("{} is {}".format(monster.name, monster.get_status_display()))

    ##########################################################################
    def dir_to_move(self, obj):
        ne = self.nearest_enemy(obj)
        if not ne:
            return
        if pow(ne.x - obj.x, 2) > pow(ne.y - obj.y, 2):
            if ne.x > obj.x:
                return 'S'
            if ne.x < obj.x:
                return 'N'
        else:
            if ne.y > obj.y:
                return 'E'
            if ne.y < obj.y:
                return 'W'

    ##########################################################################
    def make_map(self):
        for x in range(self.size_x):
            self.set_location(Wall(), x, 0)
            self.set_location(Wall(), x, self.size_y-1)
        for y in range(self.size_y):
            self.set_location(Wall(), 0, y)
            self.set_location(Wall(), self.size_x, y)
        self.save()

    ##########################################################################
    def __getitem__(self, loc):
        try:
            l = Location.objects.get(encounter=self, x=loc[0], y=loc[1])
            return l.content_object
        except ObjectDoesNotExist:
            return None

    ##########################################################################
    def delete(self, x, y):
        l = Location.objects.filter(encounter=self, x=x, y=y)
        l.delete()

    ##########################################################################
    def change_loc(self, oldx, oldy, newx, newy):
        l = Location.objects.get(encounter=self, x=oldx, y=oldy)
        l.x, l.y = newx, newy
        l.save()
        return l

    ##########################################################################
    def clear(self):
        for l in Location.objects.all():
            l.delete()

    ##########################################################################
    def move(self, obj, drn):
        dirmap = {
                'N': (-1, 0),
                'S': (1, 0),
                'E': (0, 1),
                'W': (0, -1)
                }
        targx = obj.x + dirmap[drn][0]
        targy = obj.y + dirmap[drn][1]
        if self[(targx, targy)]:
            print("{} Movement blocked by {}".format(obj.name, self[(targx, targy)].name))
            return False

        print("{} moved from {},{} {} to {}, {}".format(obj.name, obj.x, obj.y, drn, targx, targy))
        self.change_loc(obj.x, obj.y, targx, targy)
        obj.x, obj.y = targx, targy
        obj.save()
        return True

    ##########################################################################
    def all_animate(self):
        return [o.content_object for o in Location.objects.filter(encounter=self) if o.content_object.animate]

    ##########################################################################
    def __str__(self):
        m = []
        for x in range(0, self.size_x):
            ycol = []
            for y in range(0, self.size_y):
                l = Location.objects.filter(encounter=self, x=x, y=y)
                if not l:
                    ycol.append('.')
                    continue
                elif isinstance(l[0].content_object, Wall):
                    ycol.append('X')
                else:
                    sys.stderr.write("{}, {} = {}".format(x, y, type(l[0].content_object)))
                    ycol.append('?')
            m.append("".join(ycol))
        return "\n".join(m)

    ##########################################################################
    def print_arena(self):
        output = []
        arena = {}
        for i in Location.objects.filter(encounter=self):
            arena[(i.x, i.y)] = i.content_object
        for x in range(self.size_x):
            line = []
            for y in range(self.size_y):
                if (x, y) in arena:
                    line.append("{:4}".format(arena[(x, y)].name[:5]))
                else:
                    line.append("{:4}".format("_"))
            output.append(" ".join(line))
        return "\n".join(output)

    ##########################################################################
    def set_location(self, obj, x, y):
        obj.x = x
        obj.y = y
        obj.save()
        l = Location(encounter=self, x=x, y=y, content_object=obj)
        l.save()


# EOF
