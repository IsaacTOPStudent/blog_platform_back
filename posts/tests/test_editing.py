import pytest 
from rest_framework.test import APIClient
from rest_framework import status
from posts.models import Post
from users.models import Team

POST_DETAIL_URL = lambda pk: f"/api/blog/{pk}/"

@pytest.mark.django_db
def test_edit_post_only_author(auth_client):
    client, user = auth_client()
    post = Post.objects.create(author=user, title='something', content='something content here', read_permission='public', edit_permission='author')
    payload = {'title': 'New interesting title', 
               'content':'New interesting content'}
    response = client.put(POST_DETAIL_URL(post.id), payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == 'New interesting title'
    assert post.content == 'New interesting content'

@pytest.mark.django_db
def test_edit_post_forbidden_for_other_user(auth_client, client):
    team = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email='author@example.com', team=team)
    post = Post.objects.create(author=user1, title='No Edit', content='Cannot edit here', read_permission='public', edit_permission='author')
    
    client2, _ = auth_client(email='intruder@example.com')
    payload = {'title': 'content hacked'}
    response = client2.put(POST_DETAIL_URL(post.id), payload, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    #annonymous cannot edit 
    response = client.put(POST_DETAIL_URL(post.id), payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    #user with same team as the author cannot edit in this case
    client3, _ = auth_client(email="mate@example.com", team=team)
    response = client2.get(POST_DETAIL_URL(post.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_user_with_same_team_as_author_can_edit(auth_client):
    team = Team.objects.create(name="Team A")
    client1, user1 = auth_client(email='author@example.com', team=team)
    post = Post.objects.create(author=user1, title='Can Edit', content='Team can edit here', read_permission='public', edit_permission='team')
    
    #user with same team as the author can edit in this case
    client2, _ = auth_client(email='intruder@example.com', team=team)
    payload = {'title': 'content hacked',
               'content': 'new content here'}
    response = client2.put(POST_DETAIL_URL(post.id), payload, format='json')

    assert response.status_code == status.HTTP_200_OK

    #admin can edit any post
    admin_client, admin = auth_client(email="admin2@example.com", password="adminpass123")
    #admin user role
    admin.role = 'admin'
    #site admin
    #admin.is_staff = True
    #admin.is_superuser = True 
    admin.save()
    response = admin_client.put(POST_DETAIL_URL(post.id), payload, format='json')
    assert response.status_code == status.HTTP_200_OK

