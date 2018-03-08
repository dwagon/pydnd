from django.test import TestCase

from character.models import Fighter
from equipment.models import Equipment, Weapon, Armour
from monster.models import Monster, MonsterState
from encounter.models import Encounter
from world.models import World


class test_Fighter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.fg = Fighter(world=self.w, name='test', stat_con=10, stat_dex=10)
        self.fg.save()
        self.sword = Weapon(name='Long Sword', weight=5)
        self.sword.save()
        self.mace = Weapon(name='Mace', weight=7)
        self.mace.save()
        self.spikes = Equipment(name='Iron Spikes', weight=6)
        self.spikes.save()
        self.leather = Armour(name='TestLeather', weight=6, base_ac=11, armour_categ='L')
        self.leather.save()
        self.shield = Armour(name='Shield', weight=4, armour_categ='S')
        self.shield.save()

    def cleanUp(self):
        self.spikes.delete()
        self.sword.delete()
        self.leather.delete()
        self.fg.delete()
        self.w.delete()

    def test_hp(self):
        self.assertEqual(self.fg.hitdie(), 'd10')
        self.assertGreaterEqual(self.fg.hp, 1)
        self.assertLessEqual(self.fg.hp, 10)

    def test_stats(self):
        self.assertGreaterEqual(self.fg.stat_str, 3)
        self.assertLessEqual(self.fg.stat_str, 18)

    def test_equip(self):
        self.fg.equip(self.sword, ready=True)
        self.fg.equip(self.mace)
        self.fg.equip(self.spikes)
        self.assertEqual(self.fg.encumbrance, 18)
        self.fg.equip(self.leather, ready=True)
        w = self.fg.equipped_weapon()[0]
        self.assertEqual(w.name, 'Long Sword')

    def test_unequiped(self):
        w = self.fg.equipped_weapon()
        self.assertFalse(w)

    def test_armour(self):
        self.fg.equip(self.leather, ready=True)
        self.fg.equip(self.spikes)
        a = self.fg.equipped_armour()
        self.assertEqual(sorted([_.name for _ in a]), sorted(['TestLeather']))

    def test_naked(self):
        a = self.fg.equipped_armour()
        self.assertFalse(a)

    def test_ac(self):
        self.assertEqual(self.fg.ac, 10)
        self.fg.equip(self.sword, ready=True)
        self.fg.equip(self.spikes)
        self.assertEqual(self.fg.ac, 10)
        self.fg.equip(self.leather, ready=True)
        self.assertEqual(self.fg.ac, 11)
        self.fg.equip(self.shield, ready=True)
        self.assertEqual(self.fg.ac, 13)

    def test_hit(self):
        o = Monster(name='weak_orc', movement=3, ac=20, thaco=20, xp=3)
        o.save()
        e = Encounter(world=self.w)
        e.save()
        oi = MonsterState(encounter=e, monster=o)
        oi.save()
        rc = self.fg.attack(oi)
        self.assertTrue(rc)
        oi.delete()
        o.delete()

    def test_miss(self):
        o = Monster(name='strong_orc', movement=3, ac=-20, thaco=20, xp=6)
        o.save()
        e = Encounter(world=self.w)
        e.save()
        oi = MonsterState(encounter=e, monster=o)
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
        e = Encounter(world=self.w)
        e.save()
        oi = MonsterState(encounter=e, monster=o)
        oi.save()
        dmg = fg.attack(oi)
        self.assertEqual(dmg, 3)
        oi.delete()
        o.delete()
        ss.delete()
        fg.delete()

# EOF
