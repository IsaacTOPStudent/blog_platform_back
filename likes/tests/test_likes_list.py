import pytest 
from rest_framework import status
from posts.models import Post 
from likes.models import Like
from users.models import Team

LIKES_LIST_URL = lambda post_id: f'/api/post/{post_id}/likes/'

@pytest.mark.django_db
def test_list_likes_on_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    # Crear varios likes
    for i in range(3):
        other_client, other_user = auth_client(email=f"user{i}@test.com")
        Like.objects.create(user=other_user, post=post)

    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_filter_likes_by_user(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    # like de este user
    Like.objects.create(user=user, post=post)

    # otro user
    _, user2 = auth_client(email="other@test.com")
    Like.objects.create(user=user2, post=post)

    response = client.get(LIKES_LIST_URL(post.id) + f"?user_id={user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"]["id"] == user.id

@pytest.mark.django_db
def test_filter_likes_by_post(auth_client):
    client, user = auth_client()
    post1 = Post.objects.create(author=user, title="Test1", content="Content1", read_permission="public")
    post2 = Post.objects.create(author=user, title="Test2", content="Content2", read_permission="public")

    # Likes en ambos posts
    Like.objects.create(user=user, post=post1)
    _, user2 = auth_client(email="other@test.com")
    Like.objects.create(user=user2, post=post2)

    # Pedimos solo los likes de post1
    response = client.get(LIKES_LIST_URL(post1.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"]["id"] == user.id

@pytest.mark.django_db
def test_cannot_view_likes_without_permission(auth_client):
    team_a = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@test.com", team=team_a)
    post = Post.objects.create(author=user1, title="Private", content="Owner only", read_permission="author")

    team_b = Team.objects.create(name="Team B")
    client2, user2 = auth_client(email="intruder@test.com", team=team_b)

    response = client2.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_pagination_likes(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Paginated", content="Test", read_permission="public")

    for i in range(25):
        _, other_user = auth_client(email=f"user{i}@test.com")
        Like.objects.create(user=other_user, post=post)

    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None

    # Segunda página
    response_page2 = client.get(LIKES_LIST_URL(post.id) + "?page=2")
    assert len(response_page2.data["results"]) == 5


@pytest.mark.django_db
def test_anonymous_user_can_view_likes_on_public_post(client, auth_client):
    # autor autenticado crea post público
    _, author = auth_client(email="author@test.com")
    post = Post.objects.create(author=author, title="Public Post", content="Anyone can see", read_permission="public")

    # otro user da like
    _, liker = auth_client(email="liker@test.com")
    Like.objects.create(user=liker, post=post)

    # usuario anónimo intenta ver los likes
    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1