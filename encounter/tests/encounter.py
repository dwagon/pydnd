from django.test import TestCase
from world.models import World
from encounter.models import Encounter
from monster.models import Monster, MonsterState
from character.models import Cleric, Fighter, Character, Rogue


##############################################################################
##############################################################################
class test_Encounter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.orc = Monster(name="Orc", align="CE", size="M", ac=13, hitdie="2d8 + 6", speed=30, stat_str=16, stat_dex=12, stat_con=16, stat_int=7, stat_wis=11, stat_cha=10, challenge="1/2")
        self.orc.save()

    ##########################################################################
    def makeFighter(self):
        self.fighter = Fighter(world=self.w, name='Fig')
        self.fighter.save()

    ##########################################################################
    def makeThief(self):
        self.rogue = Rogue(world=self.w, name='Thf')
        self.rogue.save()

    ##########################################################################
    def tearDown(self):
        if hasattr(self, 'rogue'):
            self.rogue.delete()
        if hasattr(self, 'fighter'):
            self.fighter.delete()
        self.orc.delete()
        self.w.delete()

    ##########################################################################
    def test_place_single_pc(self):
        """ Test placing a single character that it goes in the middle """
        e = Encounter(world=self.w, size_x=20, size_y=20)
        e.save()
        self.makeFighter()
        e.place_pcs()
        figster = Character.objects.get(name='Fig')
        self.assertEqual(figster.x, 10)
        self.assertEqual(figster.y, 10)
        loc = e[(10, 10)]
        self.assertEqual(loc, figster)

    ##########################################################################
    def test_objtype(self):
        e = Encounter(world=self.w)
        e.save()
        c = Cleric(world=self.w, name='Clarence')
        c.save()
        ans = e.objtype(c)
        self.assertEqual(ans, Encounter.PC)
        mi = MonsterState(encounter=e, monster=self.orc)
        ans = e.objtype(mi)
        self.assertEqual(ans, Encounter.MONSTER)

    ##########################################################################
    def test_place_pcs(self):
        """ Test PC placement in arena """
        for i in range(10):
            f = Fighter(world=self.w, name='F{}'.format(i))
            f.save()
        e = Encounter(world=self.w, size_x=20, size_y=20)
        e.save()
        e.place_pcs()
        used_locs = set()
        for i in e.all_animate():
            used_locs.add((i.x, i.y))
        pc_locs = set([(_.x, _.y) for _ in Character.objects.all()])
        self.assertEquals(len(pc_locs), 10)
        self.assertEquals(used_locs, pc_locs)

    ##########################################################################
    def test_place_monsters(self):
        """ Test Monster placement in arena """
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        e.add_monster_type('Orc', 25)
        e.place_monsters()
        used_locs = set()
        for i in e.all_animate():
            if isinstance(i, MonsterState):
                used_locs.add((i.x, i.y))

        m_locs = set([(_.x, _.y) for _ in MonsterState.objects.filter(encounter=e)])
        self.assertEquals(used_locs, m_locs)

    ##########################################################################
    def test_set_location(self):
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        self.makeFighter()
        e.set_location(self.fighter, 3, 7)
        self.assertEqual(self.fighter.x, 3)
        self.assertEqual(self.fighter.y, 7)
        loc = e[(3, 7)]
        self.assertEqual(loc, self.fighter)

    ##########################################################################
    def test_neighbours(self):
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        self.makeFighter()
        self.makeThief()
        e.add_monster_type('Orc', 2)
        m1, m2 = MonsterState.objects.filter(encounter=e)
        e.set_location(self.fighter, 5, 5)
        e.set_location(self.rogue, 4, 4)
        e.set_location(m1, 6, 5)    # Neighbour
        e.set_location(m2, 9, 9)    # Not neighbour
        n = e.neighbours(self.fighter)
        self.assertEqual(set(n), set([self.rogue, m1]))

    ##########################################################################
    def test_enemy_neighbours(self):
        """ Test 'enemy_neighbours' function """
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        self.makeFighter()
        self.makeThief()
        e.add_monster_type('Orc', 2)
        m1, m2 = MonsterState.objects.filter(encounter=e)
        e.set_location(self.fighter, 5, 5)
        e.set_location(self.rogue, 5, 6)
        e.set_location(m1, 6, 5)    # Neighbour
        e.set_location(m2, 9, 9)    # Not neighbour
        n = e.enemy_neighbours(self.fighter)
        self.assertEqual(n, [m1])
        n = e.enemy_neighbours(m1)
        self.assertEqual(sorted(n), sorted([self.fighter, self.rogue]))

    ##########################################################################
    def test_enemy_in_reach(self):
        """ Test 'enemy_in_reach' function """
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        self.makeFighter()
        self.makeThief()
        e.add_monster_type('Orc', 2)
        e.place_pcs()
        m1, m2 = MonsterState.objects.filter(encounter=e)
        e.set_location(self.fighter, 0, 0)
        e.set_location(self.rogue, 5, 0)
        e.set_location(m1, 5, 5)    # In Reach
        e.set_location(m2, 5, 9)    # Not in reach
        n = e.enemy_in_reach(self.rogue, 7)
        self.assertEqual(n, [m1])
        n = e.enemy_in_reach(m1, 7)
        self.assertEqual(n, [self.rogue])

    ##########################################################################
    def test_nearest_enemy(self):
        """ Test 'nearest_enemy' function """
        e = Encounter(world=self.w, size_x=10, size_y=10)
        e.save()
        self.makeFighter()
        self.makeThief()
        e.add_monster_type('Orc', 2)
        e.place_pcs()
        m1, m2 = MonsterState.objects.filter(encounter=e)
        e.set_location(self.rogue, 5, 0)
        e.set_location(self.fighter, 0, 0)
        e.set_location(m1, 5, 5)
        e.set_location(m2, 5, 9)
        n = e.nearest_enemy(self.rogue)
        self.assertEqual(n, m1)
        n = e.nearest_enemy(m1)
        self.assertEqual(n, self.rogue)

# EOF
