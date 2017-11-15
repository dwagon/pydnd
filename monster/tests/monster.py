from django.test import TestCase
from monster.models import Monster


class test_Monster(TestCase):
    def setUp(self):
        self.orc = Monster(name='orc', movement=3, ac=3, thaco=19, xp=3)
        self.orc.save()

    def test_movement(self):
        self.assertEqual(self.orc.movement, 3)

    def test_hitpoints(self):
        self.assertGreaterEqual(self.orc.hp, 1)
        self.assertLessEqual(self.orc.hp, 8)

    def test_hurt(self):
        hp = self.orc.max_hp
        self.orc.hurt(5)
        self.assertEqual(self.orc.hp, hp - 5)

    def test_death(self):
        rc = self.orc.hurt(50)
        self.assertEqual(self.orc.status, 'DE')
        self.assertFalse(rc)

    def test_hit(self):
        from character.models import Character
        c = Character(name='victim', charclass='M')
        c.ac = 30   # Guarantee hit
        c.save()
        hit = self.orc.hit(c)
        self.assertTrue(hit)
        c.ac = -20    # Guarantee miss
        c.save()
        hit = self.orc.hit(c)
        self.assertFalse(hit)

# EOF
