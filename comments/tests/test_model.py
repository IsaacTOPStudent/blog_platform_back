import pytest
from django.db.utils import IntegrityError
from comments.models import Comment
from posts.models import Post


@pytest.mark.django_db
def test_create_comment(create_user):
    """An authenticated user can create a valid comment"""
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Post Title", content="Post Content")

    comment = Comment.objects.create(user=user, post=post, content="Great post!")

    assert comment.id is not None
    assert comment.user == user
    assert comment.post == post
    assert comment.content == "Great post!"


@pytest.mark.django_db
def test_comment_str_representation(create_user):
    """The __str__ should return user, post title and some of the content"""
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="My Post", content="Content here")
    comment = Comment.objects.create(user=user, post=post, content="This is a test comment that is long enough")

    string = str(comment)
    assert user.username in string 
    assert "My Post" in string
    assert "This is a test comment" in string


@pytest.mark.django_db
def test_comment_ordering(create_user):
    """Comments should be sorted by created_at desc"""
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Ordered Post", content="Content")

    comment1 = Comment.objects.create(user=user, post=post, content="First comment")
    comment2 = Comment.objects.create(user=user, post=post, content="Second comment")

    comments = list(Comment.objects.all())
    assert comments[0] == comment2  
    assert comments[1] == comment1


@pytest.mark.django_db
def test_comment_max_length(create_user):
    """The content field must not accept more than 2500 chars."""
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Validation Post", content="Content")

    long_content = "a" * 2501
    comment = Comment(user=user, post=post, content=long_content)

    with pytest.raises(Exception):  
        comment.save()


@pytest.mark.django_db
def test_comment_missing_user(create_user):
    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Missing Fields Post", content="Content")

    # without user
    with pytest.raises(IntegrityError):
        Comment.objects.create(post=post, content="No user here")

@pytest.mark.django_db
def test_comment_missing_post(create_user):

    user = create_user(email="user@test.com")
    post = Post.objects.create(author=user, title="Missing Fields Post", content="Content")
    # without post
    with pytest.raises(IntegrityError):
        Comment.objects.create(user=user, content="No post here")