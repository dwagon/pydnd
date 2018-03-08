from django.test import TestCase
from monster.models import Monster
from equipment.models import Armour
from character.models import Wizard
from world.models import World


class test_Monster(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.orc = Monster(name='orc', movement=3, ac=3, thaco=19, xp=3, damage='1d4')
        self.orc.save()

    def tearDown(self):
        self.w.delete()

    def test_movement(self):
        self.assertEqual(self.orc.movement, 3)

    def test_attack(self):
        e = Armour(name='useless', base_ac=3, armour_categ='L')
        e.save()
        c = Wizard(world=self.w, name='victim', max_hp=10, hp=10)
        c.save()
        c.equip(e, ready=True)
        dmg = self.orc.attack(c)
        self.assertGreaterEqual(dmg, 1)
        self.assertLessEqual(dmg, 4)
        self.assertEqual(c.hp, 10 - dmg)

    def test_hit(self):
        e = Armour(name='useless', base_ac=3, armour_categ='L')
        e.save()
        c = Wizard(world=self.w, name='victim')
        c.save()
        c.equip(e, ready=True)
        hit = self.orc.hit(c)
        self.assertTrue(hit)

    def test_miss(self):
        e = Armour(name='impervious', base_ac=30, armour_categ='H')
        e.save()
        c = Wizard(world=self.w, name='victim')
        c.save()
        c.equip(e, ready=True)
        c.ac = -30    # Guarantee miss
        c.save()
        hit = self.orc.hit(c)
        self.assertFalse(hit)

# EOF
