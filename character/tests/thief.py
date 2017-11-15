from django.test import TestCase

from character.models import Thief, Weapon, Equipment, Armour


class test_Thief(TestCase):
    def setUp(self):
        self.th = Thief(name='test')
        self.th.save()
        self.sword = Weapon(name='Long Sword', weight=5)
        self.sword.save()
        self.mace = Weapon(name='Mace', weight=7)
        self.mace.save()
        self.spikes = Equipment(name='Iron Spikes', weight=6)
        self.spikes.save()
        self.leather = Armour(name='Leather', weight=6, ac_base=6)
        self.leather.save()
        self.helmet = Armour(name='Helmet', weight=5, ac_modifier=1)
        self.helmet.save()
        self.shield = Armour(name='Shield', weight=4, ac_modifier=2)
        self.shield.save()

    def cleanUp(self):
        self.spikes.delete()
        self.sword.delete()
        self.leather.delete()
        self.helmet.delete()
        self.th.delete()

    def test_hp(self):
        self.assertEqual(self.th.hitdie(), 'd6')
        self.assertGreaterEqual(self.th.hp, 1)
        self.assertLessEqual(self.th.hp, 6)

    def test_thaco(self):
        self.assertEqual(self.th.thaco, 20)

    def test_encumb(self):
        self.assertEqual(self.th.encumbrance, 0)

    def test_stats(self):
        self.assertGreaterEqual(self.th.stat_dex, 3)
        self.assertLessEqual(self.th.stat_dex, 18)

    def test_equip(self):
        self.th.equip(self.sword, ready=True)
        self.th.equip(self.mace)
        self.th.equip(self.spikes)
        self.assertEqual(self.th.encumbrance, 18)
        self.th.equip(self.leather, ready=True)
        w = self.th.equipped_weapon()
        self.assertEqual(w.name, 'Long Sword')

    def test_armour(self):
        self.th.equip(self.leather, ready=True)
        self.th.equip(self.helmet, ready=True)
        self.th.equip(self.spikes)
        a = self.th.equipped_armour()
        self.assertEqual(sorted([_.name for _ in a]), sorted(['Leather', 'Helmet']))

    def test_ac(self):
        self.assertEqual(self.th.ac, 10)
        self.th.equip(self.sword, ready=True)
        self.th.equip(self.spikes)
        self.assertEqual(self.th.ac, 10)
        self.th.equip(self.leather, ready=True)
        self.assertEqual(self.th.ac, 6)
        self.th.equip(self.helmet, ready=True)
        self.assertEqual(self.th.ac, 5)
        self.th.equip(self.shield)
        self.assertEqual(self.th.ac, 5)


# EOF
