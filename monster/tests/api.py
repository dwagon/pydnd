from django.test import TestCase
from monster.models import Monster
from world.models import World
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


##############################################################################
class test_MonsterAPI(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.orc = Monster(name="Orc", align="CE", size="M", ac=13, hitdie="2d8 + 6", speed=30, stat_str=16, stat_dex=12, stat_con=16, stat_int=7, stat_wis=11, stat_cha=10, challenge="1/2")
        self.orc.save()
        self.rat = Monster(name="Rat", align="U", size="T", ac=10, hitdie="1d4 - 1", speed=20, stat_str=2, stat_dex=11, stat_con=9, stat_int=2, stat_wis=10, stat_cha=10, challenge="0")
        self.rat.save()
        self.client = APIClient()

    def tearDown(self):
        self.orc.delete()
        self.rat.delete()
        self.w.delete()

    def test_list(self):
        resp = self.client.get(reverse('monster-list'), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEqual(len(result), 2)

    def test_search(self):
        resp = self.client.get(reverse('monster-list') + '?name=rat', follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'rat')
        self.assertEqual(result[0]['damage'], '1d10')


# EOF
