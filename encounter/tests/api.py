from django.test import TestCase
from encounter.models import Encounter
from monster.models import Monster
from character.models import Character
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
        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['encounter'], enc_id)
        self.assertEqual(result[0]['monster'], m.id)

    ##########################################################################
    def test_delete_monsters(self):
        data = {'world': self.w.id, 'size_x': 13, 'size_y': 17}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        num_monsters = 3
        m = Monster(name='test_bat', numappearing=num_monsters)
        m.save()

        # Create the monsters
        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Get the list of monsters
        mresp = self.client.get(reverse('encounter-monster-list', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(mresp.status_code, status.HTTP_200_OK)
        monsters = mresp.json()

        # Delete one of the monsters
        resp = self.client.delete(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': monsters[0]['id']}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Get the shorter list of monsters
        mresp = self.client.get(reverse('encounter-monster-list', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(mresp.status_code, status.HTTP_200_OK)
        monsters = mresp.json()
        self.assertEqual(len(monsters), num_monsters - 1)

    ##########################################################################
    def test_listing_monsters(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        m = Monster(name='test_kobold', numappearing=5)
        m.save()

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(len(result), 5)

        resp = self.client.get(reverse('encounter-monster-list', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEqual(len(result), 5)
        self.assertEqual(result[-1]['encounter'], enc_id)
        self.assertEqual(result[-1]['monster'], m.id)
        self.assertEqual(result[-1]['status'], 'OK')

    ##########################################################################
    def test_placing_monsters(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        m = Monster(name='test_drow', numappearing=2)
        m.save()

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()

        resp = self.client.post(reverse('encounter-monster-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        for m in result:
            self.assertNotEqual(m['x'], -1)
            self.assertNotEqual(m['y'], -1)

    ##########################################################################
    def test_get_map(self):
        size_x = 5
        size_y = 3
        data = {'world': self.w.id, 'size_x': size_x, 'size_y': size_y}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        m = Monster(name='xyz', numappearing=1)
        m.save()

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(reverse('encounter-monster-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get(reverse('encounter-arena', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertIn(m.name, result['map'])
        lines = result['map'].splitlines()
        self.assertEqual(len(lines), size_x)
        cols = lines[0].split()
        self.assertEqual(len(cols), size_y)

    ##########################################################################
    def test_placing_pcs(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        c = self.client.post(reverse('character-list'), data={'world': self.w.id, 'charclass': 'M', 'name': 'Mike'}, follow=True, format='json')
        self.assertEqual(c.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(reverse('encounter-character-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        chars = Character.objects.filter(world=self.w)
        for c in chars:
            self.assertNotEqual(c.x, -1)
            self.assertNotEqual(c.y, -1)

# EOF
