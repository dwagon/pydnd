from django.test import TestCase

from equipment.models import Equipment, Weapon


##############################################################################
class test_Equipment(TestCase):
    def setUp(self):
        self.spikes = Equipment(name='iron spikes', cost="1gp", weight=5)
        self.spikes.save()

    def test_weight(self):
        self.assertEqual(self.spikes.weight, 5)
        self.assertEqual(self.spikes.cost, "1gp")


##############################################################################
class test_Weapons(TestCase):
    def setUp(self):
        self.sword = Weapon(name='long sword', damage='1d8', damage_cat='S')
        self.sword.save()

    def test_damage(self):
        self.assertEqual(self.sword.damage, '1d8')

# EOF
