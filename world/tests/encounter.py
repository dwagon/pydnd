from django.test import TestCase
from world.models import World, Encounter
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
        e = Encounter(world=self.w, monstername='TestOrc', arenasize=20)
        self.assertEqual(e.arenasize, 20)
        e.place_pcs()
        figster = Character.objects.get(world=self.w, name='Figgy')
        self.assertEqual(figster.x, 10)
        self.assertEqual(figster.y, 10)
        self.assertEqual(e.arena[(10, 10)], figster)

    def test_objtype(self):
        e = Encounter(world=self.w, monstername='TestOrc')
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
        e = Encounter(world=self.w, monstername='TestOrc', arenasize=20)
        e.place_pcs()
        used_locs = e.arena.keys()
        pc_locs = [(_.x, _.y) for _ in Character.objects.filter(world=self.w)]
        self.assertEquals(sorted(used_locs), sorted(pc_locs))

    def test_place_monsters(self):
        """ Test Monster placement in arena """
        m = Monster(name='TestManyOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='25')
        m.save()
        e = Encounter(world=self.w, monstername='TestManyOrc', arenasize=10)
        e.place_monsters()
        used_locs = e.arena.keys()
        m_locs = [(_.x, _.y) for _ in e.monsters]
        self.assertEquals(sorted(used_locs), sorted(m_locs))

# EOF
