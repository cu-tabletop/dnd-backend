import base64

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse

from ..models import Player, Campaign, CampaignMembership


class TestCampaignCreate(APITestCase):
    client: APIClient

    def setUp(self):
        self.url = reverse('api-1.0.0:create_campaign_view')
        self.player = Player.objects.create(telegram_id=12345, bio='test bio')

    def test_campaign_create_success(self):
        data = {
            'telegram_id': self.player.telegram_id,
            'title': 'test campaign',
            'description': 'the best campaign ever',
            'icon': base64.b64encode(open('dnd/tests/test-campaign-icon.jpg', 'rb').read())
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Campaign.objects.count(), 1)
        self.assertEqual(CampaignMembership.objects.count(), 1)

    def test_campaign_create_missing_telegram_id(self):
        data = {'title': 'no user campaign'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 422)

    def test_campaign_create_invalid_telegram_id_type(self):
        data = {'telegram_id': 'not an int', 'title': 'fail'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 422)

    def test_campaign_create_nonexistent_user(self):
        data = {'telegram_id': 99999, 'title': 'ghost campaign'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_campaign_create_missing_title(self):
        data = {'telegram_id': self.player.telegram_id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 422)

    def test_campaign_create_invalid_title_type(self):
        data = {'telegram_id': self.player.telegram_id, 'title': 12345}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 422)


class TestGetCampaignInfo(APITestCase):
    client: APIClient

    def setUp(self):
        self.url = reverse("api-1.0.0:get_campaign_info_view")
        self.player = Player.objects.create(telegram_id=111, bio='user')
        self.public_campaign = Campaign.objects.create(title='Public Campaign', private=False)
        self.private_campaign = Campaign.objects.create(title='Private Campaign', private=True)
        CampaignMembership.objects.create(user=self.player, campaign=self.private_campaign, status=2)

    def test_get_specific_public_campaign(self):
        response = self.client.get(self.url, {'campaign_id': self.public_campaign.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Public Campaign')

    def test_get_specific_campaign_not_found(self):
        response = self.client.get(self.url, {'campaign_id': 9999})
        self.assertEqual(response.status_code, 404)

    def test_get_private_campaign_with_access(self):
        response = self.client.get(self.url, {
            'campaign_id': self.private_campaign.id,
            'user_id': self.player.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Private Campaign')

    def test_get_private_campaign_without_access(self):
        another_user = Player.objects.create(telegram_id=222)
        response = self.client.get(self.url, {
            'campaign_id': self.private_campaign.id,
            'user_id': another_user.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_get_private_campaign_no_user_id(self):
        response = self.client.get(self.url, {'campaign_id': self.private_campaign.id})
        self.assertEqual(response.status_code, 403)

    def test_get_all_public_campaigns(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('campaigns', response.json())
        self.assertTrue(any(c['title'] == 'Public Campaign' for c in response.json()['campaigns']))

    def test_get_campaigns_with_valid_user_id(self):
        response = self.client.get(self.url, {'user_id': self.player.id})
        self.assertEqual(response.status_code, 200)
        titles = [c['title'] for c in response.json()['campaigns']]
        self.assertIn('Public Campaign', titles)
        self.assertIn('Private Campaign', titles)

    def test_get_campaigns_with_invalid_user_id_type(self):
        response = self.client.get(self.url, {'user_id': 'notanint'})
        self.assertEqual(response.status_code, 422)

class TestAddToCampaign(APITestCase):
    client: APIClient

    def setUp(self):
        self.url = reverse("api-1.0.0:add_to_campaign_view")
        self.owner = Player.objects.create(telegram_id=1)
        self.user = Player.objects.create(telegram_id=2)
        self.campaign = Campaign.objects.create(title="Test Campaign", private=False)
        CampaignMembership.objects.create(
            user=self.owner, campaign=self.campaign, status=2  # Owner
        )

    def test_add_user_success(self):
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": self.owner.id,
            "user_id": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            CampaignMembership.objects.filter(user=self.user, campaign=self.campaign).exists()
        )

    def test_add_user_already_exists(self):
        CampaignMembership.objects.create(user=self.user, campaign=self.campaign, status=1)
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": self.owner.id,
            "user_id": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        membership = CampaignMembership.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(membership.status, 0)  # reset to player

    def test_missing_parameters(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 422)

    def test_campaign_not_found(self):
        data = {"campaign_id": 999, "owner_id": self.owner.id, "user_id": self.user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_owner_permission_denied(self):
        other_player = Player.objects.create(telegram_id=3)
        data = {"campaign_id": self.campaign.id, "owner_id": other_player.id, "user_id": self.user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_not_found(self):
        data = {"campaign_id": self.campaign.id, "owner_id": self.owner.id, "user_id": 9999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 404)


class TestEditPermissions(APITestCase):
    client: APIClient

    def setUp(self):
        self.url = reverse("api-1.0.0:edit_permissions_view")
        self.owner = Player.objects.create(telegram_id=1)
        self.user = Player.objects.create(telegram_id=2)
        self.campaign = Campaign.objects.create(title="Permission Campaign", private=False)
        CampaignMembership.objects.create(user=self.owner, campaign=self.campaign, status=2)
        CampaignMembership.objects.create(user=self.user, campaign=self.campaign, status=0)

    def test_edit_permissions_success(self):
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": self.owner.id,
            "user_id": self.user.id,
            "status": 1,  # Promote to master
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        membership = CampaignMembership.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(membership.status, 1)

    def test_missing_parameters(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 422)

    def test_invalid_status_value(self):
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": self.owner.id,
            "user_id": self.user.id,
            "status": 5,  # invalid
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_campaign_not_found(self):
        data = {
            "campaign_id": 9999,
            "owner_id": self.owner.id,
            "user_id": self.user.id,
            "status": 1,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_owner_permission_denied(self):
        other_player = Player.objects.create(telegram_id=3)
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": other_player.id,
            "user_id": self.user.id,
            "status": 1,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_membership_not_found(self):
        stranger = Player.objects.create(telegram_id=4)
        data = {
            "campaign_id": self.campaign.id,
            "owner_id": self.owner.id,
            "user_id": stranger.id,
            "status": 1,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 404)
