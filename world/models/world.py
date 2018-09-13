import sys
import status
import random
import math

from monster.models import Monster, MonsterState
from message.models import Message
from django.db import models
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from character.models import Character
from character.models import Character

from .map_bits import Wall
from .location import Location


##############################################################################
class World(models.Model):
    MONSTER = 'M'
    PC = 'P'

    name = models.CharField(max_length=200, unique=True)
    turn = models.IntegerField(default=0)
    phase = models.IntegerField(default=-1)
    size_x = models.IntegerField(default=50)
    size_y = models.IntegerField(default=50)

    ##########################################################################
    def all_pcs(self):
        return Character.objects.filter(world=self)

    ##########################################################################
    def all_monsters(self):
        return MonsterState.objects.filter(world=self)

    ##########################################################################
    def start(self):
        self.place_pcs()
        self.place_monsters()
        tmp = []
        for m in self.monsterstate_set.all():
            tmp.append((m.initiative(), m))
        for p in self.pcs.all():
            tmp.append((p.initiative(), p))
        for num, obj in enumerate([_[1] for _ in sorted(tmp, key=lambda x: x[0])]):
            obj.initseq = num
            obj.save()
        self.start_turn()

    ##########################################################################
    def all_monsters(self):
        return MonsterState.objects.filter(world=self)

    ##########################################################################
    def add_monster_type(self, monstername, number=1):
        m = Monster.objects.get(name=monstername)
        for _ in range(number):
            ms = MonsterState(world=self, monster=m)
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
        for pc in self.all_pcs():
            x = int(self.size_x / 2)
            y = int(self.size_y / 2)
            x, y = self.find_empty_spot(x, y)
            self.set_location(pc, x, y)

    ##########################################################################
    def place_monsters(self):
        for monster in MonsterState.objects.filter(world=self):
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
            targets = [_ for _ in self.all_pcs() if _.status == status.OK]
        else:
            targets = [_ for _ in self.monsterstate_set.all() if _.status == status.OK]
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
            targets = [_ for _ in self.all_pcs() if _.status == status.OK]
        else:
            targets = [_ for _ in self.monsterstate_set.all() if _.status == status.OK]
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
        for pc in self.all_pcs():
            output.append(str(pc))
        for mon in self.all_monsters():
            output.append(str(mon))
        return output

    ##########################################################################
    def close(self):
        xp = 0
        for monster in self.all_monsters():
            xp + monster.xp
            monster.delete()
        survivors = [_ for _ in self.all_pcs() if _.status != status.DEAD]
        for surv in survivors:
            surv.earnXp(xp / len(survivors))

    ##########################################################################
    def start_turn(self):
        self.turn += 1
        self.phase = 0
        [_.start_turn() for _ in self.monsterstate_set.all() if _.status == status.OK]
        [_.start_turn() for _ in self.all_pcs() if _.status == status.OK]
        self.save()

    ##########################################################################
    def combat_phase(self):
        mon = MonsterState.objects.filter(initseq=self.phase, world=self)
        if mon:
            mon[0].take_action()
            self.phase += 1
            self.save()
            return mon[0]

        pc = Character.objects.filter(initseq=self.phase, world=self)
        if pc:
            pc[0].take_action()
            self.phase += 1
            self.save()
            return pc[0]

        self.start_turn()

    ##########################################################################
    def M(self, msg):
        m = Message(world=self, msg=msg)
        m.save()

    ##########################################################################
    def obj_dead(self, obj):
        """ Object is no longer part of the living or unliving """
        self.M("{} has died".format(obj.name))
        loc = self.locations.get(x=obj.x, y=obj.y)
        loc.delete()

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
        loc = Location(world=self, x=x, y=y, content_object=obj)
        loc.save()

    ##########################################################################
    def delete(self, *args, **kwargs):
        for l in self.locations.all():
            l.delete()
        for m in self.monsterstate_set.all():
            m.delete()
        super().delete(*args, **kwargs)


# EOF
