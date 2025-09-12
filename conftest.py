import pytest
from rest_framework.test import APIClient
from users.models import User, Team
import uuid

@pytest.fixture 
def create_user(db):
    def make_user(email=None, password='userpassword123', username=None, team=None):
        if not email: 
            email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        if not username:
            username = email.split('@')[0]
        if team is None:
            team, _ = Team.objects.get_or_create(name='Default Team')

        return User.objects.create_user(email=email, password=password, username=username, team=team)
    return make_user

@pytest.fixture
def auth_client(create_user):
    def make_client(email=None, password="authpassword123", username=None, team=None):
        if not email:
            email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        if username is None:
            username = email.split("@")[0]

        user = create_user(email=email, password=password, username=username, team=team)
        client = APIClient()

        login_response = client.post('/api/users/login/', {
            'email': email,
            'password': password
        }, format='json')

        assert login_response.status_code == 200, f"Login failed: {login_response.data}"
        assert "token" in login_response.data, f"No token returned: {login_response.data}"

        client.credentials(HTTP_AUTHORIZATION=f"Token {login_response.data['token']}")

        return client, user
    return make_client