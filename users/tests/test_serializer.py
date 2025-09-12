import pytest
from users.serializers import RegisterSerializer, EmailAuthTokenSerializer, UserSerializer, TeamSerializer
from users.models import Team
from django.contrib.auth import get_user_model

UserModel = get_user_model()

# Tests for RegisterSerializer
@pytest.mark.django_db
def test_register_serializer_creates_user_with_default_team():
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "strongpass123"
    }
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()

    assert UserModel.objects.count() == 1
    assert user.email == "newuser@example.com"
    assert user.check_password("strongpass123")
    assert user.team.name == "Default Team"


@pytest.mark.django_db
def test_register_serializer_rejects_duplicate_email():
    UserModel.objects.create_user(email="dup@example.com", password="pass123")

    data = {
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "pass456"
    }
    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0] == "user with this email already exists."


@pytest.mark.django_db
def test_register_serializer_password_min_length():
    data = {
        "username": "shortpass",
        "email": "shortpass@example.com",
        "password": "123"  # too short
    }
    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid()
    assert "password" in serializer.errors


# Tests for EmailAuthTokenSerializer
@pytest.mark.django_db
def test_email_auth_token_serializer_valid_credentials():
    user = UserModel.objects.create_user(email="auth@example.com", password="authpass123")

    serializer = EmailAuthTokenSerializer(
        data={"email": "auth@example.com", "password": "authpass123"},
        context={"request": None}
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"] == user


@pytest.mark.django_db
def test_email_auth_token_serializer_invalid_credentials():
    UserModel.objects.create_user(email="bad@example.com", password="goodpass123")

    serializer = EmailAuthTokenSerializer(
        data={"email": "bad@example.com", "password": "wrongpass"},
        context={"request": None}
    )
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors or "email" in serializer.errors


@pytest.mark.django_db
def test_email_auth_token_serializer_missing_fields():
    serializer = EmailAuthTokenSerializer(data={"email": "missing@example.com"})
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors or "password" in serializer.errors

@pytest.mark.django_db
def test_user_serializer_includes_team():
    team = Team.objects.create(name="Team Test")
    user = UserModel.objects.create_user(email="teamuser@example.com", password="pass123", team=team)

    serializer = UserSerializer(user)
    data = serializer.data
    assert data["email"] == "teamuser@example.com"
    assert data["team"]["name"] == "Team Test"


@pytest.mark.django_db
def test_team_serializer_output():
    team = Team.objects.create(name="Frontend Team")
    serializer = TeamSerializer(team)
    data = serializer.data
    assert data["name"] == "Frontend Team"
    assert "id" in data