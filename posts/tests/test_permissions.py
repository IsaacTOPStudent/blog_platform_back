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
    post = Post.objects.create(
        author=user,
        title="Public Post",
        content="Visible to all",
        author_access="write",
        team_access="read",
        authenticated_access="read",
        public_access="read",
    )

    client = APIClient()  # no auth
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Public Post"


@pytest.mark.django_db
def test_authenticated_user_sees_authenticated_posts(auth_client):
    _, author = auth_client(email="author@example.com")
    post = Post.objects.create(
        author=author,
        title="Auth Only",
        content="Secret",
        author_access="write",
        team_access="read",
        authenticated_access="read",
        public_access="none",
    )

    client2, _ = auth_client(email="reader@example.com")
    response = client2.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Auth Only"


@pytest.mark.django_db
def test_team_post_only_visible_to_same_team(auth_client):
    team = Team.objects.create(name="Team A")
    client1, author = auth_client(email="author@example.com", team=team)
    post = Post.objects.create(
        author=author,
        title="Team Post",
        content="For team only",
        author_access="write",
        team_access="read",
        authenticated_access="none",
        public_access="none",
    )

    # Same team → access allowed
    client2, _ = auth_client(email="mate@example.com", team=team)
    assert client2.get(POST_DETAIL_URL(post.id)).status_code == status.HTTP_200_OK

    # Different team → 404 (not visible)
    client3, _ = auth_client(email="outsider@example.com")
    assert client3.get(POST_DETAIL_URL(post.id)).status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_pagination_on_post_list(auth_client):
    client, user = auth_client()
    for i in range(15):
        Post.objects.create(
            author=user,
            title=f"Post {i}",
            content="Content",
            author_access="write",
            team_access="read",
            authenticated_access="read",
            public_access="read",
        )

    response = client.get(POST_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 15
    assert len(response.data["results"]) == 10
    assert "next" in response.data

    response1 = client.get(response.data["next"])
    assert "previous" in response1.data


@pytest.mark.django_db
def test_user_get_posts_without_permissions(auth_client, client):
    _, user = auth_client()
    for i in range(5):
        Post.objects.create(
            author=user,
            title=f"Private Post {i}",
            content="Content",
            author_access="write",
            team_access="read",
            authenticated_access="read",
            public_access="none",
        )

    # Anonymous user: should get 200 but empty list
    response = client.get(POST_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []

@pytest.mark.django_db
def test_public_post_visible_for_all(auth_client, client):
    # Create public post (visible to all)
    author_client, author = auth_client(email="author@example.com")
    post = Post.objects.create(
        author=author,
        title="Public post",
        content="Everyone can see this post",
        author_access="write",
        team_access="read",
        authenticated_access="read",
        public_access="read",
    )

    # Anonymous user
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Public post"

    # Authenticated with team
    team = Team.objects.create(name="Team A")
    client2, _ = auth_client(email="mate@example.com", team=team)
    response = client2.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK

    # Authenticated with no team
    other_client, _ = auth_client(email="other@example.com")
    response = other_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK

    # Admin can also see it
    admin_client, admin = auth_client(email="admin3@example.com", password="adminpass123")
    admin.role = "admin"
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    response = admin_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Public post"


@pytest.mark.django_db
def test_owner_only_post(auth_client, client):
    # Create owner-only post (only author and admin can see it)
    author_client, author = auth_client(email="owner@example.com")
    post = Post.objects.create(
        author=author,
        title="Private post",
        content="Only owner and admin can see it",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none",
    )

    # Author can see it
    response = author_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Private post"

    # Other authenticated user cannot see it
    other_client, _ = auth_client(email="intruder@example.com")
    response = other_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Anonymous cannot see it
    response = client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Admin CAN see it
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    admin.role = "admin"
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    response = admin_client.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Private post"

#-----------------------------------------------------------------------------------

#test about permissions hierarchy

@pytest.mark.django_db
def test_valid_permission_hierarchy(auth_client):
    client, user = auth_client()

    payload = {
        "title": "Valid Post",
        "content": "Some content",
        "author_access": "write",
        "team_access": "write",
        "authenticated_access": "read",
        "public_access": "none",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    post = Post.objects.get(id=response.data["id"])
    assert post.author_access == "write"
    assert post.team_access == "write"
    assert post.authenticated_access == "read"
    assert post.public_access == "none"


@pytest.mark.django_db
def test_invalid_choice_to_author(auth_client):
    client, user = auth_client()

    payload = {
        "title": "Invalid Team > Author",
        "content": "Team cannot exceed author",
        "author_access": "read", # invalid
        "team_access": "write",  
        "authenticated_access": "none",
        "public_access": "none",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "author_access" in response.data
    assert '"read" is not a valid choice.' in str(response.data["author_access"])

@pytest.mark.django_db
def test_invalid_authenticated_higher_than_team(auth_client):
    client, user = auth_client()

    payload = {
        "title": "Invalid Auth > Team",
        "content": "Auth cannot exceed team",
        "author_access": "write",
        "team_access": "read",
        "authenticated_access": "write",  # invalid
        "public_access": "none",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "authenticated_access" in response.data


@pytest.mark.django_db
def test_invalid_public_higher_than_authenticated(auth_client):
    client, user = auth_client()

    payload = {
        "title": "Invalid Public > Auth",
        "content": "Public cannot exceed authenticated",
        "author_access": "write",
        "team_access": "read",
        "authenticated_access": "read",
        "public_access": "write",  # invalid
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "public_access" in response.data


@pytest.mark.django_db
def test_none_permissions_allowed(auth_client):
    client, user = auth_client()

    payload = {
        "title": "No Access Post",
        "content": "Hidden from everyone",
        "author_access": "write",
        "team_access": "none",
        "authenticated_access": "none",
        "public_access": "none",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    post = Post.objects.get(id=response.data["id"])
    assert post.author_access == "write"
    assert post.team_access == "none"
    assert post.authenticated_access == "none"
    assert post.public_access == "none"

@pytest.mark.django_db
def test_invalid_choice_to_public(auth_client):
    client, user = auth_client()

    payload = {
        "title": "No Access Post",
        "content": "Hidden from everyone",
        "author_access": "write",
        "team_access": "none",
        "authenticated_access": "none",
        "public_access": "write",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "public_access" in response.data
    assert '"write" is not a valid choice.' in str(response.data["public_access"])