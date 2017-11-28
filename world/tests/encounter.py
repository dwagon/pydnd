from django.test import TestCase
from world.models import World, Encounter, Location
from monster.models import Monster, MonsterState
from character.models import Cleric, Fighter, Character


class test_Encounter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.m = Monster(name='TestOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='1')
        self.m.save()

    def tearDown(self):
        self.m.delete()
        self.w.delete()

    def test_arena(self):
        figgy = Fighter(name='Figgy', world=self.w)
        figgy.generate_stats()
        figgy.save()
        e = Encounter(world=self.w, arena_x=20, arena_y=20)
        e.save()
        e.place_pcs()
        figster = Character.objects.get(world=self.w, name='Figgy')
        self.assertEqual(figster.x, 10)
        self.assertEqual(figster.y, 10)
        l = Location.objects.get(arena=e, x=10, y=10)
        self.assertEqual(l.content_object, figster)

    def test_objtype(self):
        e = Encounter(world=self.w)
        e.save()
        c = Cleric(name='Clarence', world=self.w)
        c.generate_stats()
        c.save()
        ans = e.objtype(c)
        self.assertEqual(ans, Encounter.PC)
        mi = MonsterState(self.m)
        ans = e.objtype(mi)
        self.assertEqual(ans, Encounter.MONSTER)

    def test_place_pcs(self):
        """ Test PC placement in arena """
        for i in range(10):
            f = Fighter(name='F{}'.format(i), world=self.w)
            f.generate_stats()
            f.save()
        e = Encounter(world=self.w, arena_x=20, arena_y=20)
        e.save()
        e.place_pcs()
        arena = {}
        for i in Location.objects.filter(arena=e):
            arena[(i.x, i.y)] = i.content_object
        used_locs = arena.keys()
        pc_locs = [(_.x, _.y) for _ in Character.objects.filter(world=self.w)]
        self.assertEquals(sorted(used_locs), sorted(pc_locs))

    def test_place_monsters(self):
        """ Test Monster placement in arena """
        m = Monster(name='TestManyOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='25')
        m.save()
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestManyOrc')
        e.place_monsters()
        arena = {}
        for i in Location.objects.filter(arena=e):
            arena[(i.x, i.y)] = i.content_object
        used_locs = arena.keys()
        m_locs = [(_.x, _.y) for _ in e.monsters.all()]
        self.assertEquals(sorted(used_locs), sorted(m_locs))

    def test_neighbours(self):
        m = Monster(name='TestSingleOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='1')
        m.save()
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestSingleOrc')
        f = Fighter(name='F', world=self.w)
        f.generate_stats()
        f.x = 5
        f.y = 5
        f.save()
        e.arena[(5, 5)] = f
        e.arena[(6, 5)] = e.monsters[0]
        n = e.neighbours(f)
        self.assertEqual(n, e.monsters)


# EOF
