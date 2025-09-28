import base64

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse

from ..models import *


class TestCampaignCreate(APITestCase):
    client: APIClient
    def test_campaign_create_success(self):
        url = reverse('create campaign')
        player_obj = Player.objects.create(telegram_id=1, bio='test bio')

        data = {
            'telegram_id': player_obj.telegram_id,
            'title': 'test campaign',
            'description': 'the best campaign ever',
            'icon': base64.b64encode(open('dnd/tests/test-campaign-icon.jpg', 'rb').read())
        }

        self.assertEqual(Campaign.objects.all().count(), 0)
        self.assertEqual(CampaignMembership.objects.all().count(), 0)

        response: Response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Campaign.objects.all().count(), 1)
        self.assertEqual(CampaignMembership.objects.all().count(), 1)
