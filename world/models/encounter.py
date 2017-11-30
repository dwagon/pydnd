from django.db import models
from monster.models import Monster, MonsterState
from character.models import Character
from .world import World
from .arena import Arena
from utils import roll
import status
import math
import random


##############################################################################
class Encounter(models.Model):
    MONSTER = 'M'
    PC = 'P'

    world = models.ForeignKey(World)
    arena = models.OneToOneField(Arena, on_delete=models.CASCADE)
    turn = models.IntegerField(default=0)
    monsters = models.ManyToManyField(MonsterState, blank=True)
    pcs = models.ManyToManyField(Character, blank=True)
    monster_types = models.ManyToManyField(Monster, blank=True)

    ##########################################################################
    @classmethod
    def create(cls, *args, **kwargs):
        ar_kwargs = {}
        if 'arena_x' in kwargs:
            arena_x = kwargs['arena_x']
            del kwargs['arena_x']
            ar_kwargs['arena_x'] = arena_x
        if 'arena_y' in kwargs:
            arena_y = kwargs['arena_y']
            del kwargs['arena_y']
            ar_kwargs['arena_y'] = arena_y
        enc = cls(*args, **kwargs)
        ar_kwargs['world'] = enc.world
        ar = Arena(**ar_kwargs)
        ar.save()
        enc.arena = ar
        return enc

    ##########################################################################
    def print_arena(self):
        return self.arena.print_arena()

    ##########################################################################
    def set_location(self, obj, x, y):
        return self.arena.set_location(obj, x, y)

    ##########################################################################
    def __str__(self):
        mons = []
        for m in self.monster_types.all().distinct():
            mons.append("{}".format(m.name))

        return "Encounter with {}".format(", ".join(mons))

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
            x = int(self.arena.arena_x / 2)
            y = int(self.arena.arena_y / 2)
            while self.arena[(x, y)]:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.arena.set_location(pc, x, y)
            pc.x = x
            pc.y = y
            pc.save()
            self.pcs.add(pc)

    ##########################################################################
    def place_monsters(self):
        for monster in self.monsters.all():
            x = random.randint(0, self.arena.arena_x-1)
            y = random.randint(0, self.arena.arena_y-1)
            while self.arena[(x, y)]:
                xdelta = random.choice([-1, 0, 1])
                ydelta = random.choice([-1, 0, 1])
                x += xdelta
                y += ydelta
            self.arena.set_location(monster, x, y)
            monster.x = x
            monster.y = y
            monster.save()

    ##########################################################################
    def neighbours(self, obj):
        assert obj.x >= 0
        assert obj.y >= 0
        arena = {}
        for i in self.arena.all_animate():
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
            targets = [_ for _ in self.pcs.all() if _.status == status.OK]
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
            targets = [_ for _ in self.pcs.all() if _.status == status.OK]
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
        survivors = [_ for _ in self.pcs.exclude(status=status.DEAD)]
        for surv in survivors:
            surv.earnXp(xp / len(survivors))

    ##########################################################################
    def combat_round(self):
        self.turn += 1
        print("\nTurn {}".format(self.turn))
        m_targets = [_ for _ in self.monsters.all() if _.status == status.OK]
        if not m_targets:
            return False
        pcs = self.pcs.all()
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
        self.arena.delete(obj.x, obj.y)

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
        for pc in self.pcs.all():
            if pc.status == status.OK:
                self.obj_action(pc)
            else:
                print("{} is {}".format(pc.name, pc.get_status_display()))

    ##########################################################################
    def monster_action(self):
        for monster in self.monsters.all():
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
    def move(self, obj, drn):
        dirmap = {
                'N': (-1, 0),
                'S': (1, 0),
                'E': (0, 1),
                'W': (0, -1)
                }
        targx = obj.x + dirmap[drn][0]
        targy = obj.y + dirmap[drn][1]
        if self.arena[(targx, targy)]:
            print("{} Movement blocked by {}".format(obj.name, self.arena[(targx, targy)].name))
            return

        print("{} moved from {},{} {} to {}, {}".format(obj.name, obj.x, obj.y, drn, targx, targy))
        self.arena.move(obj.x, obj.y, targx, targy)
        obj.x, obj.y = targx, targy
        obj.save()

# EOF
