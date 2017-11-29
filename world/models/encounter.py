from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from monster.models import Monster, MonsterState
from character.models import Character
from . import World
from .map_bits import Wall
from utils import roll
import math
import random
import sys


##############################################################################
class Location(models.Model):
    arena = models.ForeignKey('Encounter', blank=True)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        try:
            return "{} at {}, {}".format(self.content_object.name, self.x, self.y)
        except AttributeError:
            return "Unknown at {}, {}".format(self.x, self.y)


##############################################################################
class Encounter(models.Model):
    MONSTER = 'M'
    PC = 'P'

    world = models.ForeignKey(World)
    turn = models.IntegerField(default=0)
    arena_x = models.IntegerField(default=0)
    arena_y = models.IntegerField(default=0)
    monsters = models.ManyToManyField(MonsterState, blank=True)
    pcs = models.ManyToManyField(Character, blank=True)
    monster_types = models.ManyToManyField(Monster, blank=True)

    ##########################################################################
    def __str__(self):
        mons = []
        for m in self.monster_types.all().distinct():
            mons.append("{}".format(m.name))

        return "Encounter with {}".format(", ".join(mons))

    ##########################################################################
    def make_map(self):
        for x in range(self.arena_x):
            self.set_location(Wall(), x, 0)
            self.set_location(Wall(), x, self.arena_y-1)
        for y in range(self.arena_y):
            self.set_location(Wall(), 0, y)
            self.set_location(Wall(), self.arena_x, y)
        self.save()

    ##########################################################################
    def map_repr(self):
        m = []
        for x in range(0, self.arena_x):
            ycol = []
            for y in range(0, self.arena_y):
                l = Location.objects.filter(arena=self, x=x, y=y)
                if not l:
                    ycol.append('.')
                    continue
                elif isinstance(l[0].content_object, Wall):
                    ycol.append('X')
                else:
                    sys.stderr.write("{}, {} = {}".format(x, y, type(l[0].content_object)))
                    ycol.append('?')
            m.append("".join(ycol))
        return m

    ##########################################################################
    def add_monster_type(self, monstername, number=0):
        m = Monster.objects.get(name=monstername)
        self.monster_types.add(m)
        self.save()
        num = number if number else roll(m.numappearing)
        for _ in range(num):
            ms = MonsterState(monster=m)
            ms.name = "{}{}".format(m.name, _)
            ms.save()
            self.monsters.add(ms)
        self.save()

    ##########################################################################
    def place_pcs(self):
        """ Put all PCs in this world in the arena clustered around the middle """
        for pc in Character.objects.filter(world=self.world):
            x = int(self.arena_x / 2)
            y = int(self.arena_y / 2)
            while Location.objects.filter(arena=self, x=x, y=y):
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.set_location(pc, x, y)
            pc.x = x
            pc.y = y
            pc.save()
            self.pcs.add(pc)

    ##########################################################################
    def place_monsters(self):
        for monster in self.monsters.all():
            x = random.randint(0, self.arena_x-1)
            y = random.randint(0, self.arena_y-1)
            while Location.objects.filter(arena=self, x=x, y=y):
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.set_location(monster, x, y)
            monster.x = x
            monster.y = y
            monster.save()

    ##########################################################################
    def print_arena(self, out=sys.stdout):
        arena = {}
        for i in Location.objects.filter(arena=self):
            arena[(i.x, i.y)] = i.content_object
        for x in range(self.arena_x):
            for y in range(self.arena_y):
                if (x, y) in arena:
                    out.write("{:4} ".format(arena[(x, y)].name[:5]))
                else:
                    out.write("{:4} ".format("_"))
            out.write("\n")
        out.write("\n")

    ##########################################################################
    def neighbours(self, obj):
        assert obj.x >= 0
        assert obj.y >= 0
        arena = {}
        for i in Location.objects.filter(arena=self):
            arena[(i.x, i.y)] = i.content_object
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
    def set_location(self, obj, x, y):
        obj.x = x
        obj.y = y
        obj.save()
        l = Location(arena=self, x=x, y=y, content_object=obj)
        l.save()

    ##########################################################################
    def enemy_neighbours(self, obj):
        """ Return a list of valid targets for obj (PC or Monster)"""
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        ns = self.neighbours(obj)
        badns = []
        for n in ns:
            if self.objtype(n) == self.PC and enemy == self.PC and n.status == Character.OK:
                badns.append(n)
            if self.objtype(n) == self.MONSTER and enemy == self.MONSTER and n.status == MonsterState.OK:
                badns.append(n)
        return badns

    ##########################################################################
    def enemy_in_reach(self, obj, reach):
        enemy = self.PC if self.objtype(obj) == self.MONSTER else self.MONSTER
        in_reach = set()
        if enemy == self.PC:
            targets = [_ for _ in self.pcs.all() if _.status == Character.OK]
        else:
            targets = [_ for _ in self.monsters.all() if _.status == MonsterState.OK]
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
            targets = [_ for _ in self.pcs.all() if _.status == Character.OK]
        else:
            targets = [_ for _ in self.monsters.all() if _.status == MonsterState.OK]
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
        for pc in self.pcs.all():
            print(pc)
        for mon in self.monsters.all():
            print(mon)

    ##########################################################################
    def close(self):
        xp = 0
        for monster in self.monsters.all():
            xp + monster.xp
            monster.delete()
        survivors = [_ for _ in self.pcs.exclude(status=Character.DEAD)]
        for surv in survivors:
            surv.earnXp(xp / len(survivors))

    ##########################################################################
    def combat_round(self):
        self.turn += 1
        print("\nTurn {}".format(self.turn))
        m_targets = [_ for _ in self.monsters.all() if _.status == MonsterState.OK]
        if not m_targets:
            return False
        pcs = self.pcs.all()
        pc_targets = [_ for _ in pcs if _.status == Character.OK]
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
        l = Location.objects.filter(arena=self, x=obj.x, y=obj.y)
        l.delete()

    ##########################################################################
    def obj_attack(self, obj):
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
                self.move(obj)
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
            if targ.status == MonsterState.DEAD:
                self.obj_dead(targ)
        else:
            print("{} missed {}".format(obj.name, targ.name))

    ##########################################################################
    def pc_attack(self):
        for pc in Character.objects.filter(world=self.world):
            if pc.status == Character.OK:
                self.obj_attack(pc)
            else:
                print("{} is {}".format(pc.name, pc.get_status_display()))

    ##########################################################################
    def monster_attack(self):
        for monster in self.monsters.all():
            if monster.status == MonsterState.OK:
                self.obj_attack(monster)
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
    def move(self, obj):
        ne = self.nearest_enemy(obj)
        if not ne:
            return
        d = self.dir_to_move(obj)
        for delta in [0, 1, -1]:
            if d == 'N':
                targx = obj.x - 1
                targy = obj.y + delta
            elif d == 'S':
                targx = obj.x + 1
                targy = obj.y + delta
            elif d == 'E':
                targx = obj.x + delta
                targy = obj.y + 1
            elif d == 'W':
                targx = obj.x + delta
                targy = obj.y - 1
            if Location.objects.filter(arena=self, x=targx, y=targy):
                continue
            break
        else:
            print("{} Movement toward {} blocked by {}".format(obj.name, ne.name, Location.objects.get(arena=self, x=targx, y=targy).content_object.name))
            return

        print("{} moved from {},{} {} to {}, {} (Target {} @ {},{})".format(obj.name, obj.x, obj.y, d, targx, targy, ne.name, ne.x, ne.y))
        l = Location.objects.get(arena=self, x=obj.x, y=obj.y)
        l.x = targx
        l.y = targy
        l.save()
        obj.x = targx
        obj.y = targy
        obj.save()

# EOF
