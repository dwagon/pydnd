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
        self.orc = Monster(name='test_orc', movement=3, ac=3, thaco=19, xp=3, damage='1d4')
        self.orc.save()
        self.bunny = Monster(name='test_bunny', movement=9, ac=3, thaco=4, xp=3, damage='1d10')
        self.bunny.save()
        self.client = APIClient()

    def tearDown(self):
        self.orc.delete()
        self.bunny.delete()
        self.w.delete()

    def test_list(self):
        resp = self.client.get(reverse('monster-list'), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEqual(len(result), 2)

    def test_search(self):
        resp = self.client.get(reverse('monster-list') + '?name=test_bunny', follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_bunny')
        self.assertEqual(result[0]['damage'], '1d10')


# EOF
