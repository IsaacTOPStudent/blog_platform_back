import pytest
from likes.serializers import LikeSerializer
from likes.models import Like
from posts.models import Post

@pytest.mark.django_db
def test_like_serializer_returns_expected_fields(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Post 1", content="Content")
    like = Like.objects.create(user=user, post=post)

    serializer = LikeSerializer(instance=like)
    data = serializer.data

    assert set(data.keys()) == {"id", "user", "created_at"}
    assert data["user"] == user.username
    assert isinstance(data["id"], int)
    assert data["created_at"] is not None


@pytest.mark.django_db
def test_like_serializer_user_is_readonly(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Post 1", content="Content")

    payload = {"user": "hacker", "post": post.id}
    serializer = LikeSerializer(data=payload)

    # No debería aceptar 'user' porque es read-only
    assert serializer.is_valid(), serializer.errors
    assert "user" not in serializer.validated_data


@pytest.mark.django_db
def test_like_serializer_invalid_without_instance(create_user):
    """For serializer without instance and missing required fields"""
    payload = {}
    serializer = LikeSerializer(data=payload)

# is_valid() will be true because the Like model is created from the view,
# but user/post must be assigned in the logic, not in the serializer.
    assert serializer.is_valid()
    # Manual saving fails because required fields are missing
    with pytest.raises(Exception):
        serializer.save()


@pytest.mark.django_db
def test_like_serializer_with_instance(create_user):
    """Check that serializer works correctly with an existing instance"""
    user = create_user(email="test@example.com")
    post = Post.objects.create(author=user, title="Title", content="Content")
    like = Like.objects.create(user=user, post=post)

    serializer = LikeSerializer(like)
    assert serializer.data["user"] == user.username