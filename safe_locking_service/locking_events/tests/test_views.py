from django.test import TestCase
from django.urls import reverse

from rest_framework import status


class TestQueueService(TestCase):
    def test_about_view(self):
        url = reverse("v1:locking_events:about")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
