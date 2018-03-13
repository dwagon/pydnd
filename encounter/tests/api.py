from django.test import TestCase
from encounter.models import Encounter
from equipment.models import Equipment
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
        self.elf = Monster(name="Elf", align="CG", size="M", ac=13, hitdie="2d8 + 6", speed=30, stat_str=16, stat_dex=12, stat_con=16, stat_int=7, stat_wis=11, stat_cha=10, challenge="1/2")
        self.elf.save()

    ##########################################################################
    def tearDown(self):
        self.elf.delete()
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
    def test_delete(self):
        data = {'world': self.w.id, 'size_x': 13, 'size_y': 7}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()

        resp = self.client.delete(reverse('encounter-detail', kwargs={'pk': data['id']}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        e = Encounter.objects.filter(id=data['id'])
        self.assertEqual(len(e), 0)

    ##########################################################################
    def test_add_monsters(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        data = {'number': 3}
        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': self.elf.id}), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['encounter'], enc_id)
        self.assertEqual(result[0]['monster'], self.elf.id)

    ##########################################################################
    def test_delete_monsters(self):
        data = {'world': self.w.id, 'size_x': 13, 'size_y': 17}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        # Create the monsters
        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': self.elf.id}), data=data, follow=True, format='json')
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
        self.assertEqual(len(monsters), 0)

    ##########################################################################
    def test_listing_monsters(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        m = Monster.objects.get(name='Elf')

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={'number': 5}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        self.assertEqual(result[0]['name'][0:3], 'Elf')
        self.assertEqual(result[0]['status'], 'OK')
        self.assertGreaterEqual(result[0]['hp'], 8)
        self.assertLessEqual(result[0]['hp'], 24)

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

        m = Monster.objects.get(name='Elf')

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

        m = Monster.objects.get(name='Elf')

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(reverse('encounter-monster-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get(reverse('encounter-arena', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        for loc in result:
            x = int(loc.split()[0])
            y = int(loc.split()[1])
            self.assertEqual(x, result[loc]['x'])
            self.assertEqual(y, result[loc]['y'])
            self.assertEqual(result[loc]['content']['name'], 'Elf0')

    ##########################################################################
    def test_placing_pcs(self):
        data = {'world': self.w.id, 'size_x': 17, 'size_y': 11}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        result = resp.json()
        enc_id = result['id']

        c = self.client.post(reverse('character-list'), data={'world': self.w.id, 'charclass': 'WZ', 'name': 'Mike'}, follow=True, format='json')
        self.assertEqual(c.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(reverse('encounter-character-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        chars = Character.objects.filter(world=self.w)
        for c in chars:
            self.assertNotEqual(c.x, -1)
            self.assertNotEqual(c.y, -1)

    ##########################################################################
    def setup_pc(self, enc_id):
        # Create a pointed stick
        ls = Equipment(name='Pointed Stick')
        ls.save()

        # Create a PC
        c = self.client.post(reverse('character-list'), data={'world': self.w.id, 'charclass': 'FG', 'name': 'Figlet'}, follow=True, format='json')
        self.assertEqual(c.status_code, status.HTTP_201_CREATED)
        char = c.json()['id']

        # Find a pointed stick
        ps = self.client.get(reverse('equipment-list') + '?name=Pointed%20Stick', follow=True, format='json')
        self.assertEqual(ps.status_code, status.HTTP_200_OK)
        stick = ps.json()[0]['id']

        # Equip the stick
        equ = self.client.post(reverse('inventory-detail', kwargs={'pk': char, 'inv_pk': stick}), data={'ready': True}, follow=True, format='json')
        self.assertEqual(equ.status_code, status.HTTP_200_OK)

    ##########################################################################
    def test_combat_round(self):
        data = {'world': self.w.id, 'size_x': 3, 'size_y': 7}
        resp = self.client.post(reverse('encounter-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        enc_id = resp.json()['id']

        self.setup_pc(enc_id)

        # Place the PC
        resp = self.client.post(reverse('encounter-character-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create the monsters
        m = Monster.objects.get(name='Elf')

        resp = self.client.post(reverse('encounter-monster-detail', kwargs={'pk': enc_id, 'monster': m.id}), data={}, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Place the monsters
        resp = self.client.post(reverse('encounter-monster-place', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Finally, combat
        resp = self.client.post(reverse('encounter-combat-phase', kwargs={'pk': enc_id}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

# EOF
