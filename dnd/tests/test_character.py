from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse

import json
from ..models import *


class TestGetCharacter(APITestCase):
    client: APIClient

    def setUp(self):
        self.url = reverse('get character')
        self.owner_obj = Player.objects.create(telegram_id=123, bio='bio')
        self.campaign_obj = Campaign.objects.create(title="campaign")

    def create_character(self, data=None):
        char_obj = Character.objects.create(owner=self.owner_obj, campaign=self.campaign_obj)
        if data is None:
            data = {"char_name": "Default"}
        char_obj.save_data(data)
        char_obj.save()
        return char_obj

    def test_get_character_success(self):
        char_obj = self.create_character({"char_name": "Grigory"})
        response = self.client.get(self.url, {"char_id": char_obj.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("char_data"), {"char_name": "Grigory"})
        self.assertEqual(response.data.get("campaign_id"), self.campaign_obj.id)

    def test_get_character_incorrect_query_type_error(self):
        response = self.client.get(self.url, {"char_id": "Hello, world!"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_character_missing_char_id(self):
        response = self.client.get(self.url)  # no char_id at all
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_character_char_id_zero(self):
        response = self.client.get(self.url, {"char_id": 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_character_not_found(self):
        response = self.client.get(self.url, {"char_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_character_with_path_request_success(self):
        char_obj = self.create_character({"info": {"charClass": "Wizard"}})
        response = self.client.get(
            self.url,
            {"char_id": char_obj.id, "path": ["info", "charClass"]},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("requested"), "Wizard")

    def test_get_character_with_path_request_nonexistent_key(self):
        char_obj = self.create_character({"info": {"charClass": "Wizard"}})
        response = self.client.get(
            self.url,
            {"char_id": char_obj.id, "path": ["info", "nonexistent"]},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get("requested"))

    def test_get_character_with_path_request_not_list(self):
        char_obj = self.create_character({"char_name": "Grigory"})
        response = self.client.get(
            self.url,
            {"char_id": char_obj.id, "path": "char_name"},  # not a list
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('requested'), 'Grigory')

    def test_character_set_success(self):
        char_obj = self.create_character({"info": {"charClass": "Wizard"}})
        result = char_obj.set("info", value="Sorcerer")
        self.assertTrue(result)
        self.assertEqual(char_obj.get("info", "value"), "Sorcerer")

    def test_character_set_invalid_path(self):
        char_obj = self.create_character({"info": {"charClass": "Wizard"}})
        result = char_obj.set("not_exist", value="Sorcerer")
        self.assertFalse(result)
        self.assertIsNone(char_obj.get("not_exist"))

class TestUploadCharacter(APITestCase):
    client: APIClient
    def test_upload_character_success(self):
        url = reverse('upload character')
        data_str = json.load(open("dnd/tests/example-character.json", encoding='utf-8'))
        user_id = 1
        campaign_obj = Campaign.objects.create(
            title='test campaign'
        )
        player_obj = Player.objects.create(
            id=user_id,
            bio="test bio",
            admin=False,
        )
        CampaignMembership.objects.create(
            user=player_obj,
            campaign=campaign_obj,
        )
        self.assertEqual(Character.objects.all().count(), 0)
        response = self.client.post(url, data={
            "owner_id": user_id,
            "campaign_id": campaign_obj.id,
            "data": data_str,
            "char_name": "example-character",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Character.objects.all().count(), 1)
