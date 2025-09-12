import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

LOGIN_URL = '/api/users/login/'

@pytest.mark.django_db
def test_login_success():
    user = User.objects.create_user(
        email='userexample@example.com',
        password='userexample12345'
    )
    client = APIClient()

    payload = {
        'email': 'userexample@example.com',  
        'password': 'userexample12345'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 200
    assert 'token' in response.data


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
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_user_not_exist():
    client = APIClient()
    payload = {
        'email': 'falseuser@example.com',
        'password': 'falseuser12345'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_with_false_email():
    client = APIClient()
    payload = {
        'email': 'bademail',
        'password': 'correctpasswod'
    }
    response = client.post(LOGIN_URL, payload, format='json')

    assert response.status_code == 400


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