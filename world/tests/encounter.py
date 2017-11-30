from django.test import TestCase
from world.models import World, Encounter
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
        self.fighter.save()
        self.thief = Thief(name='Thf', world=self.w)
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
        e = Encounter.create(world=self.w, arena_x=20, arena_y=20)
        e.save()
        e.place_pcs()
        self.thief.save()
        figster = Character.objects.get(world=self.w, name='Fig')
        self.assertEqual(figster.x, 10)
        self.assertEqual(figster.y, 10)
        l = e.arena[(10, 10)]
        self.assertEqual(l, figster)
        nw.delete()

    ##########################################################################
    def test_objtype(self):
        e = Encounter.create(world=self.w)
        e.save()
        c = Cleric(name='Clarence', world=self.w)
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
            f.save()
        e = Encounter.create(world=self.w, arena_x=20, arena_y=20)
        e.save()
        e.place_pcs()
        used_locs = set()
        for i in e.arena.all_animate():
            used_locs.add((i.x, i.y))
        pc_locs = set([(_.x, _.y) for _ in Character.objects.filter(world=self.w)])
        self.assertEquals(used_locs, pc_locs)

    ##########################################################################
    def test_place_monsters(self):
        """ Test Monster placement in arena """
        m = Monster(name='TestManyOrc', ac=19, xp=5, thaco=19, movement=3, numappearing='25')
        m.save()
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.add_monster_type('TestManyOrc')
        e.place_monsters()
        used_locs = set()
        for i in e.arena.all_animate():
            used_locs.add((i.x, i.y))
        m_locs = set([(_.x, _.y) for _ in e.monsters.all()])
        self.assertEquals(used_locs, m_locs)

    ##########################################################################
    def test_set_location(self):
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
        e.save()
        e.set_location(self.fighter, 3, 7)
        self.assertEqual(self.fighter.x, 3)
        self.assertEqual(self.fighter.y, 7)
        l = e.arena[(3, 7)]
        self.assertEqual(l, self.fighter)

    ##########################################################################
    def test_neighbours(self):
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
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
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
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
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
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
        e = Encounter.create(world=self.w, arena_x=10, arena_y=10)
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
