import pytest 
from rest_framework import status
from posts.models import Post 
from likes.models import Like
from users.models import Team

LIKE_URL = lambda post_id: f'/api/post/{post_id}/like/'

@pytest.mark.django_db
def test_authenticated_user_can_like_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Post content", read_permission="public")

    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.filter(user=user, post=post).exists()

@pytest.mark.django_db
def test_prevent_multiple_likes(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Post content", read_permission="public")

    # First like
    response1 = client.post(LIKE_URL(post.id))
    assert response1.status_code == status.HTTP_201_CREATED
    # Second like should fail
    response2 = client.post(LIKE_URL(post.id))
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert Like.objects.filter(user=user, post=post).count() == 1

@pytest.mark.django_db
def test_anonymous_user_cannot_like_post(client, auth_client):
    # anonymous client
    _, user = auth_client()
    post = Post.objects.create(author=user, title="Anon test", content="Only auth can like", read_permission="public")

    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Like.objects.count() == 0

@pytest.mark.django_db
def test_user_can_unlike_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Post content", read_permission="public")

    # Like
    client.post(LIKE_URL(post.id))
    assert Like.objects.filter(user=user, post=post).exists()

    # Unlike
    response = client.delete(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Like.objects.filter(user=user, post=post).exists()

@pytest.mark.django_db
def test_user_must_have_view_access_to_like(auth_client):
    # Create author in one team
    team_a = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@test.com", team=team_a)
    post = Post.objects.create(author=user1, title="Private", content="Owner only", read_permission="team")

    # Different user in another team
    team_b = Team.objects.create(name="Team B")
    client2, user2 = auth_client(email="intruder@test.com", team=team_b)

    response = client2.post(LIKE_URL(post.id))
    # no access → 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Like.objects.count() == 0

@pytest.mark.django_db
def test_prevent_unlike_on_unliked_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Post content", read_permission="public")

    # removing a like on an unliked post should fail
    response1 = client.delete(LIKE_URL(post.id))
    assert response1.status_code == status.HTTP_400_BAD_REQUEST
    assert response1.data['detail'] == "You have not liked this post."

@pytest.mark.django_db
def test_like_in_post_only_see_author(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Post content", read_permission="author")

    client2, _ = auth_client(email="intruder@test.com")
    response = client2.post(LIKE_URL(post.id))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Like.objects.count() == 0

    response = client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED

    # Admin CAN see it
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    #admin user role
    admin.role = 'admin'
    #site admin
    #admin.is_staff = True
    #admin.is_superuser = True 
    admin.save()
    response = admin_client.post(LIKE_URL(post.id))
    assert response.status_code == status.HTTP_201_CREATED
