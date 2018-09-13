from django.test import TestCase

from character.models import Fighter
from equipment.models import Equipment, Weapon, Armour
from monster.models import Monster, MonsterState
from world.models import World


class test_Fighter(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.fg = Fighter(world=self.w, name='test', stat_con=10, stat_dex=10)
        self.fg.save()
        self.sword = Weapon(name='Long Sword', weight=5, damage='1d8', damage_cat='S')
        self.sword.save()
        self.mace = Weapon(name='Mace', weight=7)
        self.mace.save()
        self.spikes = Equipment(name='Iron Spikes', weight=6)
        self.spikes.save()
        self.leather = Armour(name='TestLeather', weight=6, base_ac=11, armour_categ='L')
        self.leather.save()
        self.shield = Armour(name='Shield', weight=4, armour_categ='S')
        self.shield.save()
        self.setup_orc()

    def setup_orc(self):
        o = Monster(name="Orc", align="CE", size="M", ac=13, hitdie="2d8 + 6", speed=30, stat_str=16, stat_dex=12, stat_con=16, stat_int=7, stat_wis=11, stat_cha=10, challenge="1/2")
        o.save()

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
        self.fg.equip(self.sword, ready=True)
        o = Monster.objects.get(name='Orc')
        o.ac = 1        # Ensure hit
        o.save()
        oi = MonsterState(monster=o, world=self.w)
        oi.save()
        rc = self.fg.attack(oi)
        self.assertTrue(rc)
        o.ac = 13       # Restore
        o.save()
        oi.delete()

    def test_miss(self):
        o = Monster.objects.get(name='Orc')
        o.ac = 30   # Ensure miss
        o.save()
        oi = MonsterState(monster=o, world=self.w)
        oi.save()
        rc = self.fg.attack(oi)
        self.assertFalse(rc)
        o.ac = 13       # Restore
        o.save()
        oi.delete()

    def test_strength(self):
        fg = Fighter(world=self.w, name='test', stat_str=18)
        fg.save()
        ss = Weapon(name='Short Stick', weight=1, damage='1', damage_cat='P')
        ss.save()
        fg.equip(ss, ready=True)
        o = Monster.objects.get(name='Orc')
        o.ac = 1
        o.save()    # Ensure hit
        oi = MonsterState(monster=o, world=self.w)
        oi.save()
        dmg = fg.attack(oi)
        self.assertEqual(dmg, [(1 + 4, 'P')])
        oi.delete()
        ss.delete()
        o.ac = 13   # Restore
        o.save()
        fg.delete()

# EOF
