import pytest
from django.core.exceptions import ValidationError
from posts.models import Post

@pytest.mark.django_db
def test_excerpt_is_generated(create_user):
    user = create_user()
    long_content = "x" * 500
    post = Post.objects.create(
        author=user,
        title="Excerpt Test",
        content=long_content,
    )
    assert post.excerpt == long_content[:200]
    assert len(post.excerpt) <= 200


@pytest.mark.django_db
def test_str_method_returns_title_and_author(create_user):
    user = create_user(email="author@example.com")
    post = Post.objects.create(
        author=user,
        title="Hello World",
        content="Some content",
    )
    assert str(post) == f"Hello World ({user})"


@pytest.mark.django_db
def test_likes_count_default(create_user):
    user = create_user()
    post = Post.objects.create(
        author=user,
        title="Likes Test",
        content="Some content"
    )
    assert post.likes_count == 0


@pytest.mark.django_db
def test_invalid_public_access_choice(create_user):
    user = create_user()
    post = Post(
        author=user,
        title="Invalid Test",
        content="Content",
        public_access="write"  
    )
    with pytest.raises(ValidationError):
        post.full_clean()  

@pytest.mark.django_db
def test_invalid_author_access_choice(create_user):
    user = create_user()
    post = Post(
        author=user,
        title="Invalid Test",
        content="Content",
        author_access="none"  
    )
    with pytest.raises(ValidationError):
        post.full_clean()  


@pytest.mark.django_db
def test_ordering_by_created_at(create_user):
    user = create_user()
    post1 = Post.objects.create(author=user, title="First", content="...")
    post2 = Post.objects.create(author=user, title="Second", content="...")

    posts = list(Post.objects.all())
    assert posts[0] == post2
    assert posts[1] == post1

@pytest.mark.django_db
def test_post_has_author(create_user):
    user = create_user(email="author@test.com")
    post = Post.objects.create(
        author=user,
        title="Post with Author",
        content="Testing foreign key",
    )

    assert post.author == user
    assert user.posts.count() == 1
    assert user.posts.first().title == "Post with Author"


@pytest.mark.django_db
def test_update_at_changes_on_update(create_user):
    user = create_user()
    post = Post.objects.create(
        author=user,
        title="Original Title",
        content="Original content",
    )

    old_update_at = post.update_at

    post.title = "Updated Title"
    post.save()

    post.refresh_from_db()

    assert post.title == "Updated Title"
    assert post.update_at > old_update_at 