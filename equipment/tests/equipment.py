from django.test import TestCase

from equipment.models import Equipment, Weapon


##############################################################################
class test_Equipment(TestCase):
    def setUp(self):
        self.spikes = Equipment(name='iron spikes', cost=1, weight=5)
        self.spikes.save()

    def test_weight(self):
        self.assertEqual(self.spikes.weight, 5)
        self.assertEqual(self.spikes.cost, 1)


##############################################################################
class test_Weapons(TestCase):
    def setUp(self):
        self.sword = Weapon(name='long sword', damage='1d8', magic='+1')
        self.sword.save()

    def test_damage(self):
        self.assertEqual(self.sword.damage, '1d8')
        dmg = self.sword.weapon_dmg()
        self.assertGreaterEqual(dmg, 2)
        self.assertLessEqual(dmg, 9)

# EOF
