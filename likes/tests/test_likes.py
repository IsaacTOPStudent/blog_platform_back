import pytest 
from rest_framework import status
from posts.models import Post 
from likes.models import Like
from users.models import Team

LIKE_URL = lambda post_id: f'/api/post/{post_id}/like/'

@pytest.mark.django_db
def test_authenticated_user_can_like_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Post content",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.filter(user=user, post=post).exists()


@pytest.mark.django_db
def test_prevent_multiple_likes(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Post content",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    # First like
    response1 = client.post(LIKE_URL(post.id))
    assert response1.status_code == status.HTTP_201_CREATED

    # Second like should fail
    response2 = client.post(LIKE_URL(post.id))
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert Like.objects.filter(user=user, post=post).count() == 1


@pytest.mark.django_db
def test_anonymous_user_cannot_like_post(client, auth_client):
    _, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Anon test",
        content="Only auth can like",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Like.objects.count() == 0


@pytest.mark.django_db
def test_user_can_unlike_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Post content",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    # Like
    client.post(LIKE_URL(post.id))
    assert Like.objects.filter(user=user, post=post).exists()

    # Unlike
    response = client.delete(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Like.objects.filter(user=user, post=post).exists()


@pytest.mark.django_db
def test_user_must_have_view_access_to_like(auth_client):
    team_a = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@test.com", team=team_a)
    post = Post.objects.create(
        author=user1,
        title="Private",
        content="Owner or team only",
        author_access="write",
        team_access="read",   
        authenticated_access="none",
        public_access="none"
    )

    team_b = Team.objects.create(name="Team B")
    client2, _ = auth_client(email="intruder@test.com", team=team_b)

    response = client2.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Like.objects.count() == 0
    client3, _ =auth_client(email='sameteam@test.com', team=team_a)

    response1 = client3.post(LIKE_URL(post.id))
    assert response1.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 1


@pytest.mark.django_db
def test_prevent_unlike_on_unliked_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Post content",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    # Removing a like on an unliked post should fail
    response = client.delete(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "You have not liked this post."


@pytest.mark.django_db
def test_like_in_post_only_visible_to_author_or_admin(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Post content",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none"
    )

    # Other user cannot like
    client2, _ = auth_client(email="intruder@test.com")
    response = client2.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Like.objects.count() == 0

    # Author can like
    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED

    # Admin can like
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    admin.role = "admin"
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    response = admin_client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED