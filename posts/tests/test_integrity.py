import pytest 
from rest_framework import status
from posts.models import Post


POST_DETAIL_URL = lambda post_id: f"/api/blog/{post_id}/"
POST_LIST_URL = '/api/post/'

@pytest.mark.django_db
def test_post_permissions_are_persisted(auth_client):
    client, user = auth_client(email="owner@example.com")
    payload = {
        "title": "Permission Test",
        "content": "Check read/edit perms",
        "read_permission": "authenticated",
        "edit_permission": "team"
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    post = Post.objects.get(id=response.data["id"])
    assert post.read_permission == "authenticated"
    assert post.edit_permission == "team"


@pytest.mark.django_db
def test_update_post_permissions(auth_client):
    client, user = auth_client(email="owner@example.com")
    post = Post.objects.create(
        author=user,
        title="Initial",
        content="Initial content",
        read_permission="public",
        edit_permission="author"
    )

    payload = {
        "read_permission": "team",
        "edit_permission": "team"
    }

    response = client.patch(POST_DETAIL_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_200_OK

    post.refresh_from_db()
    assert post.read_permission == "team"
    assert post.edit_permission == "team"