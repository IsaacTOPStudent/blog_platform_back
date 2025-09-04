import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

LOGIN_URL = '/api/users/login/'
REFRESH_URL = '/api/users/token/refresh/'

@pytest.mark.django_db
def test_login_success():
    user = User.objects.create_user(
        email='userexample@example.com',
        password='userexample12345'
    )
    client = APIClient()

    payload = {
        'email':'userexample@example.com',
        'password':'userexample12345'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_login_invalid_password():
    user = User.objects.create_user(
        email='otheruser@example.com',
        password='otheruser12345'
    )
    client = APIClient()
    payload = {
        'email': 'otheruser@example.com',
        'password': 'wrongpass'
    }
    response = client.post(LOGIN_URL, payload, follow='json')

    assert response.status_code == 401



@pytest.mark.django_db
def test_login_user_not_exist():
    client = APIClient()
    payload = {
        'email': 'falseuser@example.com',
        'password': 'falseuser12345'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 401

@pytest.mark.django_db
def test_login_with_false_email():
    client = APIClient()
    payload = {
        'email': 'bademail',
        'password': 'correctpasswod'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_missing_fields():
    client = APIClient()
    payload = {
        'email': 'login@example.com'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_login_with_empty_fields():
    client = APIClient()
    response = client.post(LOGIN_URL, {"email": "", "password": ""}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_token_refresh():
    user = User.objects.create_user(
        email='refresh@example.com',
        password='refreshuser12345'
    )
    client = APIClient()
    login_response = client.post(LOGIN_URL, {
        'email': 'refresh@example.com',
        'password': 'refreshuser12345'
    }, format='json')

    refresh = login_response.data['refresh']

    response = client.post(REFRESH_URL, {'refresh': refresh}, format='json')

    assert response.status_code == 200
    assert 'access' in response.data

