import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

LOGIN_URL = '/api/users/login/'
LOGOUT_URL = '/api/users/logout/'
PROTECTED_URL = '/api/post/'

@pytest.fixture
def create_user(db):
    def make_user(email="logout@example.com", password="password123"):
        return User.objects.create_user(email=email, password=password)
    return make_user

@pytest.fixture
def auth_client(create_user):
    def make_client(email="logout@example.com", password="password123"):
        user = create_user(email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return client, user, token
    return make_client


@pytest.mark.django_db
def test_logout_success(auth_client):
    client, user, token = auth_client()

    response = client.post(LOGOUT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert not Token.objects.filter(key=token.key).exists()


@pytest.mark.django_db
def test_logout_requires_authentication():
    client = APIClient()
    response = client.post(LOGOUT_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_twice(auth_client):
    client, user, token = auth_client()

    response1 = client.post(LOGOUT_URL)
    assert response1.status_code == status.HTTP_200_OK

    response2 = client.post(LOGOUT_URL)
    assert response2.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
def test_access_after_logout(auth_client):
    client, user, token = auth_client()

    client.post(LOGOUT_URL)

    response = client.get(PROTECTED_URL, HTTP_AUTHORIZATION=f"Token {token.key}")
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]