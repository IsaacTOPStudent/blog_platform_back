import pytest 
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Team
from posts.models import Post

POST_LIST_URL = '/api/post/'
POST_DETAIL_URL = lambda pk: f"/api/post/{pk}/"

@pytest.mark.django_db
def test_public_post_visible_to_anonymous(create_user):
    user = create_user(email="author@example.com")
    post = Post.objects.create(author=user, title="Public Post", content="Visible to all", read_permission="public", edit_permission="author")

    client = APIClient()  # no auth
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_authenticated_user_sees_authenticated_posts(auth_client):
    _, author = auth_client(email="author@example.com")
    post = Post.objects.create(author=author, title="Auth Only", content="Secret", read_permission="authenticated", edit_permission="author")

    client2, _ = auth_client(email="reader@example.com")
    response = client2.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_team_post_only_visible_to_same_team(auth_client):
    team = Team.objects.create(name="Team A")
    client1, author = auth_client(email="author@example.com", team=team)
    post = Post.objects.create(author=author, title="Team Post", content="For team only", read_permission="team", edit_permission="author")

    client2, _ = auth_client(email="mate@example.com", team=team)
    assert client2.get(POST_DETAIL_URL(post.id)).status_code == status.HTTP_200_OK

    client3, _ = auth_client(email="outsider@example.com")
    assert client3.get(POST_DETAIL_URL(post.id)).status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_pagination_on_post_list(auth_client):
    client, user = auth_client()
    for i in range(15):
        Post.objects.create(author=user, title=f"Post {i}", content="Content", read_permission="public", edit_permission="author")

    response = client.get(POST_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 15
    assert len(response.data["results"]) == 10
    assert "next" in response.data
    response1 = client.get(response.data['next']) 
    assert "previous" in response1.data

@pytest.mark.django_db
def test_user_get_posts_without_permissions(auth_client, client):
    _, user = auth_client()
    for i in range(15):
        Post.objects.create(author=user, title=f"Post {i}", content="Content", read_permission="authenticated", edit_permission="author")
    # anonymous user: should get 200 but empty list
    response = client.get(POST_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []
    

@pytest.mark.django_db
def test_public_post_visible_for_all(auth_client, client):
    # Create public post
    author_client, author = auth_client(email="author@example.com")
    post = Post.objects.create(
        author=author,
        title="Public post",
        content="Everyone can see this post",
        read_permission="public",
        edit_permission="author",
    )

    # anonymous user
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Public post"

    #Authenticated with team
    team = Team.objects.create(name="Team A")

    client2, _ = auth_client(email="mate@example.com", team=team)
    response = client2.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK

    # user authenticated with default team
    other_client, _ = auth_client(email="other@example.com")
    response = other_client.get(POST_DETAIL_URL(post.id))

    assert response.status_code == status.HTTP_200_OK

    admin_client, admin = auth_client(email="admin3@example.com", password="admi3npass123")
    admin.role = 'admin'
    admin.is_staff = True
    admin.is_superuser = True 
    admin.save()
    response = admin_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Public post"

@pytest.mark.django_db
def test_owner_only_post(auth_client, client):
    # Create post owner-only
    author_client, author = auth_client(email="owner@example.com")
    post = Post.objects.create(
        author=author,
        title="Private post",
        content="Only owner and admin can see it ",
        read_permission="author",
        edit_permission="author",
    )

    # The author can see it
    response = author_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Private post"

    # Other authenticated user cannot see it
    other_client, _ = auth_client(email="intruder@example.com")
    response = other_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Anonymous can't see it either.
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Admin CAN see it

    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    #admin user role
    admin.role = 'admin'
    #site admin
    #admin.is_staff = True
    #admin.is_superuser = True 
    admin.save()
    response = admin_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Private post"