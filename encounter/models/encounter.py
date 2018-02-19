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
from message.models import Message
from utils import roll


##############################################################################
class Encounter(models.Model):
    MONSTER = 'M'
    PC = 'P'

    turn = models.IntegerField(default=0)
    phase = models.IntegerField(default=-1)
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
    def find_empty_spot(self, x, y):
        while self[(x, y)]:
            xdelta = random.choice([-1, 0, 1])
            ydelta = random.choice([-1, 0, 1])
            x += xdelta
            y += ydelta
            x = max(0, x)
            y = max(0, y)
            x = min(x, self.size_x)
            y = min(y, self.size_y)
        return x, y

    ##########################################################################
    def place_pcs(self):
        """ Put all PCs in this world in the arena clustered around the middle """
        for pc in self.world.all_pcs():
            x = int(self.size_x / 2)
            y = int(self.size_y / 2)
            x, y = self.find_empty_spot(x, y)
            self.set_location(pc, x, y)

    ##########################################################################
    def place_monsters(self):
        for monster in MonsterState.objects.filter(encounter=self):
            x = random.randint(0, self.size_x-1)
            y = random.randint(0, self.size_y-1)
            x, y = self.find_empty_spot(x, y)
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
        if obj in n:
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
        output = []
        for pc in self.world.all_pcs():
            output.append(str(pc))
        for mon in self.encounter.all_monsters():
            output.append(str(mon))
        return output

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
    def combat_turn(self):
        self.turn += 1
        self.phase = 0
        [_.start_turn() for _ in self.monsters.all() if _.status == status.OK]
        [_.start_turn() for _ in self.world.all_pcs() if _.status == status.OK]
        self.save()

    ##########################################################################
    def combat_phase(self):
        if self.phase < 0 or self.phase > 20:
            self.combat_turn()
        self.phase += 1
        self.save()
        all_pcs = self.world.all_pcs()
        all_monsters = self.monsters.all()
        m_targets = [_ for _ in all_monsters if _.status == status.OK]
        if not m_targets:
            return False
        pc_targets = [_ for _ in all_pcs if _.status == status.OK]
        if not pc_targets:
            return False
        [self.obj_action(_) for _ in all_pcs if _.status == status.OK and self.phase >= _.initiative]
        [self.obj_action(_) for _ in all_monsters if _.status == status.OK and self.phase >= _.initiative]

        return True

    ##########################################################################
    def M(self, msg):
        m = Message(world=self.world, msg=msg)
        m.save()

    ##########################################################################
    def obj_dead(self, obj):
        """ Object is no longer part of the living or unliving """
        self.M("{} has died".format(obj.name))
        loc = self.locations.get(x=obj.x, y=obj.y)
        loc.delete()

    ##########################################################################
    def obj_action(self, obj):
        """ Move towards an enemy until one is range and then attack them """
        reach = obj.get_reach()
        if reach:
            targ_list = self.enemy_in_reach(obj, reach)
        else:
            targ_list = self.enemy_neighbours(obj)

        if not targ_list and obj.moves > 0:
            ne = self.nearest_enemy(obj)
            if ne:
                dirn = self.dir_to_move(obj)
                self.move(obj, dirn)
                obj.moves -= 1
                obj.save()

        if obj.attacks > 0 and targ_list:
            obj.attacks -= 1
            targ = random.choice(targ_list)
            dmg = obj.attack(targ)
            if dmg:
                if hasattr(obj, 'equipped_weapon') and obj.equipped_weapon():
                    weap = "with {} ".format(obj.equipped_weapon().name)
                else:
                    weap = ""
                self.M("{} hit {} {}for {} -> {}".format(obj.name, targ.name, weap, dmg, targ.get_status_display()))
                if targ.status == status.DEAD:
                    self.obj_dead(targ)
            else:
                self.M("{} missed {}".format(obj.name, targ.name))
            obj.save()

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
            loc = self.locations.get(x=loc[0], y=loc[1])
            return loc.content_object
        except ObjectDoesNotExist:
            return None

    ##########################################################################
    def change_loc(self, oldx, oldy, newx, newy):
        loc = self.locations.get(x=oldx, y=oldy)
        loc.x, loc.y = newx, newy
        loc.save()
        return loc

    ##########################################################################
    def clear(self):
        for l in self.locations.all():
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
            self.M("{} Movement blocked by {}".format(obj.name, self[(targx, targy)].name))
            return False

        self.M("{} moved from {},{} {} to {}, {}".format(obj.name, obj.x, obj.y, drn, targx, targy))
        self.change_loc(obj.x, obj.y, targx, targy)
        obj.x, obj.y = targx, targy
        obj.save()
        return True

    ##########################################################################
    def all_animate(self):
        return [o.content_object for o in self.locations.all() if o.content_object.animate]

    ##########################################################################
    def __str__(self):
        m = []
        for x in range(0, self.size_x):
            ycol = []
            for y in range(0, self.size_y):
                loc = self.locations.filter(x=x, y=y)
                if not loc:
                    ycol.append('.')
                    continue
                elif isinstance(loc[0].content_object, Wall):
                    ycol.append('X')
                else:
                    sys.stderr.write("{}, {} = {}".format(x, y, type(loc[0].content_object)))
                    ycol.append('?')
            m.append("".join(ycol))
        return "\n".join(m)

    ##########################################################################
    def set_location(self, obj, x, y):
        obj.x = x
        obj.y = y
        obj.save()
        loc = Location(encounter=self, x=x, y=y, content_object=obj)
        loc.save()

    ##########################################################################
    def delete(self, *args, **kwargs):
        for l in self.locations.all():
            l.delete()
        for m in self.monsters.all():
            m.delete()
        super().delete(*args, **kwargs)


# EOF
