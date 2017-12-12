from django.test import TestCase
from encounter.models import Encounter
from monster.models import Monster
from world.models import World
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status


class test_Encounter_API(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.w = World()
        self.w.save()

    ##########################################################################
    def tearDown(self):
        self.w.delete()

    ##########################################################################
    def test_create(self):
        data = {'world': self.w.id, 'size_x': 13, 'size_y': 7}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(result['turn'], 0)
        self.assertEqual(result['world'], self.w.id)
        self.assertEqual(result['size_y'], 7)
        e = Encounter.objects.get(id=result['id'])
        self.assertEqual(e.world.id, self.w.id)
        self.assertEqual(e.size_x, 13)

    ##########################################################################
    def test_add_monsters(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        m = Monster(name='test_elf', numappearing=20)
        m.save()

        data = {'number': 3}
        resp = self.client.post(reverse('encounter-monster-create', kwargs={'pk': enc_id, 'monster': m.id}), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['encounter'], enc_id)
        self.assertEqual(result[0]['monster'], m.id)

# EOF
