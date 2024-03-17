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
    request.POST = {'name': 'testing quality enforcement', 'password': 'testingstinks', 'description': "report bad code"}


    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser', password="123")
    request.user = testUser

    # view being tested
    save_community(request)

    community = Community.objects.get(name="testing quality enforcement")
    self.assertEqual(community.name,"testing quality enforcement")
    self.assertEqual(community.description, "report bad code")
    self.assertEqual(community.password, 'testingstinks')

    admin = CommunityMember.objects.get(community=community, member=testUser, is_admin=True),
    self.assertIsNotNone(admin)


  def test_join_community_valid_community(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser', password="123")
    testUser.save()

    request = HttpRequest()
    request.method = "POST"
    request.POST = {'name': 'test_community', 'password': "123"}
    request.user = testUser

    test_community = Community(name="test_community", description="report bad code", password="123")
    test_community.save()

    # view being tested
    join_community(request)

    member = CommunityMember.objects.get(community=test_community, member=testUser, is_admin=False)
    self.assertIsNotNone(member)
    self.assertEqual(member.member.username, testUser.username)
    self.assertEqual(member.member.password, testUser.password)


  def test_save_report_authenticated_user(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser', password="123")
    testUser.save()

    request = HttpRequest()
    request.method = 'POST'
    request.POST = {'title': 'test_report', 'content': 'this is a report', 'resolution_method': 'Canary'}
    request.user = testUser

    test_community = Community(name="test_community", description="report bad code", password="123")
    test_community.save()

    # view being tested
    save_report(request, test_community.id)

    # check for existence of report
    report = Report.objects.get(title='test_report', content='this is a report', author=testUser)
    self.assertIsNotNone(report)
    self.assertEqual(report.author, testUser)
    self.assertEqual(report.content, 'this is a report')
    # check that community acknowledges report
    self.assertIn(report, test_community.reports.all())
