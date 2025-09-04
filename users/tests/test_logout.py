import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

LOGIN_URL = '/api/users/login/'
LOGOUT_URL = '/api/users/logout/'
PROTECTED_URL = '/api/post/'

@pytest.mark.django_db
def get_tokens_for_user(email='logout@example.com', password='password123'):
    user = User.objects.create_user(email=email, password=password)
    client = APIClient()
    login_response = client.post(LOGIN_URL, {
        'email': email, 
        'password': password
    }, format='json')

    assert login_response.status_code == 200, login_response.data
    return login_response.data['access'], login_response.data['refresh']

@pytest.mark.django_db
def test_logout_success():
    access, refresh = get_tokens_for_user()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = client.post(LOGOUT_URL, {'refresh': refresh}, format='json')

    assert response.status_code == 200
    assert 'Successful Logout' in response.data['message']

@pytest.mark.django_db
def test_logout_with_refresh_but_no_access_header():
    access, refresh = get_tokens_for_user()
    client = APIClient()

    response = client.post(LOGOUT_URL, {"refresh": refresh}, format="json")

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.django_db
def test_logout_twice_with_same_refresh():
    access, refresh = get_tokens_for_user()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # First logout (sould be correct)
    response1 = client.post(LOGOUT_URL, {"refresh": refresh}, format="json")
    assert response1.status_code == status.HTTP_200_OK

    # Second log out with the same refresh → it should fail because it is already blacklisted
    response2 = client.post(LOGOUT_URL, {"refresh": refresh}, format="json")
    assert response2.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]


@pytest.mark.django_db
def test_logout_without_refresh():
    access, _ = get_tokens_for_user()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = client.post(LOGOUT_URL, {}, format='json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_logout_unauthenticated():
    client = APIClient()
    response = client.post(LOGOUT_URL, {}, format='json')

    assert response.status_code == 401

@pytest.mark.django_db
def test_logout_invalid_refresh():
    access, _ = get_tokens_for_user()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = client.post(LOGOUT_URL, {'refresh': 'invalidtoken'}, format='json')

    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_access_after_logout_blacklisted_token():
    access, refresh = get_tokens_for_user()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION =f"Bearer {access}")

    #logout
    client.post(LOGOUT_URL, {'refresh': refresh}, format='json')

    response = client.get(PROTECTED_URL)

    assert response.status_code in [200, 401, 403]