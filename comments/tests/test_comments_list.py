import pytest 
from rest_framework import status 
from comments.models import Comment
from posts.models import Post
from users.models import Team

COMMENTS_LIST_URL = lambda post_id: f"/api/post/{post_id}/comments/"

@pytest.mark.django_db
def test_list_comments_for_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    Comment.objects.create(user=user, post=post, content="First comment")
    Comment.objects.create(user=user, post=post, content="Second comment")

    response = client.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert "user" in response.data["results"][0]
    assert "created_at" in response.data["results"][0]


@pytest.mark.django_db
def test_filter_comments_by_user(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    other_user_client, other_user = auth_client(email="other@test.com")
    Comment.objects.create(user=user, post=post, content="By author")
    Comment.objects.create(user=other_user, post=post, content="By other")

    response = client.get(COMMENTS_LIST_URL(post.id) + f"?user_id={other_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["user"] == other_user.username


@pytest.mark.django_db
def test_user_without_access_cannot_view_comments(auth_client):
    team_a = Team.objects.create(name="Team A")
    team_b = Team.objects.create(name="Team B")

    client1, user1 = auth_client(team=team_a)
    post = Post.objects.create(author=user1, title="Private", content="Hidden", read_permission="author")

    Comment.objects.create(user=user1, post=post, content="Secret comment")

    client2, _ = auth_client(team=team_b)
    response = client2.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comments_are_paginated(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Paginated Post", content="Content", read_permission="public")

    # make 15 comments
    for i in range(15):
        Comment.objects.create(user=user, post=post, content=f"Comment {i}")

    response = client.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10  # límite de la paginación
    assert "count" in response.data
    assert "next" in response.data
    assert "previous" in response.data

    # Check second page
    response_page_2 = client.get(COMMENTS_LIST_URL(post.id) + "?page=2")
    assert response_page_2.status_code == status.HTTP_200_OK
    assert len(response_page_2.data["results"]) == 5

@pytest.mark.django_db
def test_empty_comments_list(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Empty Post", content="No comments", read_permission="public")

    response = client.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_filter_by_nonexistent_user(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Filter Test", content="...", read_permission="public")

    Comment.objects.create(user=user, post=post, content="Valid comment")

    response = client.get(COMMENTS_LIST_URL(post.id) + "?user_id=9999")  # ID inexistente
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_anonymous_can_view_public_post(client, auth_client):
    _, user = auth_client()
    post = Post.objects.create(author=user, title="Public Post", content="...", read_permission="public")

    Comment.objects.create(user=user, post=post, content="Hello world")

    response = client.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_anonymous_cannot_view_private_post(client, auth_client):
    _, user = auth_client()
    post = Post.objects.create(author=user, title="Private Post", content="...", read_permission="author")

    Comment.objects.create(user=user, post=post, content="Hidden comment")

    response = client.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_combined_filters(auth_client):
    client, user = auth_client()
    other_client, other_user = auth_client(email="other@example.com")

    post = Post.objects.create(author=user, title="Combined Filters", content="...", read_permission="public")

    Comment.objects.create(user=user, post=post, content="Author comment")
    Comment.objects.create(user=other_user, post=post, content="Other user comment")

    # filter by author id
    response = client.get(COMMENTS_LIST_URL(post.id) + f"?user_id={user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"] == user.username


@pytest.mark.django_db
def test_user_from_other_team_can_view_public_post(auth_client):
    team_a = Team.objects.create(name="Team A")
    team_b = Team.objects.create(name="Team B")

    client1, user1 = auth_client(team=team_a)
    client2, user2 = auth_client(email="other@example.com", team=team_b)

    post = Post.objects.create(author=user1, title="Cross-team", content="Visible", read_permission="public")

    Comment.objects.create(user=user1, post=post, content="Team A comment")

    response = client2.get(COMMENTS_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_invalid_user_id_param(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Invalid Param Test", content="...", read_permission="public")

    Comment.objects.create(user=user, post=post, content="Valid comment")

    response = client.get(COMMENTS_LIST_URL(post.id) + "?user_id=abc")  # invalid value
    # Bad request
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'user_id' in response.data