from django.test import TestCase

from equipment.models import Equipment, Weapon, Armour


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
        self.stick = Weapon(name='test stick', damage='1d4', damage_cat='P')
        self.stick.save()

    def test_damage(self):
        self.assertEqual(self.stick.damage, '1d4')


##############################################################################
class test_Armour(TestCase):
    def setUp(self):
        self.plate = Armour(name='test breastplate', cost="400gp", base_ac=14, armour_categ='M')
        self.plate.save()

    def test_ac(self):
        ac = self.plate.calc_ac(5)
        self.assertEqual(ac, 16)

# EOF
