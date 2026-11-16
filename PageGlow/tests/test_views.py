"""
Тесты маршрутизации SPA и служебных Django-страниц.
"""
import pytest

from main.models import Post


@pytest.mark.django_db
class TestSpaRouting:
    @pytest.mark.parametrize('path', [
        '/',
        '/profile/',
        '/login/',
        '/register/',
        '/add-post/',
        '/edit/example/',
        '/search/',
        '/subscriptions/',
        '/inbox/',
        '/admin-panel/',
        '/forgot-password/',
        '/reset-password/uid/token/',
    ])
    def test_client_routes_return_spa(self, client, path):
        response = client.get(path)

        assert response.status_code == 200
        assert b'<div id="root"></div>' in response.content

    def test_unknown_post_returns_404(self, client):
        response = client.get('/post/example/')

        assert response.status_code == 404
        assert b'<div id="root"></div>' not in response.content

    def test_api_404_is_not_spa(self, client):
        response = client.get('/api/mobile/posts/does-not-exist/')

        assert response.status_code == 404
        assert b'<div id="root"></div>' not in response.content

    def test_health_check(self, client):
        response = client.get('/health/')

        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'

    def test_sitemap_renders(self, client, post):
        response = client.get('/sitemap.xml')

        assert response.status_code == 200
        assert b'<urlset' in response.content
        assert post.get_absolute_url().encode() in response.content


@pytest.mark.django_db
class TestPostUrl:
    def test_get_absolute_url(self, post):
        assert post.get_absolute_url() == f'/post/{post.slug}/'

    def test_duplicate_titles_do_not_break_save(self, user):
        first = Post.objects.create(title='Одинаковый заголовок', author=user)
        second = Post.objects.create(title='Одинаковый заголовок', author=user)

        assert first.slug == 'odinakovy-zagolovok'
        assert second.slug == 'odinakovy-zagolovok-2'
