from django.test import TestCase

from character.models import Thief


class test_Thief(TestCase):
    def setUp(self):
        self.th = Thief(name='test')
        self.th.save()

    def test_hp(self):
        self.assertEqual(self.th.hitdie, 6)
        self.assertGreaterEqual(self.th.hp, 1)
        self.assertLessEqual(self.th.hp, 6)

    def test_thaco(self):
        self.assertEqual(self.th.thaco, 20)

    def test_encumb(self):
        self.assertEqual(self.th.encumbrance, 0)

    def test_stats(self):
        self.assertGreaterEqual(self.th.stat_dex, 3)
        self.assertLessEqual(self.th.stat_dex, 18)


# EOF
