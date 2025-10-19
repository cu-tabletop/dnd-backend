import json

from django.test import Client, TestCase

from dnd.models import Campaign, CampaignMembership, Character, Player
from dnd.schemas.campaign import CampaignPermissions


class TestCharacterAPI(TestCase):
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
        self.character_data = json.load(
            open("dnd/tests/example-character.json", encoding="utf-8")
        )
        self.character = Character.objects.create(
            owner=self.player1, campaign=self.campaign
        )
        self.character.save_data(self.character_data)

    # def test_get_character_success(self):
    #     # Test successful retrieval of a character by ID
    #     response = self.client.get(
    #         f"/api/character/get/?char_id={self.character.id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         response.json(),
    #         {
    #             "id": self.character.id,
    #             "owner_id": self.player1.id,
    #             "owner_telegram_id": self.player1.telegram_id,
    #             "campaign_id": self.campaign.id,
    #             "data": self.character_data,
    #         },
    #     )

    def test_get_character_not_found(self):
        # Test 404 for non-existent character
        response = self.client.get(
            "/api/character/get/?char_id=9999",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_get_character_missing_char_id(self):
        # Test 400 for missing char_id parameter
        response = self.client.get(
            "/api/character/get/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_character_success(self):
        # Test successful character creation
        new_character_data = json.load(
            open("dnd/tests/example-character.json", encoding="utf-8")
        )
        payload = {
            "owner_id": self.player1.id,
            "campaign_id": self.campaign.id,
            "data": new_character_data,
        }
        response = self.client.post(
            "/api/character/post/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["owner_id"], self.player1.id)
        self.assertEqual(
            response_data["owner_telegram_id"], self.player1.telegram_id
        )
        self.assertEqual(response_data["campaign_id"], self.campaign.id)
        self.assertEqual(response_data["data"], new_character_data)
        self.assertTrue("id" in response_data)

        # Verify character creation in the database
        character = Character.objects.get(id=response_data["id"])
        self.assertEqual(character.owner_id, self.player1.id)
        self.assertEqual(character.campaign_id, self.campaign.id)

    def test_upload_character_missing_owner(self):
        # Test 404 for non-existent owner
        payload = {
            "owner_id": 9999,  # Non-existent player
            "campaign_id": self.campaign.id,
            "data": {"name": "Invalid Hero", "level": 1},
        }
        response = self.client.post(
            "/api/character/post/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_upload_character_missing_campaign(self):
        # Test 404 for non-existent campaign
        payload = {
            "owner_id": self.player1.id,
            "campaign_id": 9999,  # Non-existent campaign
            "data": {"name": "Invalid Hero", "level": 1},
        }
        response = self.client.post(
            "/api/character/post/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Объект не найден"})

    def test_upload_character_invalid_data(self):
        # Test 400 for invalid data (e.g., non-dict data)
        payload = {
            "owner_id": self.player1.id,
            "campaign_id": self.campaign.id,
            "data": "invalid_data",  # Should be a dict
        }
        response = self.client.post(
            "/api/character/post/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
