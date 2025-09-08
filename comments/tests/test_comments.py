import pytest
from rest_framework import status
from posts.models import Post
from comments.models import Comment
from users.models import User, Team

COMMENTS_LIST_URL = lambda post_id: f'/api/post/{post_id}/comment/'
COMMENT_DELETE_URL = lambda comment_id: f'/api/comment/{comment_id}/'

@pytest.mark.django_db
def test_authenticated_user_can_comment_post(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    payload = {"content": "Great post!"}
    response = client.post(COMMENTS_LIST_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Comment.objects.filter(user=user, post=post, content="Great post!").exists()
    assert response.data['post'] == post.title


@pytest.mark.django_db
def test_anonymous_user_cannot_comment_post(client, auth_client):
    _, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    payload = {"content": "I should not be able to comment"}
    response = client.post(COMMENTS_LIST_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_without_access_cannot_comment(auth_client):
    team_a = Team.objects.create(name="Team A")
    team_b = Team.objects.create(name="Team B")

    client1, user1 = auth_client(email="author@test.com", team=team_a)
    post = Post.objects.create(author=user1, title="Private", content="Owner only", read_permission="author")

    client2, _ = auth_client(email="intruder@test.com", team=team_b)
    payload = {"content": "Trying to comment without access"}
    response = client2.post(COMMENTS_LIST_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_can_delete_own_comment(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    comment = Comment.objects.create(user=user, post=post, content="My comment")
    response = client.delete(COMMENT_DELETE_URL(comment.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cannot_delete_others_comment(auth_client):
    client1, user1 = auth_client()
    post = Post.objects.create(author=user1, title="Test", content="Content", read_permission="public")

    comment = Comment.objects.create(user=user1, post=post, content="Author's comment")

    client2, _ = auth_client(email="other@test.com")
    response = client2.delete(COMMENT_DELETE_URL(comment.id))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_admin_can_delete_any_comment(auth_client):
    client1, user1 = auth_client()
    post = Post.objects.create(author=user1, title="Test", content="Content", read_permission="public")

    comment = Comment.objects.create(user=user1, post=post, content="Comment to delete")

    client_admin, admin = auth_client(email="admin@test.com", password="adminpass123")
    admin.role = 'admin'
    admin.is_staff = True
    admin.is_superuser = True 
    admin.save()

    response = client_admin.delete(COMMENT_DELETE_URL(comment.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(id=comment.id).exists()

@pytest.mark.django_db
def test_cannot_post_empty_comment(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    payload = {"content": "   "}  # only spaces
    response = client.post(COMMENTS_LIST_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"--> {response.data}")
    assert "Comment cannot be empty." in str(response.data)


@pytest.mark.django_db
def test_comment_too_long(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    payload = {"content": "a" * 2501}  # limit 2500 chars
    response = client.post(COMMENTS_LIST_URL(post.id), payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_nonexistent_comment(auth_client):
    client, user = auth_client()
    # trying to delete a non-existent comment
    response = client.delete(COMMENT_DELETE_URL(9999))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_on_nonexistent_post(auth_client):
    client, user = auth_client()
    payload = {"content": "Trying to comment on ghost post"}
    response = client.post(COMMENTS_LIST_URL(5), payload, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_can_post_multiple_comments(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    payload1 = {"content": "First comment"}
    payload2 = {"content": "Second comment"}

    response1 = client.post(COMMENTS_LIST_URL(post.id), payload1, format="json")
    response2 = client.post(COMMENTS_LIST_URL(post.id), payload2, format="json")

    assert response1.status_code == status.HTTP_201_CREATED
    assert response2.status_code == status.HTTP_201_CREATED
    assert Comment.objects.filter(post=post, user=user).count() == 2


@pytest.mark.django_db
def test_comments_deleted_when_user_deleted(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title="Test", content="Content", read_permission="public")

    comment = Comment.objects.create(user=user, post=post, content="Will vanish")

    # delete the user
    user.delete()

    # comment should be deleted
    assert Comment.objects.filter(id=comment.id).count() == 0