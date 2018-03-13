from django.test import TestCase
from world.models import World
from character.models import Character
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status
import json


##############################################################################
class test_api(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.w = World(name='test_api')
        self.w.save()

    ##########################################################################
    def cleanUp(self):
        self.w.delete()

    ##########################################################################
    def test_create(self):
        data = {'world': self.w.id, 'charclass': 'FG', 'name': 'Zebedee', 'stat_cha': 2}
        resp = self.client.post(reverse('character-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = json.loads(resp.content)

        c = Character.objects.get(pk=data['id'])
        self.assertEqual(c.name, 'Zebedee')
        self.assertEqual(data['name'], 'Zebedee')
        self.assertEqual(c.stat_cha, 2)
        self.assertEqual(c.charclass, 'FG')
        self.assertNotEqual(c.status, 'XX')

    ##########################################################################
    def test_delete(self):
        data = {'world': self.w.id, 'charclass': 'FG', 'name': 'Florence'}
        resp = self.client.post(reverse('character-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        flo = json.loads(resp.content)

        resp = self.client.delete(reverse('character-detail', kwargs={'pk': flo['id']}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        cs = Character.objects.filter(pk=flo['id'])
        self.assertEqual(len(cs), 0)

# EOF
