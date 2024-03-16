import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from communities.urls import urlpatterns
from accounts.models import User
import communities.views
# from communities.models import Community, CommunityMember



@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create(username='tester@gmail.com', password='testingisfun')
    assert user.username == 'tester@gmail.com'


class MockMaker:
    @staticmethod
    def mock_user_model():
        User = get_user_model()
        return User.objects
    @staticmethod
    def mock_user():
        return User.objects.create(username='tester2', password='testingisbad', email="tester2@gmail.com")


@pytest.mark.django_db
def test_community_creation(client, monkeypatch, django_db_setup):
    url = reverse("communities:save_community")
    post_data = {'name': 'testing quality enforcement', 'password': 'testingstinks', 'description': "report bad code"
                 ,'user_id': 'tester2@gmail.com'}
    def mock_get(*args, **kwargs):
        return MockMaker.mock_user_model()
    def mock_user():
        return MockMaker.mock_user()
    monkeypatch.setattr('django.contrib.auth.get_user_model', mock_user)
    response = client.post(url, data=post_data)
    assert response.status_code == 200

