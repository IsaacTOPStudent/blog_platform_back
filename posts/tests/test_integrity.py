import pytest 
from rest_framework import status
from posts.models import Post


POST_UPDATE_URL = lambda post_id: f"/api/blog/{post_id}/"
POST_LIST_URL = '/api/post/'


@pytest.mark.django_db
def test_post_permissions_are_persisted(auth_client):
    client, user = auth_client(email="owner@example.com")
    payload = {
        "title": "Permission Test",
        "content": "Check access perms",
        "author_access": "write",
        "team_access": "read",
        "authenticated_access": "read",
        "public_access": "none",
    }

    response = client.post(POST_LIST_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    post = Post.objects.get(id=response.data["id"])
    assert post.author_access == "write"
    assert post.team_access == "read"
    assert post.authenticated_access == "read"
    assert post.public_access == "none"


@pytest.mark.django_db
def test_update_post_permissions(auth_client):
    client, user = auth_client(email="owner@example.com")
    post = Post.objects.create(
        author=user,
        title="Initial",
        content="Initial content",
        author_access="write",
        team_access="none",
        authenticated_access="none",
        public_access="none",
    )

    payload = {
        "team_access": "write",
        "authenticated_access": "read",
        "public_access": "none",
    }

    response = client.patch(POST_UPDATE_URL(post.id), payload, format="json")
    assert response.status_code == status.HTTP_200_OK

    post.refresh_from_db()
    assert post.team_access == "write"
    assert post.authenticated_access == "read"
    assert post.public_access == "none"