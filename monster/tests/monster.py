from django.test import TestCase
from monster.models import Monster
from character.models import Armour, Mage
from world.models import World


class test_Monster(TestCase):
    def setUp(self):
        self.orc = Monster(name='orc', movement=3, ac=3, thaco=19, xp=3, damage='1d4')
        self.orc.save()
        self.world = World()
        self.world.save()

    def tearDown(self):
        self.world.delete()

    def test_movement(self):
        self.assertEqual(self.orc.movement, 3)

    def test_attack(self):
        e = Armour(name='useless', ac_base=30)
        e.save()
        c = Mage(name='victim', world=self.world, max_hp=10, hp=10)
        c.save()
        c.equip(e, ready=True)
        dmg = self.orc.attack(c)
        self.assertGreaterEqual(dmg, 1)
        self.assertLessEqual(dmg, 4)
        self.assertEqual(c.hp, 10 - dmg)

    def test_hit(self):
        e = Armour(name='useless', ac_base=30)
        e.save()
        c = Mage(name='victim', world=self.world)
        c.save()
        c.equip(e, ready=True)
        hit = self.orc.hit(c)
        self.assertTrue(hit)

    def test_miss(self):
        e = Armour(name='impervious', ac_base=-30)
        e.save()
        c = Mage(name='victim', world=self.world)
        c.save()
        c.equip(e, ready=True)
        c.ac = -30    # Guarantee miss
        c.save()
        hit = self.orc.hit(c)
        self.assertFalse(hit)

# EOF
