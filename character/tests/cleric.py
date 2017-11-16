from django.test import TestCase

from character.models import Cleric, Spell


class test_Cleric(TestCase):
    def setUp(self):
        self.cl = Cleric(name='test')
        self.cl.save()
        self.sp = Spell(name='Cure Light Wounds', level=1, charclass=Spell.CLERIC)
        self.sp.save()

    def cleanUp(self):
        self.sp.delete()
        self.cl.delete()

    def test_hp(self):
        self.assertEqual(self.cl.hitdie(), 'd8')
        self.assertGreaterEqual(self.cl.hp, 1)
        self.assertLessEqual(self.cl.hp, 8)

    def test_thaco(self):
        self.assertEqual(self.cl.thaco, 20)

    def test_stats(self):
        self.assertGreaterEqual(self.cl.stat_wis, 3)
        self.assertLessEqual(self.cl.stat_wis, 18)

    def test_learn_spell(self):
        self.cl.learnSpell(self.sp)
        self.cl.learnSpell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 2)

    def test_unknown_spells(self):
        known = self.cl.known_spells(level=2)
        self.assertFalse(known)

    def test_cast_spell(self):
        self.cl.learnSpell(self.sp)
        self.cl.learnSpell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 2)
        self.cl.castSpell(self.sp)
        known = self.cl.known_spells(level=1)
        self.assertEqual(len(known), 1)

# EOF
