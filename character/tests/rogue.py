from django.test import TestCase

from character.models import Rogue
from equipment.models import Equipment, Weapon, Armour
from encounter.models import Encounter
from monster.models import Monster, MonsterState
from world.models import World
import status


class test_Rogue(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.th = Rogue(world=self.w, name='test', stat_con=9, stat_dex=18)
        self.th.save()
        self.bow = Weapon(name='Test Bow', weight=5, normal_range=5, long_range=10)
        self.bow.save()
        self.mace = Weapon(name='Mace', weight=7)
        self.mace.save()
        self.spikes = Equipment(name='Iron Spikes', weight=6)
        self.spikes.save()
        self.leather = Armour(name='Leather', weight=6)
        self.leather.save()
        self.helmet = Armour(name='Helmet', weight=5)
        self.helmet.save()
        self.shield = Armour(name='Shield', weight=4)
        self.shield.save()

    def cleanUp(self):
        self.spikes.delete()
        self.bow.delete()
        self.leather.delete()
        self.helmet.delete()
        self.th.delete()
        self.w.delete()

    def test_hp(self):
        self.assertEqual(self.th.hitdie(), 'd6')
        self.assertGreaterEqual(self.th.hp, 1)
        self.assertLessEqual(self.th.hp, 6)

    def test_encumb(self):
        self.assertEqual(self.th.encumbrance, 0)

    def test_stats(self):
        self.assertGreaterEqual(self.th.stat_wis, 3)
        self.assertLessEqual(self.th.stat_wis, 18)
        self.assertEqual(self.th.stat_dex, 18)

    def test_ranged(self):
        """ Test ranged combat """
        e = Encounter(world=self.w)
        e.save()
        self.th.equip(self.bow, ready=True)
        self.assertEqual(self.th.get_reach(), (5, 10))
        o = Monster(name='weak_orc', movement=3, ac=20, thaco=20, xp=3)
        o.save()
        oi = MonsterState(encounter=e, monster=o)
        oi.save()
        dmg, dmgcat = self.th.ranged_attack(self.th.equipped_weapon()[0], oi)
        self.assertEqual(dmg, 5)    # 3dmg + 2 missattack

    def test_hurt(self):
        """ Test being hurt - ouch """
        self.th.hp = 9
        self.th.save()
        rc = self.th.hurt(1)
        self.assertEqual(self.th.status, status.OK)
        self.assertTrue(rc)
        rc = self.th.hurt(10)
        self.assertEqual(self.th.status, status.UNCONSCIOUS)
        self.assertFalse(rc)
        rc = self.th.hurt(10)
        self.assertEqual(self.th.status, status.DEAD)
        self.assertFalse(rc)


# EOF
