import pytest 
from rest_framework.test import APIClient
from rest_framework import status
from posts.models import Post
from users.models import Team

POST_UPDATE_URL = lambda pk: f"/api/blog/{pk}/"

@pytest.mark.django_db
def test_edit_post_only_author(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="something",
        content="something content here",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none",
    )
    payload = {"title": "New interesting title", "content": "New interesting content"}
    response = client.put(POST_UPDATE_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == "New interesting title"
    assert post.content == "New interesting content"


@pytest.mark.django_db
def test_edit_post_forbidden_for_other_user(auth_client, client):
    team = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@example.com", team=team)
    post = Post.objects.create(
        author=user1,
        title="No Edit",
        content="Cannot edit here",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none",
    )

    payload = {"title": "content hacked"}

    # other auth user
    client2, _ = auth_client(email="intruder@example.com")
    response = client2.put(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # anonymous
    response = client.put(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # same team user, but no edit permission
    client3, _ = auth_client(email="mate@example.com", team=team)
    response = client3.put(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_with_same_team_as_author_can_edit(auth_client):
    team = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@example.com", team=team)
    post = Post.objects.create(
        author=user1,
        title="Can Edit",
        content="Team can edit here",
        author_access="write",
        team_access="write", 
        authenticated_access="read",
        public_access="none",
    )

    payload = {"title": "content hacked", "content": "new content here"}

    # same team user can edit it
    client2, _ = auth_client(email="teammate@example.com", team=team)
    response = client2.put(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == "content hacked"

    # admin can edit anything post
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    admin.role = "admin"
    admin.save()

    response = admin_client.put(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_200_OK
