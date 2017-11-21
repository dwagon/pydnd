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


# EOF
