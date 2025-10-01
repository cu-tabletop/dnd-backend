from django.test import TestCase
from django.urls import reverse


class TestPing(TestCase):
    def test_ping(self):
        url = reverse("api-1.0.0:ping")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
