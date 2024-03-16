from django.test import TestCase
from django.urls import reverse
from django.apps import AppConfig
from django.apps import apps
from .models import *
#from accounts.models import User


class CommunityTests(TestCase):
    def test_community_dashboard_new_community(self):
        test_community = Community.objects.create(name='test_community', password='123', description='test_description')
        response = self.client.get(reverse("communities:dashboard", args=(test_community.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['members'], [])
        self.assertQuerysetEqual(response.context['reports'], [])
        self.assertEqual(response.context['community'], test_community)


class CommunityViewTests(TestCase):
    def test_community_dashboard_populated_community(self):
        test_community = Community.objects.create(name='test_community', password='123', description='test_description')
        userModel = apps.get_model('accounts', 'User')
        test_user = userModel.objects.create_user(username='test_user')
        member = CommunityMember.objects.create(community=test_community, member=test_user)
        response = self.client.get(reverse("communities:dashboard", args=(test_community.id,)))
        #print(response.context['members'])
        members_set = set(response.context['members'].values_list('member', flat=True))
        print(members_set)
        print("hi")
        self.assertContains(response, member)