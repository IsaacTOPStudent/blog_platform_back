import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from users.models import Team, User

User = get_user_model()

REGISTER_URL = '/api/users/register/'

@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    payload = {
        'email': 'test@example.com',
        'password': 'security12345'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code ==201
    assert User.objects.filter(email=payload['email']).exists()


@pytest.mark.django_db
def test_register_user_missing_email():
    client = APIClient()
    payload = {
        'password': 'security12345'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 400
    assert 'email' in response.data

@pytest.mark.django_db
def test_register_user_missing_password():
    client = APIClient()
    payload = {
        'email': 'test@example.com'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 400
    assert 'password' in response.data


@pytest.mark.django_db
def test_register_user_duplicate_email():
    client = APIClient()
    User.objects.create_user(email='duplicate@example.com', password='duplicate12345')

    payload = {
        'email': 'duplicate@example.com',
        'password': 'newduplicate12345'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 400
    assert 'email' in response.data

@pytest.mark.django_db
def test_register_password_too_short():
    client = APIClient()
    payload = {
        'email': 'shortpass@example.com',
        'password': '123'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 400
    assert 'password' in response.data

@pytest.mark.django_db
def test_register_without_username_and_team():
    client = APIClient()
    payload = {
        'email': 'noteamandusername@example.com',
        'password': 'noteam12345'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 201
    user = User.objects.get(email='noteamandusername@example.com')
    assert user.username is None
    assert user.team.name == 'Default Team'

@pytest.mark.django_db
def test_register_default_role_is_blogger():
    client = APIClient()
    payload = {
        'email': 'checkrole@example.com',
        'password': 'validpass123'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 201
    user = User.objects.get(email='checkrole@example.com')
    assert user.role == 'blogger'

@pytest.mark.django_db
def test_create_superuser_assings_admin_role():
    superuser = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )
    assert superuser.is_staff is True
    assert superuser.is_superuser is True 
    assert superuser.role == 'admin'

@pytest.mark.django_db
def test_register_username_duplicate_in_team():
    team = Team.objects.create(name='Teachers')

    User.objects.create_user(email='user1@example.com', password='pass123', username='duplicate', team=team)

    with pytest.raises(IntegrityError):
        User.objects.create_user(email='user2@example.com', password='pass123', username='duplicate', team=team)


@pytest.mark.django_db
def test_register_assigns_default_team_if_none_provided():
    client = APIClient()
    payload = {
        "email": 'defaultteam@example.com',
        "password": 'validpass123'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 201
    user = User.objects.get(email='defaultteam@example.com')
    assert user.team.name == 'Default Team'

@pytest.mark.django_db
def test_register_without_email():
    client = APIClient()
    payload = {
        'email': 'whithoutemail',
        'password': 'password12345'
    }
    response = client.post(REGISTER_URL, payload, format='json')

    assert response.status_code == 400
    assert 'email' in response.data

@pytest.mark.django_db
def test_user_can_register_password_not_returned():
    client = APIClient()
    user_data = {
        'username': 'sebastian',
        'email': 'sebastian@email.com',
        'password': '123456',
    }
    response = client.post(REGISTER_URL, user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'password' not in response.data


@pytest.mark.django_db
def test_user_can_register_hashed_password():
    client = APIClient()
    user_data = {
        'username': 'sebastian',
        'email': 'sebastian@email.com',
        'password': '123456',
    }
    response = client.post(REGISTER_URL, user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(username='sebastian')
    # The password should not be stored in plain text
    assert user.password != user_data['password']
    assert user.check_password(user_data['password'])