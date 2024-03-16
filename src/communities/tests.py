from django.test import TestCase
from django.urls import reverse
from django.apps import AppConfig
from .models import Community


class CommunityTests(TestCase):
    def test_communities(self):

        test_community = Community.objects.create(name='test_community', password='123',description='test_description')

        response = self.client.get(reverse("communities:dashboard", args=(test_community.id)))
        print(response)
        self.assertEqual(response.status_code == 200)
