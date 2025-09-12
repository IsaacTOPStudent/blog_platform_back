import pytest
from comments.serializers import CommentSerializer
from comments.models import Comment
from posts.models import Post

@pytest.mark.django_db
def test_valid_comment_serialization(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Test Post", content="Post content")

    comment = Comment.objects.create(user=user, post=post, content="Nice post!")
    serializer = CommentSerializer(comment)

    data = serializer.data
    assert data["content"] == "Nice post!"
    assert data["user"] == user.username
    assert data["post"] == post.title
    assert "created_at" in data


@pytest.mark.django_db
def test_serializer_rejects_empty_comment(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Test Post", content="Post content")

    serializer = CommentSerializer(data={"content": "   "})
    assert not serializer.is_valid()
    assert "content" in serializer.errors
    assert serializer.errors["content"][0] == "Comment cannot be empty."


@pytest.mark.django_db
def test_serializer_rejects_comment_too_long(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Test Post", content="Post content")

    long_text = "x" * 2501
    serializer = CommentSerializer(data={"content": long_text})
    assert not serializer.is_valid()
    assert "content" in serializer.errors
    assert serializer.errors["content"][0] == "Comment cannot exceed 2500 characters"


@pytest.mark.django_db
def test_serializer_accepts_valid_comment(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Test Post", content="Post content")

    serializer = CommentSerializer(data={"content": "This is valid"})
    assert serializer.is_valid(), serializer.errors
    validated_data = serializer.validated_data
    assert validated_data["content"] == "This is valid"


@pytest.mark.django_db
def test_read_only_fields_are_enforced(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Test Post", content="Post content")

    payload = {
        "content": "Trying to override",
        "user": "intrude",
        "post": "Fake Post"
    }

    serializer = CommentSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors 
    validated_data = serializer.validated_data
    assert "user" not in validated_data
    assert "post" not in validated_data