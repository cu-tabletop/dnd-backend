from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

import json
from ..models import *


class TestUploadCharacter(APITestCase):
    def test_upload_character_success(self):
        url = reverse('upload character')
        data_str = json.load(open("dnd/tests/example-character.json", encoding='utf-8'))
        user_id = 1
        Player.objects.create(
            id=user_id,
            bio="test bio",
            admin=False,
        )
        self.assertEqual(Character.objects.all().count(), 0)
        response = self.client.post(url, data={
            "owner_id": user_id,
            "data": data_str,
            "char_name": "example-character",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Character.objects.all().count(), 1)
