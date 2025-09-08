import pytest 
from rest_framework import status 
from posts.models import Post
from comments.models import Comment
from likes.models import Like
from users.models import Team

POST_DELETE_URL = lambda post_id: f"/api/post/{post_id}/delete/"

@pytest.mark.django_db
def test_author_can_delete_own_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test Post", content="...", edit_permission="author")

    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(id=post.id).exists()

@pytest.mark.django_db
def test_user_without_permission_cannot_delete_post(auth_client):
    client1, user1 = auth_client()
    client2, user2 = auth_client(email="other@example.com")

    post = Post.objects.create(author=user1, title="Another Post", content="...", edit_permission="author")

    response = client2.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.filter(id=post.id).exists()

@pytest.mark.django_db
def test_admin_can_delete_any_post(auth_client):
    client, admin_user = auth_client(email="admin@example.com")
    admin_user.role = "admin"
    admin_user.save()

    post_author_client, post_author = auth_client(email="author@example.com")
    post = Post.objects.create(author=post_author, title="Admin Deletes This", content="...", edit_permission="author")

    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(id=post.id).exists()

@pytest.mark.django_db
def test_delete_post_removes_associated_likes_and_comments(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="With Relations", content="...")

    Like.objects.create(user=user, post=post)
    Comment.objects.create(user=user, post=post, content="Comment to be deleted")

    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(id=post.id).exists()
    assert not Like.objects.filter(post=post).exists()
    assert not Comment.objects.filter(post=post).exists()

@pytest.mark.django_db
def test_anonymous_cannot_delete_post(client, auth_client):
    _, user = auth_client()
    post = Post.objects.create(author=user, title="Anonymous Cannot Delete", content="...")

    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Post.objects.filter(id=post.id).exists()

@pytest.mark.django_db
def test_delete_post_with_team_permission(auth_client, create_user):
    team = Team.objects.create(name="Team A")
    client_author, author = auth_client(team=team)
    post = Post.objects.create(
        author=author,
        title="Team Post",
        content="...",
        edit_permission="team"
    )

    # Same user team can delete
    client_same_team, same_team_user = auth_client(email="same@test.com", team=team)
    response = client_same_team.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # different team can't delete
    client_other_team, other_user = auth_client(email="other@test.com", team=Team.objects.create(name="Team B"))
    post2 = Post.objects.create(
        author=author,
        title="Team Post 2",
        content="...",
        edit_permission="team"
    )
    response = client_other_team.delete(POST_DELETE_URL(post2.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_post_with_authenticated_permission(auth_client):
    client_author, author = auth_client()
    post = Post.objects.create(
        author=author,
        title="Auth Post",
        content="...",
        edit_permission="authenticated"
    )

    # authenticated users can delete
    client_other, other_user = auth_client(email="other@test.com")
    response = client_other.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_post_with_public_permission(auth_client):
    client_author, author = auth_client()
    post = Post.objects.create(
        author=author,
        title="Public Post",
        content="...",
        edit_permission="public"
    )

    # anonymous user can delete it 
    client_other, other_user = auth_client(email="other@test.com")
    response = client_other.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_already_deleted_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Delete Twice", content="...")

    # First delete
    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # second delete, should raise 404
    response = client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_superuser_can_delete_any_post(auth_client, create_user):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Superuser Post", content="...")

# Admin CAN see it
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    #admin user role
    #admin.role = 'admin'
    #site admin
    admin.is_staff = True
    admin.is_superuser = True 
    admin.save()
    response = admin_client.delete(POST_DELETE_URL(post.id))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_nonexistent_post(auth_client):
    client, user = auth_client()
    response = client.delete(POST_DELETE_URL(100))  # nonexistent id
    assert response.status_code == status.HTTP_404_NOT_FOUND