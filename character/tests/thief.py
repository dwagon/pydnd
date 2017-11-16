from django.test import TestCase

from character.models import Thief, Weapon, Equipment, Armour, Character


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

    def test_hurt(self):
        """ Test being hurt - ouch """
        self.th.hp = 9
        self.th.save()
        rc = self.th.hurt(1)
        self.assertEqual(self.th.status, Character.OK)
        self.assertTrue(rc)
        rc = self.th.hurt(10)
        self.assertEqual(self.th.status, Character.UNCONSCIOUS)
        self.assertFalse(rc)
        rc = self.th.hurt(10)
        self.assertEqual(self.th.status, Character.DEAD)
        self.assertFalse(rc)


# EOF
