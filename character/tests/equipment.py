from django.test import TestCase

from character.models import Equipment, Weapons, Armour


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
        self.sword = Weapons(name='long sword', damage='1d8', magic='+1')
        self.sword.save()

    def test_damage(self):
        self.assertEqual(self.sword.damage, '1d8')
        dmg = self.sword.hit()
        self.assertGreaterEqual(dmg, 2)
        self.assertLessEqual(dmg, 9)


##############################################################################
class test_Armour(TestCase):
    def setUp(self):
        self.leather = Armour(name='leather', cost=100, ac_base=2)
        self.leather.save()

    def test_constant(self):
        self.assertEqual(self.leather.cost, 100)
        self.assertEqual(self.leather.magic, '')
# EOF
