from django.test import TestCase
from monster.models import Monster


class test_Monster(TestCase):
    def setUp(self):
        self.orc = Monster(name='orc', movement=3, ac=3, thaco=19, xp=3)
        self.orc.save()

    def test_movement(self):
        self.assertEqual(self.orc.movement, 3)

# EOF
