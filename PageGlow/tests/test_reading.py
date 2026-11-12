"""Тесты чтения, дашборда автора, импорта с Хабра и SSR-страницы статьи."""
from unittest.mock import patch

import pytest
from django.test import Client
from rest_framework.test import APIClient

from main.models import PostView


def api_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestPostReadTracking:
    def test_read_event_is_created_and_updated(self, user, post):
        api = api_for(user)

        first = api.post(
            f'/api/mobile/posts/{post.slug}/read/',
            {'scroll_depth': 40, 'read_seconds': 10, 'session_key': 'session-1'},
            format='json',
        )
        second = api.post(
            f'/api/mobile/posts/{post.slug}/read/',
            {
                'scroll_depth': 100,
                'read_seconds': 30,
                'session_key': 'session-1',
                'is_read_complete': True,
            },
            format='json',
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert PostView.objects.filter(post=post).count() == 1
        view = PostView.objects.get(post=post)
        assert view.scroll_depth == 100
        assert view.read_seconds == 30
        assert view.is_read_complete is True
        assert view.user == user

    def test_author_dashboard_returns_period_data(self, user, post):
        api = api_for(user)
        api.post(
            f'/api/mobile/posts/{post.slug}/read/',
            {
                'scroll_depth': 100,
                'read_seconds': 45,
                'session_key': 'session-1',
                'is_read_complete': True,
                'source': 'search',
            },
            format='json',
        )

        response = api.get('/api/mobile/author/dashboard/?days=7')

        assert response.status_code == 200
        data = response.data
        assert data['period_days'] == 7
        assert data['kpi']['views'] == 1
        assert data['kpi']['completed'] == 1
        assert data['kpi']['completion_rate'] == 100.0
        assert len(data['daily']) == 7
        assert data['sources'][0]['source'] == 'search'
        assert data['top_posts'][0]['slug'] == post.slug

    def test_dashboard_requires_authentication(self):
        response = Client().get('/api/mobile/author/dashboard/')

        assert response.status_code in (401, 403)


@pytest.mark.django_db
class TestHabrImportEndpoint:
    def test_rejects_non_habr_url(self, user):
        api = api_for(user)

        response = api.post(
            '/api/mobile/import/habr/',
            {'url': 'https://example.com/article/1'},
            format='json',
        )

        assert response.status_code == 400
        assert 'habr.com' in str(response.data['detail'])

    def test_returns_sanitized_draft(self, user):
        api = api_for(user)
        draft = {
            'title': 'Импортированная статья',
            'content': '<p>Очищенный текст</p>',
            'tags': ['python'],
            'cover_url': '/media/imports/habr/cover.jpg',
            'source_url': 'https://habr.com/ru/articles/1/',
            'source': 'habr',
            'author': 'Автор',
            'description': 'Описание',
        }

        with patch('mobile_api.views.import_habr_article', return_value=draft) as importer:
            response = api.post(
                '/api/mobile/import/habr/',
                {'url': 'https://habr.com/ru/articles/1/'},
                format='json',
            )

        assert response.status_code == 200
        assert response.data == draft
        importer.assert_called_once_with('https://habr.com/ru/articles/1/')


@pytest.mark.django_db
class TestPostSSR:
    def test_published_post_renders_html_and_initial_data(self, post):
        response = Client().get(f'/post/{post.slug}/')

        assert response.status_code == 200
        html = response.content.decode()
        assert post.title in html
        assert 'initial-post-data' in html
        assert 'application/ld+json' in html
        assert 'og:title' in html
        assert post.content in html

    def test_draft_is_not_rendered(self, draft_post):
        response = Client().get(f'/post/{draft_post.slug}/')

        assert response.status_code == 404
