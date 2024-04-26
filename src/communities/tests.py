from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.apps import AppConfig
from django.apps import apps
from .models import *
#from accounts.models import User
from .views import *
from django.contrib.messages.storage.fallback import FallbackStorage
from django.shortcuts import get_object_or_404
from django.http import Http404
from unittest.mock import PropertyMock
from unittest.mock import patch
from django.contrib.auth.models import AnonymousUser, User


class CommunityTests(TestCase):

  def test_community_save_community(self):
    request = HttpRequest()
    request.method = "GET"
    request.POST = {'name': 'testing quality enforcement', 'description': "report bad code"}


    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    request.user = testUser

    # view being tested
    save_community(request)

    community = Community.objects.get(name="testing quality enforcement")
    self.assertEqual(community.name,"testing quality enforcement")
    self.assertEqual(community.description, "report bad code")

    admin = CommunityMember.objects.get(community=community, member=testUser, is_admin=True, is_owner=True),
    self.assertIsNotNone(admin)

  #this test broke after community joining was switched to links
  """"
  def test_join_community_valid_community(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testUser.save()

    request = HttpRequest()
    request.method = "POST"
    request.POST = {'name': 'test_community'}
    request.user = testUser

    test_community = Community(name="test_community", description="report bad code")
    test_community.save()

    # view being tested
    join_community(request)

    member = CommunityMember.objects.get(community=test_community, member=testUser, is_admin=False)
    self.assertIsNotNone(member)
    self.assertEqual(member.member.username, testUser.username)
"""

  def test_save_report_authenticated_user(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testUser.save()

    request = HttpRequest()
    request.method = 'POST'
    request.POST = {'title': 'test_report', 'content': 'this is a report', 'resolution_method': 'Canary'}
    request.user = testUser
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    test_community = Community(name="test_community", description="report bad code")
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



  def test_invalid_save_community_too_long(self):
    request = HttpRequest()
    request.method = "GET"
    request.POST = {'name': 'test', 'description': "Lets mess some stuff up" * 30}


    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    request.user = testUser

    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    # view being tested
    save_community(request)

    with self.assertRaises(Http404):
      get_object_or_404(Community, name="test")

    with self.assertRaises(Http404):
      get_object_or_404(CommunityMember, member=testUser)

  def test_invalid_save_community_name_is_space(self):

    request = HttpRequest()
    request.method = "GET"
    request.POST = {'name': ' ', 'description': "Lets mess some stuff up"}

    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    request.user = testUser

    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    save_community(request)

    with self.assertRaises(Http404):
      get_object_or_404(Community, name="test")

    with self.assertRaises(Http404):
      get_object_or_404(CommunityMember, member=testUser)


  #not authenticated case
  def test_user_access_anon_user(self):
    request = HttpRequest()
    request.user = AnonymousUser()
    result = check_user_access(request, "community", level='member')
    self.assertFalse(result)


  def test_user_access_normal_member(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testCommunity = Community(name="testCommunity", description="for testing")
    testUser.save()
    testCommunity.save()

    request = HttpRequest()
    request.user = testUser

    member = CommunityMember(community=testCommunity, member=testUser, is_admin=False)
    member.save()
    result = check_user_access(request, "community", level='member', community_id=testCommunity.id)
    self.assertTrue(result)

  def test_user_access_not_member(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testCommunity = Community(name="testCommunity", description="for testing")
    testUser.save()
    testCommunity.save()

    request = HttpRequest()
    request.user = testUser

    #member = CommunityMember(community=testCommunity, member=testUser, is_admin=False)
    #member.save()
    result = check_user_access(request, "community", level='member', community_id=testCommunity.id)
    self.assertFalse(result)


  def test_user_access_own_report(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testCommunity = Community(name="testCommunity", description="for testing")
    testUser.save()
    testCommunity.save()

    member = CommunityMember(community=testCommunity, member=testUser, is_admin=False)
    member.save()

    request = HttpRequest()
    request.user = testUser

    test_report = Report(title='test_report', content='I snitched', author=testUser)
    test_report.save()
    result = check_user_access(request, "report", level='member', community_id=testCommunity.id, report_id=test_report.id)
    self.assertTrue(result)

  def test_user_access_admin(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testCommunity = Community(name="testCommunity", description="for testing")
    testUser.save()
    testCommunity.save()

    member = CommunityMember(community=testCommunity, member=testUser, is_admin=False)
    member.save()

    request = HttpRequest()
    request.user = testUser
    result = check_user_access(request, "community", level='admin', community_id=testCommunity.id)
    self.assertFalse(result)

  def test_leave_community_member(self):
    userModel = apps.get_model('accounts', 'User')
    testUser = userModel.objects.create_user(email="test_user@gmail.com", username='testuser')
    testCommunity = Community(name="testCommunity", description="for testing")
    testUser.save()
    testCommunity.save()

    member = CommunityMember(community=testCommunity, member=testUser, is_admin=False)
    member.save()

    request = HttpRequest()
    request.user = testUser

    leave_community(request=request, community_id=testCommunity.id)
    
    user_in_community = CommunityMember.objects.filter(community=testCommunity, member=testUser).exists()
    
    self.assertFalse(user_in_community)
