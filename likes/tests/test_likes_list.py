import pytest 
from rest_framework import status
from posts.models import Post 
from likes.models import Like
from users.models import Team

LIKES_LIST_URL = lambda post_id: f'/api/post/{post_id}/likes/'

@pytest.mark.django_db
def test_list_likes_on_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Content",
        team_access='read',
        authenticated_access='read',
        public_access="read"  
    )

    # create 3 likes
    for i in range(3):
        _, other_user = auth_client(email=f"user{i}@test.com")
        Like.objects.create(user=other_user, post=post)

    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_filter_likes_by_user(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Test",
        content="Content",
        team_access='read',
        authenticated_access='read',
        public_access="read"
    )

    # like for this user
    Like.objects.create(user=user, post=post)

    # other user 
    _, user2 = auth_client(email="other@test.com")
    Like.objects.create(user=user2, post=post)

    response = client.get(LIKES_LIST_URL(post.id) + f"?user_id={user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"] == user.username


@pytest.mark.django_db
def test_filter_likes_by_post(auth_client):
    client, user = auth_client()
    post1 = Post.objects.create(
        author=user, title="Test1", content="Content1", public_access="read", authenticated_access ='read',
        team_access = 'read'
    )
    post2 = Post.objects.create(
        author=user, title="Test2", content="Content2", public_access="read", authenticated_access ='read',
        team_access = 'read'
    )

    # Likes on both posts
    Like.objects.create(user=user, post=post1)
    _, user2 = auth_client(email="other@test.com")
    Like.objects.create(user=user2, post=post2)

    # only post 1 likes
    response = client.get(LIKES_LIST_URL(post1.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"] == user.username


@pytest.mark.django_db
def test_cannot_view_likes_without_permission(auth_client):
    team_a = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email="author@test.com", team=team_a)
    post = Post.objects.create(
        author=user1,
        title="Private",
        content="Owner only",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none"
    )

    team_b = Team.objects.create(name="Team B")
    client2, _ = auth_client(email="intruder@test.com", team=team_b)

    response = client2.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_pagination_likes(auth_client):
    client, user = auth_client()
    post = Post.objects.create(
        author=user,
        title="Paginated",
        content="Test",
        authenticated_access='read',
        team_access='read',
        public_access="read"
    )

    for i in range(25):
        _, other_user = auth_client(email=f"user{i}@test.com")
        Like.objects.create(user=other_user, post=post)

    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None

    # second page
    response_page2 = client.get(LIKES_LIST_URL(post.id) + "?page=2")
    assert len(response_page2.data["results"]) == 5


@pytest.mark.django_db
def test_anonymous_user_can_view_likes_on_public_post(client, auth_client):
    # auth user makes a post
    _, author = auth_client(email="author@test.com")
    post = Post.objects.create(
        author=author,
        title="Public Post",
        content="Anyone can see",
        authenticated_access='read',
        team_access='read',
        public_access="read"
    )

    # other user liked it
    _, liker = auth_client(email="liker@test.com")
    Like.objects.create(user=liker, post=post)

    # anonymous user can view these likes
    response = client.get(LIKES_LIST_URL(post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1