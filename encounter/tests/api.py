from django.test import TestCase
from encounter.models import Encounter
from world.models import World
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status


class test_Encounter_API(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.w = World()
        self.w.save()

    def tearDown(self):
        self.w.delete()

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

# EOF
