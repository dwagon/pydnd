from django.test import TestCase
from world.models import World
from message.models import Message
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status
import json


##############################################################################
class test_api(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.w = World()
        self.w.save()

    ##########################################################################
    def cleanUp(self):
        self.w.delete()

    ##########################################################################
    def test_create(self):
        data = {'world': self.w.id, 'msg': 'test message'}
        resp = self.client.post(reverse('message-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = json.loads(resp.content)

        m = Message.objects.get(pk=data['id'])
        self.assertEqual(m.msg, 'test message')

    ##########################################################################
    def test_delete(self):
        data = {'world': self.w.id, 'msg': 'test delete message'}
        resp = self.client.post(reverse('message-list'), data=data, follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        m = json.loads(resp.content)

        resp = self.client.delete(reverse('message-detail', kwargs={'pk': m['id']}), follow=True, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        cs = Message.objects.filter(pk=m['id'])
        self.assertEqual(len(cs), 0)

# EOF
