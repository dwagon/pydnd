from django.test import TestCase

from character.models import Fighter
from equipment.models import Equipment, Weapon, Armour
from monster.models import Monster, MonsterState
from world.models import World


class test_Fighter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.fg = Fighter(world=self.w, name='test', stat_con=9, stat_dex=9)
        self.fg.save()
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
        self.fg.delete()
        self.w.delete()

    def test_hp(self):
        self.assertEqual(self.fg.hitdie(), 'd10')
        self.assertGreaterEqual(self.fg.hp, 1)
        self.assertLessEqual(self.fg.hp, 10)

    def test_thaco(self):
        self.assertEqual(self.fg.thaco, 20)

    def test_stats(self):
        self.assertGreaterEqual(self.fg.stat_str, 3)
        self.assertLessEqual(self.fg.stat_str, 18)

    def test_equip(self):
        self.fg.equip(self.sword, ready=True)
        self.fg.equip(self.mace)
        self.fg.equip(self.spikes)
        self.assertEqual(self.fg.encumbrance, 18)
        self.fg.equip(self.leather, ready=True)
        w = self.fg.equipped_weapon()
        self.assertEqual(w.name, 'Long Sword')

    def test_unequiped(self):
        w = self.fg.equipped_weapon()
        self.assertFalse(w)

    def test_armour(self):
        self.fg.equip(self.leather, ready=True)
        self.fg.equip(self.helmet, ready=True)
        self.fg.equip(self.spikes)
        a = self.fg.equipped_armour()
        self.assertEqual(sorted([_.name for _ in a]), sorted(['Leather', 'Helmet']))

    def test_naked(self):
        a = self.fg.equipped_armour()
        self.assertFalse(a)

    def test_ac(self):
        self.assertEqual(self.fg.ac, 10)
        self.fg.equip(self.sword, ready=True)
        self.fg.equip(self.spikes)
        self.assertEqual(self.fg.ac, 10)
        self.fg.equip(self.leather, ready=True)
        self.assertEqual(self.fg.ac, 6)
        self.fg.equip(self.helmet, ready=True)
        self.assertEqual(self.fg.ac, 5)
        self.fg.equip(self.shield)
        self.assertEqual(self.fg.ac, 5)

    def test_hit(self):
        o = Monster(name='weak_orc', movement=3, ac=20, thaco=20, xp=3)
        o.save()
        oi = MonsterState(world=self.w, monster=o)
        oi.save()
        rc = self.fg.attack(oi)
        self.assertTrue(rc)
        oi.delete()
        o.delete()

    def test_miss(self):
        o = Monster(name='strong_orc', movement=3, ac=-20, thaco=20, xp=6)
        o.save()
        oi = MonsterState(world=self.w, monster=o)
        oi.save()
        rc = self.fg.attack(oi)
        self.assertFalse(rc)
        oi.delete()
        o.delete()

    def test_strength(self):
        fg = Fighter(world=self.w, name='test', stat_str=18)
        fg.save()
        ss = Weapon(name='Short Sword', weight=1, damage='1')
        ss.save()
        fg.equip(ss, ready=True)
        o = Monster(name='weak_orc', movement=3, ac=20, thaco=20, xp=3)
        o.save()
        oi = MonsterState(world=self.w, monster=o)
        oi.save()
        dmg = fg.attack(oi)
        self.assertEqual(dmg, 3)
        oi.delete()
        o.delete()
        ss.delete()
        fg.delete()

# EOF
