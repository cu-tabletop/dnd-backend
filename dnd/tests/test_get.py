from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse


from ..models import *


class TestGetCharacter(APITestCase):
    client: APIClient
    def test_get_character_success(self):
        url = reverse('get character')

        owner_obj = Player.objects.create(telegram_id=1, bio='test bio')
        campaign_obj = Campaign.objects.create(title="test")
        char_obj = Character.objects.create(owner=owner_obj, campaign=campaign_obj)
        char_data = { "char_name": "Grigory", }
        char_obj.save_data(char_data)
        char_obj.save()

        response: Response = self.client.get(url, { "char_id": char_obj.id })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data.get("char_data"), char_data)
        self.assertEqual(response.data.get('campaign_id'), campaign_obj.id)

    def test_get_character_incorrect_query(self):
        url = reverse('get character')
        response: Response = self.client.get(url, { "char_id": 'Hello, world!' })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
