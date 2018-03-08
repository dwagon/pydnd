from django.test import TestCase
from world.models import World

from character.models import Cleric, Spell
import status


class test_Cleric(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.cl = Cleric(world=self.w, name='test', stat_con=9)
        self.cl.save()
        self.sp = Spell(name='Cure Light Wounds', level=1, charclass=Spell.CLERIC, spellfile='cure_light_wounds')
        self.sp.save()

    def cleanUp(self):
        self.sp.delete()
        self.cl.delete()
        self.w.delete()

    def test_hp(self):
        self.assertEqual(self.cl.hitdie(), 'd8')
        self.assertGreaterEqual(self.cl.hp, 1)
        self.assertLessEqual(self.cl.hp, 8)

    def test_stats(self):
        self.assertGreaterEqual(self.cl.stat_wis, 3)
        self.assertLessEqual(self.cl.stat_wis, 18)

    def test_learn_spell(self):
        self.cl.learn_spell(self.sp)
        self.cl.learn_spell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 2)

    def test_unknown_spells(self):
        known = self.cl.known_spells(level=2)
        self.assertFalse(known)

    def test_cast_spell(self):
        self.cl.learn_spell(self.sp)
        self.cl.learn_spell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 2)
        self.cl.cast_spell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 1)

    def test_heal(self):
        self.cl.learn_spell(self.sp)
        self.cl.max_hp = 8
        self.cl.hp = 5
        self.cl.save()
        self.cl.heal(5)
        self.assertEqual(self.cl.hp, 8)
        self.cl.hurt(9)
        self.assertEqual(self.cl.status, status.UNCONSCIOUS)
        self.cl.heal(5)
        self.assertEqual(self.cl.hp, 4)
        self.assertEqual(self.cl.status, status.OK)

# EOF
