"""
Регрессионные тесты mobile API: публикация, черновики, права и комментарии.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from main.models import Comment, Post, Subscription

User = get_user_model()


@pytest.fixture
def api(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def post_payload(**overrides):
    data = {
        'title': 'Тестовая публикация',
        'content': '<p>Текст публикации</p>',
        'post_type': 'article',
        'is_published': True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestPostPublishing:
    def test_create_published_post(self, api, user):
        response = api.post('/api/mobile/posts/', post_payload(), format='json')

        assert response.status_code == 201
        post = Post.objects.get(slug=response.data['slug'])
        assert post.author == user
        assert post.is_published is True

    def test_duplicate_titles_get_unique_slugs(self, api):
        first = api.post('/api/mobile/posts/', post_payload(), format='json')
        second = api.post('/api/mobile/posts/', post_payload(), format='json')

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.data['slug'] != second.data['slug']
        assert second.data['slug'].endswith('-2')

    def test_autosaved_draft_can_be_published_without_duplicate(self, api):
        draft = api.post(
            '/api/mobile/posts/',
            post_payload(is_published=False),
            format='json',
        )
        assert draft.status_code == 201
        slug = draft.data['slug']
        post_id = draft.data['id']

        published = api.patch(
            f'/api/mobile/posts/{slug}/',
            post_payload(is_published=True, content='<p>Обновлённый текст</p>'),
            format='json',
        )

        assert published.status_code == 200
        assert published.data['slug'] == slug
        assert published.data['is_published'] is True
        assert Post.objects.filter(id=post_id).count() == 1
        assert Post.objects.count() == 1

    def test_partial_update_keeps_published_status(self, api, post):
        response = api.patch(
            f'/api/mobile/posts/{post.slug}/',
            {'content': '<p>Новый текст</p>'},
            format='json',
        )

        assert response.status_code == 200
        post.refresh_from_db()
        assert post.is_published is True

    def test_draft_is_hidden_from_public(self, api_client, draft_post):
        response = api_client.get(f'/api/mobile/posts/{draft_post.slug}/')

        assert response.status_code == 404

    def test_author_can_open_own_draft(self, api, draft_post):
        response = api.get(f'/api/mobile/posts/{draft_post.slug}/')

        assert response.status_code == 200
        assert response.data['is_published'] is False

    def test_non_author_cannot_update_post(self, another_user, post):
        client = APIClient()
        client.force_authenticate(user=another_user)

        response = client.patch(
            f'/api/mobile/posts/{post.slug}/',
            {'title': 'Взлом'},
            format='json',
        )

        assert response.status_code == 403
        post.refresh_from_db()
        assert post.title == 'Тестовая статья'

    def test_non_author_cannot_delete_post(self, another_user, post):
        client = APIClient()
        client.force_authenticate(user=another_user)

        response = client.delete(f'/api/mobile/posts/{post.slug}/')

        assert response.status_code == 404
        assert Post.objects.filter(id=post.id).exists()

    def test_view_counter_skips_author(self, api, post):
        initial = post.views

        response = api.get(f'/api/mobile/posts/{post.slug}/')

        assert response.status_code == 200
        post.refresh_from_db()
        assert post.views == initial

    def test_view_counter_increments_for_reader(self, api_client, post):
        initial = post.views

        response = api_client.get(f'/api/mobile/posts/{post.slug}/')

        assert response.status_code == 200
        post.refresh_from_db()
        assert post.views == initial + 1


@pytest.mark.django_db
class TestCommentPermissions:
    def test_comment_requires_existing_post(self, api):
        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Комментарий', 'post_id': 999999},
            format='json',
        )

        assert response.status_code == 404

    def test_comment_requires_post_id(self, api):
        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Комментарий'},
            format='json',
        )

        assert response.status_code == 400

    def test_comment_rejects_invalid_post_id(self, api):
        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Комментарий', 'post_id': 'not-a-number'},
            format='json',
        )

        assert response.status_code == 400

    def test_cannot_comment_on_someone_else_draft(self, another_user, draft_post):
        client = APIClient()
        client.force_authenticate(user=another_user)

        response = client.post(
            '/api/mobile/comments/',
            {'content': 'Комментарий', 'post_id': draft_post.id},
            format='json',
        )

        assert response.status_code == 403

    def test_comment_is_created(self, api, post):
        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Комментарий', 'post_id': post.id},
            format='json',
        )

        assert response.status_code == 201
        assert response.data['post'] == post.id
        assert Comment.objects.filter(post=post, content='Комментарий').exists()

    def test_non_author_cannot_edit_comment(self, another_user, comment):
        client = APIClient()
        client.force_authenticate(user=another_user)

        response = client.patch(
            f'/api/mobile/comments/{comment.id}/',
            {'content': 'Изменено чужим пользователем'},
            format='json',
        )

        assert response.status_code == 403
        comment.refresh_from_db()
        assert comment.content == 'Тестовый комментарий'

    def test_author_edit_marks_comment_as_edited(self, api, comment):
        response = api.patch(
            f'/api/mobile/comments/{comment.id}/',
            {'content': 'Изменено автором'},
            format='json',
        )

        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.content == 'Изменено автором'
        assert comment.is_edited is True

    def test_comment_like_action(self, api, comment, user):
        response = api.post(f'/api/mobile/comment-actions/{comment.id}/toggle_like/')

        assert response.status_code == 200
        assert response.data['liked'] is True
        assert comment.likes.filter(id=user.id).exists()

    def test_comment_like_action_returns_404_for_missing_comment(self, api):
        response = api.post('/api/mobile/comment-actions/999999/toggle_like/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestCsrfProtection:
    def test_post_creation_requires_csrf_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(
            '/api/mobile/posts/',
            post_payload(),
            format='json',
        )

        assert response.status_code == 403
        assert Post.objects.count() == 0

    def test_post_creation_accepts_csrf_token_from_me_endpoint(self, user):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        me = client.get('/api/mobile/me/')
        token = me.cookies['csrftoken'].value

        response = client.post(
            '/api/mobile/posts/',
            post_payload(),
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        assert response.status_code == 201


@pytest.mark.django_db
class TestLoginCsrf:
    def test_login_requires_csrf(self, user):
        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            '/api/mobile/auth/login/',
            {'username': user.username, 'password': 'testpass123'},
            format='json',
        )

        assert response.status_code == 403

    def test_login_accepts_csrf_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        token = client.get('/api/mobile/me/').cookies['csrftoken'].value

        response = client.post(
            '/api/mobile/auth/login/',
            {'username': user.username, 'password': 'testpass123'},
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        assert response.status_code == 200
        assert response.data['username'] == user.username

    def test_register_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            '/api/mobile/auth/register/',
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'strongpass123',
                'password2': 'strongpass123',
            },
            format='json',
        )

        assert response.status_code == 403

    def test_register_accepts_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        token = client.get('/api/mobile/me/').cookies['csrftoken'].value

        response = client.post(
            '/api/mobile/auth/register/',
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'strongpass123',
                'password2': 'strongpass123',
            },
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        assert response.status_code == 201
        assert response.data['username'] == 'newuser'

    def test_logout_requires_csrf(self, user):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post('/api/mobile/auth/logout/')

        assert response.status_code == 403

    def test_logout_accepts_csrf_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)
        token = client.get('/api/mobile/me/').cookies['csrftoken'].value

        response = client.post(
            '/api/mobile/auth/logout/',
            HTTP_X_CSRFTOKEN=token,
        )

        assert response.status_code == 200


@pytest.mark.django_db
class TestSubscriptionEndpoint:
    def test_subscribe_requires_csrf_for_session_auth(self, user, another_user):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post('/ajax/subscribe/', {'author_id': another_user.id})

        assert response.status_code == 403
        assert not Subscription.objects.filter(subscriber=user, author=another_user).exists()
