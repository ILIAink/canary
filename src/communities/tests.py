from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from django.apps import AppConfig
from django.apps import apps
from .models import *
#from accounts.models import User
from .views import *


class CommunityTests(TestCase):

  def test_community_save_community(self):
    request = HttpRequest()
    request.method = "GET"
    request.POST = {'name': 'testing quality enforcement', 'password': 'testingstinks', 'description': "report bad code"
                 ,'user_id': 'tester2@gmail.com'}

    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser', password="123")
    request.user = testUser

    # call function we are testing
    save_community(request)

    community = Community.objects.get(name="testing quality enforcement")
    self.assertEqual(community.name,"testing quality enforcement")
    self.assertEqual(community.description, "report bad code")
    self.assertEqual(community.password, 'testingstinks')

    admin = CommunityMember.objects.get(community=community, member=testUser, is_admin=True),
    self.assertIsNotNone(admin)


