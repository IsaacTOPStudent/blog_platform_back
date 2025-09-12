import pytest
from django.db import IntegrityError
from posts.models import Post
from likes.models import Like


@pytest.mark.django_db
def test_user_can_like_post_once(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Post 1", content="Content")

    Like.objects.create(user=user, post=post)

    with pytest.raises(IntegrityError):
        Like.objects.create(user=user, post=post)

@pytest.mark.django_db
def test_like_str_representation(create_user):
    user = create_user(email="tester@test.com")
    post = Post.objects.create(author=user, title="My Awesome Post", content="Content")
    like = Like.objects.create(user=user, post=post)

    result = str(like)
    assert user.email in result
    assert post.title[:30] in result


@pytest.mark.django_db
def test_like_ordering(create_user):
    user = create_user(email="order@test.com")
    post = Post.objects.create(author=user, title="Order Test", content="Content")

    like1 = Like.objects.create(user=user, post=post)
    other_user = create_user(email="second@test.com")
    like2 = Like.objects.create(user=other_user, post=post)

    likes = list(Like.objects.all())
    assert likes[0] == like2  
    assert likes[1] == like1


@pytest.mark.django_db
def test_like_deleted_if_user_deleted(create_user):
    user = create_user(email="cascade@test.com")
    post = Post.objects.create(author=user, title="Cascade Post", content="Content")
    like = Like.objects.create(user=user, post=post)

    user.delete()
    assert Like.objects.filter(id=like.id).count() == 0


@pytest.mark.django_db
def test_like_deleted_if_post_deleted(create_user):
    user = create_user(email="cascade2@test.com")
    post = Post.objects.create(author=user, title="Cascade Post", content="Content")
    like = Like.objects.create(user=user, post=post)

    post.delete()
    assert Like.objects.filter(id=like.id).count() == 0