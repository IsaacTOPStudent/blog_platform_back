import pytest
from django.db import IntegrityError
from users.models import User, Team

@pytest.mark.django_db
def test_create_team():
    team = Team.objects.create(name="Team A")
    assert Team.objects.count() == 1
    assert str(team) == "Team A"

@pytest.mark.django_db
def test_create_user_with_default_team():
    user = User.objects.create_user(email="user1@example.com", password="pass123")
    assert user.team is not None
    assert user.check_password("pass123")
    assert user.role == "blogger"
    assert str(user).startswith("user1") or str(user).startswith("user1@example.com")

@pytest.mark.django_db
def test_create_user_with_custom_team():
    team = Team.objects.create(name="Custom Team")
    user = User.objects.create_user(email="user2@example.com", password="pass123", team=team)
    assert user.team == team
    assert user.email == "user2@example.com"

@pytest.mark.django_db
def test_email_uniqueness():
    User.objects.create_user(email="unique@example.com", password="pass123")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="unique@example.com", password="pass123")

@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(email="admin@example.com", password="admin123")
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.role == "admin"
    assert str(admin) == f"{admin.username if admin.username else admin.email} (admin)"

@pytest.mark.django_db
def test_unique_username_per_team():
    team = Team.objects.create(name="Same Team")
    User.objects.create_user(email="userA@example.com", password="pass123", username="duplicate", team=team)
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="userB@example.com", password="pass123", username="duplicate", team=team)

@pytest.mark.django_db
def test_same_username_different_teams():
    team1 = Team.objects.create(name="Team 1")
    team2 = Team.objects.create(name="Team 2")

    user1 = User.objects.create_user(email="u1@example.com", password="pass123", username="same", team=team1)
    user2 = User.objects.create_user(email="u2@example.com", password="pass123", username="same", team=team2)

    assert user1.username == user2.username == "same"
    assert user1.team != user2.team

@pytest.mark.django_db
def test_user_str_method_with_and_without_username():
    team = Team.objects.create(name="Team X")
    user_with_username = User.objects.create_user(email="with@example.com", password="pass123", username="withname", team=team)
    user_without_username = User.objects.create_user(email="without@example.com", password="pass123", username=None, team=team)

    assert str(user_with_username) == "withname (blogger)"
    assert str(user_without_username) == "without@example.com (blogger)"