import pytest 
from rest_framework import status
from posts.models import Post

POST_LIST_URL = '/api/post/'

@pytest.mark.django_db
def test_create_post_sets_author(auth_client):
    client, user = auth_client()
    payload = {'title': 'Isaac Post', 
               'content': 'Some interesting content',
               'read_permission': 'public',
               'edit_permission': 'author'}
    response = client.post(POST_LIST_URL, payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    post = Post.objects.get(id=response.data['id'])
    assert post.author == user 
    assert post.excerpt == post.content[:200]

@pytest.mark.django_db
def test_create_post_missing_required_fields(auth_client):
    client, _ = auth_client()

    # Without title
    response = client.post(POST_LIST_URL, {"content": "Contenido sin título"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Without content
    response = client.post(POST_LIST_URL, {"title": "Título sin contenido"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_post_excerpt_is_generated_and_limited(auth_client):
    client, user = auth_client()

    long_content = "x" * 500  # 500 
    payload = {
        "title": "Post con excerpt",
        "content": long_content,
        "read_permission": "public",
        "edit_permission": "author",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    post = Post.objects.get(id=response.data["id"])
    assert post.excerpt is not None
    assert len(post.excerpt) <= 200
    # Excerpt must be exactly the first 200 characters
    assert post.excerpt == long_content[:200]