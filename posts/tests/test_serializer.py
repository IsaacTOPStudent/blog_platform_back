import pytest
from posts.models import Post
from posts.serializers import PostSerializer, PostDetailSerializer, PostUpdateSerializer


@pytest.mark.django_db
def test_post_serializer_valid(create_user):
    user = create_user(username="author1")
    post = Post.objects.create(
        author=user,
        title="Test Post",
        content="Content example",
        authenticated_access='read',
        team_access='read',
        public_access="read"
    )

    serializer = PostSerializer(post)

    data = serializer.data
    assert data["title"] == "Test Post"
    assert data["author"] == user.username  
    assert "created_at" in data
    assert data["public_access"] == "read"
    assert data["authenticated_access"] == "read"
    assert data["team_access"] == "read"
    assert data["author_access"] == "write"


@pytest.mark.django_db
def test_post_serializer_invalid_permissions(create_user):
    user = create_user()
    post = Post(author=user, title="Bad Post", content="Invalid perms")

    data = {
        "title": "Invalid Post",
        "content": "Testing wrong hierarchy",
        "author_access": "read",
        "team_access": "write",
        "authenticated_access": "write",
        "public_access": "write",  
    }

    serializer = PostSerializer(instance=post, data=data)
    assert not serializer.is_valid()
    assert "public_access" in serializer.errors


@pytest.mark.django_db
def test_author_field_is_readonly(create_user):
    user = create_user(username="original_author")
    post = Post.objects.create(author=user, title="ReadOnly", content="...")

    new_user = create_user(username="hacker")
    data = {"author": new_user.username, "title": "Modified Title", "content": "..."}

    serializer = PostSerializer(instance=post, data=data, partial=True)
    assert serializer.is_valid()
    updated_post = serializer.save()

    assert updated_post.author == user  
    assert updated_post.title == "Modified Title"


@pytest.mark.django_db
def test_post_detail_serializer(create_user):
    user = create_user(username="detailuser")
    post = Post.objects.create(author=user, title="Detail Post", content="Testing detail")

    serializer = PostDetailSerializer(post)
    data = serializer.data

    assert data["title"] == "Detail Post"
    assert data["author"] == str(user)  
    assert "created_at" in data
    assert "update_at" in data


@pytest.mark.django_db
def test_post_update_serializer_respects_validation(create_user):
    user = create_user()
    post = Post.objects.create(
        author=user,
        title="Updatable",
        content="...",
        author_access="write",
        team_access="read",
        authenticated_access="none",
        public_access="none"
    )

    data = {
        "team_access": "write",
        "authenticated_access": "write",  
        "public_access": "read",
    }

    serializer = PostUpdateSerializer(instance=post, data=data, partial=True)
    assert serializer.is_valid()
    assert "authenticated_access" in serializer.data