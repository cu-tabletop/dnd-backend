import base64
import json
from io import BytesIO

from django.test import Client, TestCase
from PIL import Image

from dnd.models import Campaign, CampaignMembership, Player
from dnd.schemas.campaign import CampaignPermissions


class TestCampaignAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.player1 = Player.objects.create(telegram_id=1001, verified=True)
        self.player2 = Player.objects.create(telegram_id=1002, verified=False)
        self.campaign = Campaign.objects.create(
            title="Test Campaign", verified=True
        )
        CampaignMembership.objects.create(
            user=self.player1,
            campaign=self.campaign,
            status=CampaignPermissions.OWNER,
        )

    def test_create_campaign_success(self):
        # Test successful campaign creation with icon and description
        image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        icon_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        payload = {
            "telegram_id": self.player1.telegram_id,
            "title": "New Campaign",
            "description": "A test campaign",
            "icon": icon_data,
        }
        response = self.client.post(
            "/api/campaign/create/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "created"})

        # Verify campaign and membership creation
        campaign = Campaign.objects.get(title="New Campaign")
        self.assertEqual(campaign.description, "A test campaign")
        self.assertTrue(campaign.icon.name.endswith(".png"))
        self.assertTrue(
            CampaignMembership.objects.filter(
                user=self.player1,
                campaign=campaign,
                status=CampaignPermissions.OWNER,
            ).exists()
        )

    def test_create_campaign_missing_player(self):
        # Test 404 when player does not exist
        payload = {
            "telegram_id": 9999,  # Non-existent player
            "title": "Invalid Campaign",
        }
        response = self.client.post(
            "/api/campaign/create/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_get_campaign_by_id_success(self):
        # Test retrieving a public campaign by ID
        response = self.client.get(
            f"/api/campaign/get/?campaign_id={self.campaign.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.campaign.id,
                "title": "Test Campaign",
                "description": "",
                "icon": None,
                "verified": True,
                "private": False,
            },
        )

    def test_get_campaign_private_no_access(self):
        # Test accessing a private campaign without membership
        self.campaign.private = True
        self.campaign.save()
        response = self.client.get(
            f"/api/campaign/get/?campaign_id={self.campaign.id}&user_id={self.player2.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(), {"detail": "requested campaign does not exist"}
        )

    def test_get_campaign_private_with_access(self):
        # Test accessing a private campaign with membership
        self.campaign.private = True
        self.campaign.save()
        CampaignMembership.objects.create(
            user=self.player2,
            campaign=self.campaign,
            status=CampaignPermissions.PLAYER,
        )
        response = self.client.get(
            f"/api/campaign/get/?campaign_id={self.campaign.id}&user_id={self.player2.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.campaign.id)

    def test_get_all_campaigns(self):
        # Test retrieving all campaigns (public and user-specific)
        Campaign.objects.create(title="Public Campaign", private=False)
        response = self.client.get(
            f"/api/campaign/get/?user_id={self.player1.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        campaigns = response.json()
        self.assertGreaterEqual(
            len(campaigns), 2
        )  # At least test campaign and public campaign
        self.assertTrue(any(c["id"] == self.campaign.id for c in campaigns))

    def test_get_campaign_not_found(self):
        # Test 404 for non-existent campaign
        response = self.client.get(
            "/api/campaign/get/?campaign_id=9999",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_add_to_campaign_success(self):
        # Test adding a new user to a campaign
        payload = {"owner_id": self.player1.id, "user_id": self.player2.id}
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/add/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "message": f"User {self.player2.id} added to campaign {self.campaign.id}"
            },
        )
        self.assertTrue(
            CampaignMembership.objects.filter(
                user=self.player2,
                campaign=self.campaign,
                status=CampaignPermissions.PLAYER,
            ).exists()
        )

    def test_add_to_campaign_already_member(self):
        # Test adding an existing member
        CampaignMembership.objects.create(
            user=self.player2,
            campaign=self.campaign,
            status=CampaignPermissions.MASTER,
        )
        payload = {"owner_id": self.player1.id, "user_id": self.player2.id}
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/add/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": f"User {self.player2.id} added to campaign {self.campaign.id}"
            },
        )
        membership = CampaignMembership.objects.get(
            user=self.player2, campaign=self.campaign
        )
        self.assertEqual(membership.status, CampaignPermissions.PLAYER)

    def test_add_to_campaign_not_owner(self):
        # Test 403 when non-owner tries to add a user
        payload = {"owner_id": self.player2.id, "user_id": self.player2.id}
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/add/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(), {"message": "Only the owner can add members"}
        )

    def test_add_to_campaign_not_found(self):
        # Test 404 for non-existent user
        payload = {"owner_id": self.player1.id, "user_id": 9999}
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/add/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_edit_permissions_success(self):
        # Test updating permissions for a campaign member
        CampaignMembership.objects.create(
            user=self.player2,
            campaign=self.campaign,
            status=CampaignPermissions.PLAYER,
        )
        payload = {
            "owner_id": self.player1.id,
            "user_id": self.player2.id,
            "status": CampaignPermissions.MASTER,
        }
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/edit-permissions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": f"Updated user {self.player2.id} role "
                f"to {CampaignPermissions.MASTER} in campaign {self.campaign.id}"
            },
        )
        membership = CampaignMembership.objects.get(
            user=self.player2, campaign=self.campaign
        )
        self.assertEqual(membership.status, CampaignPermissions.MASTER)

    def test_edit_permissions_invalid_status(self):
        # Test 400 for invalid status value
        payload = {
            "owner_id": self.player1.id,
            "user_id": self.player2.id,
            "status": 999,
        }
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/edit-permissions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_permissions_not_owner(self):
        # Test 403 when non-owner tries to edit permissions
        CampaignMembership.objects.create(
            user=self.player2,
            campaign=self.campaign,
            status=CampaignPermissions.PLAYER,
        )
        payload = {
            "owner_id": self.player2.id,
            "user_id": self.player2.id,
            "status": CampaignPermissions.MASTER,
        }
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/edit-permissions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(), {"message": "Only the owner can edit permissions"}
        )

    def test_edit_permissions_not_found(self):
        # Test 404 for non-existent membership
        payload = {
            "owner_id": self.player1.id,
            "user_id": 9999,
            "status": CampaignPermissions.MASTER,
        }
        response = self.client.post(
            f"/api/campaign/{self.campaign.id}/edit-permissions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_get_campaigns_for_user(self):
        # Test retrieving campaigns for user_id=2
        response = self.client.get(
            f"/api/campaign/get/?user_id={self.player2.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        campaigns = response.json()
        self.assertTrue(isinstance(campaigns, list))
        # self.assertFalse(
        #     any(c["id"] == self.campaign.id for c in campaigns)
        # )  # player2 has no access to the campaign
