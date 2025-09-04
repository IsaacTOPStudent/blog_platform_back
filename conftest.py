import pytest
from rest_framework.test import APIClient
from users.models import User, Team

@pytest.fixture 
def create_user(db):
    def make_user(email='user@example.com', password='userpassword123', username='tester', team=None):
        if team is None:
            team, _ = Team.objects.get_or_create(name='Default Team')

        return User.objects.create_user(email=email, password=password, username=username, team=team)
    return make_user

@pytest.fixture 
def auth_client(create_user):
    def make_client(email='auth@example.com', password='authpassword123', username=None, team=None):
        if username is None:
            username = email.split("@")[0]
        user = create_user(email=email, password=password, username=username, team=team)
        client = APIClient()
        login_response = client.post('/api/users/login/', {
            'email': email,
            'password': password
        }, format='json')
        assert login_response.status_code == 200, f"Login failed: {login_response.data}"
        client.credentials(HTTP_AUTHORIZATION=f"Bearer { login_response.data['access']}")
        return client, user 
    return make_client