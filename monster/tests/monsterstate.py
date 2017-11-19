from django.test import TestCase
from monster.models import Monster, MonsterState
from character.models import Armour, Mage
from world.models import World


class test_MonsterState(TestCase):
    def setUp(self):
        self.orc = Monster(name='orc', movement=3, ac=3, thaco=19, xp=3)
        self.orc.save()
        self.ms = MonsterState(self.orc)
        self.ms.save()
        self.world = World()
        self.world.save()

    def tearDown(self):
        self.ms.delete()
        self.orc.delete()
        self.world.delete()

    def test_movement(self):
        self.assertEqual(self.orc.movement, 3)

    def test_hit(self):
        e = Armour(name='useless', ac_base=30)
        e.save()
        c = Mage(name='victim', world=self.world)
        c.generate_stats()
        c.save()
        c.equip(e, ready=True)
        hit = self.ms.hit(c)
        self.assertTrue(hit)

    def test_miss(self):
        e = Armour(name='impervious', ac_base=-30)
        e.save()
        c = Mage(name='victim', world=self.world)
        c.generate_stats()
        c.save()
        c.equip(e, ready=True)
        c.ac = -30    # Guarantee miss
        c.save()
        hit = self.ms.hit(c)
        self.assertFalse(hit)

# EOF
