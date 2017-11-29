from django.test import TestCase
from world.models import World, Encounter, Location
from monster.models import Monster, MonsterState
from character.models import Cleric, Fighter, Character, Thief


##############################################################################
##############################################################################
class test_Encounter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.orc = Monster(name='TestOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='1')
        self.orc.save()
        self.dualorc = Monster(name='TestDualOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='2')
        self.dualorc.save()
        self.fighter = Fighter(name='Fig', world=self.w)
        self.fighter.generate_stats()
        self.fighter.save()
        self.thief = Thief(name='Thf', world=self.w)
        self.thief.generate_stats()
        self.thief.save()

    ##########################################################################
    def tearDown(self):
        self.orc.delete()
        self.w.delete()
        self.dualorc.delete()
        self.fighter.delete()
        self.thief.delete()

    ##########################################################################
    def test_place_single_pc(self):
        """ Test placing a single character that it goes in the middle """
        # Put thief in another world to stop interfering with placement
        nw = World()
        nw.save()
        self.thief.world = nw
        self.thief.save()
        e = Encounter(world=self.w, arena_x=20, arena_y=20)
        e.save()
        e.place_pcs()
        self.thief.save()
        figster = Character.objects.get(world=self.w, name='Fig')
        self.assertEqual(figster.x, 10)
        self.assertEqual(figster.y, 10)
        l = Location.objects.get(arena=e, x=10, y=10)
        self.assertEqual(l.content_object, figster)
        nw.delete()

    ##########################################################################
    def test_objtype(self):
        e = Encounter(world=self.w)
        e.save()
        c = Cleric(name='Clarence', world=self.w)
        c.generate_stats()
        c.save()
        ans = e.objtype(c)
        self.assertEqual(ans, Encounter.PC)
        mi = MonsterState(self.orc)
        ans = e.objtype(mi)
        self.assertEqual(ans, Encounter.MONSTER)

    ##########################################################################
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

    ##########################################################################
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

    ##########################################################################
    def test_set_location(self):
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.set_location(self.fighter, 3, 7)
        self.assertEqual(self.fighter.x, 3)
        self.assertEqual(self.fighter.y, 7)
        l = Location.objects.get(arena=e, x=3, y=7)
        self.assertEqual(l.content_object, self.fighter)

    ##########################################################################
    def test_neighbours(self):
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestDualOrc')
        m1, m2 = e.monsters.all()
        e.set_location(self.fighter, 5, 5)
        e.set_location(m1, 6, 5)    # Neighbour
        e.set_location(m2, 9, 9)    # Not neighbour
        n = e.neighbours(self.fighter)
        self.assertEqual(n, [m1])

    ##########################################################################
    def test_enemy_neighbours(self):
        """ Test 'enemy_neighbours' function """
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestDualOrc')
        m1, m2 = e.monsters.all()
        e.set_location(self.fighter, 5, 5)
        e.set_location(self.thief, 5, 6)
        e.set_location(m1, 6, 5)    # Neighbour
        e.set_location(m2, 9, 9)    # Not neighbour
        n = e.enemy_neighbours(self.fighter)
        self.assertEqual(n, [m1])
        n = e.enemy_neighbours(m1)
        self.assertEqual(sorted(n), sorted([self.fighter, self.thief]))

    ##########################################################################
    def test_enemy_in_reach(self):
        """ Test 'enemy_in_reach' function """
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestDualOrc')
        e.place_pcs()
        m1, m2 = e.monsters.all()
        e.set_location(self.fighter, 0, 0)
        e.set_location(self.thief, 5, 0)
        e.set_location(m1, 5, 5)    # In Reach
        e.set_location(m2, 5, 9)    # Not in reach
        n = e.enemy_in_reach(self.thief, 7)
        self.assertEqual(n, [m1])
        n = e.enemy_in_reach(m1, 7)
        self.assertEqual(n, [self.thief])

    ##########################################################################
    def test_nearest_enemy(self):
        """ Test 'nearest_enemy' function """
        e = Encounter(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestDualOrc')
        e.place_pcs()
        m1, m2 = e.monsters.all()
        e.set_location(self.thief, 5, 0)
        e.set_location(self.fighter, 0, 0)
        e.set_location(m1, 5, 5)
        e.set_location(m2, 5, 9)
        n = e.nearest_enemy(self.thief)
        self.assertEqual(n, m1)
        n = e.nearest_enemy(m1)
        self.assertEqual(n, self.thief)

# EOF
