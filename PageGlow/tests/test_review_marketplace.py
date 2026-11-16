"""Тесты маркетплейса разборов, импорта из GitHub и статистики ревьюера."""
import base64
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from main import github_import
from main.models import Comment, Post, ReviewOffer, ReviewRequest
from users.models import UserReputationLog

CODE = 'def add(a, b):\n    return a + b\n'


def api_for(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


def review_payload(**overrides):
    data = {
        'title': 'Разбор функции add',
        'content': '<p>Проверьте код</p>',
        'post_type': 'review',
        'is_published': True,
        'code_snippet': CODE,
        'code_language': 'python',
    }
    data.update(overrides)
    return data


@pytest.fixture
def review_post(user):
    return Post.objects.create(
        title='Разбор кода',
        content='<p>Разбор кода на Python</p>',
        post_type=Post.PostType.REVIEW,
        code_snippet=CODE,
        code_language='python',
        author=user,
        is_published=Post.Status.PUBLISHED,
    )


@pytest.mark.django_db
class TestReviewMarketplace:
    def test_request_is_created_with_post_and_configured(self, user):
        deadline = (timezone.now() + timedelta(days=7)).isoformat()
        response = api_for(user).post(
            '/api/mobile/posts/',
            review_payload(review_deadline=deadline, review_budget=5000),
            format='json',
        )

        assert response.status_code == 201
        review_request = ReviewRequest.objects.get(post__slug=response.data['slug'])
        assert review_request.status == ReviewRequest.Status.OPEN
        assert review_request.budget == 5000
        assert review_request.deadline is not None

    def test_reviewer_offers_and_author_selects(self, review_post, another_user, user):
        reviewer_api = api_for(another_user)
        response = reviewer_api.post(
            f'/api/mobile/review-requests/{review_post.review_request.id}/offer/',
            {'message': 'Посмотрю за вечер', 'price': 3000, 'deadline_days': 2},
            format='json',
        )

        assert response.status_code == 200
        assert response.data['my_offer']['price'] == 3000
        assert response.data['can_offer'] is True
        offer = ReviewOffer.objects.get(request=review_post.review_request, reviewer=another_user)
        assert offer.status == ReviewOffer.Status.PENDING

        author_api = api_for(user)
        listing = author_api.get(
            f'/api/mobile/review-requests/{review_post.review_request.id}/'
        )
        assert listing.status_code == 200
        assert listing.data['can_select_offer'] is True
        assert len(listing.data['offers']) == 1

        selected = author_api.post(
            f'/api/mobile/review-requests/{review_post.review_request.id}/select_offer/',
            {'offer_id': offer.id},
            format='json',
        )

        assert selected.status_code == 200
        offer.refresh_from_db()
        review_post.refresh_from_db()
        assert offer.status == ReviewOffer.Status.SELECTED
        assert review_post.reviewer == another_user
        assert review_post.review_status == Post.ReviewStatus.IN_REVIEW

    def test_non_author_cannot_select(self, review_post, another_user):
        offer = ReviewOffer.objects.create(
            request=review_post.review_request,
            reviewer=another_user,
        )

        response = api_for(another_user).post(
            f'/api/mobile/review-requests/{review_post.review_request.id}/select_offer/',
            {'offer_id': offer.id},
            format='json',
        )

        assert response.status_code == 403
        review_post.refresh_from_db()
        assert review_post.reviewer is None

    def test_withdraw_offer(self, review_post, another_user):
        offer = ReviewOffer.objects.create(
            request=review_post.review_request,
            reviewer=another_user,
        )

        response = api_for(another_user).post(
            f'/api/mobile/review-requests/{review_post.review_request.id}/withdraw_offer/'
        )

        assert response.status_code == 200
        offer.refresh_from_db()
        assert offer.status == ReviewOffer.Status.WITHDRAWN

    def test_cancel_closes_request_and_blocks_claim(self, review_post, user, another_user):
        response = api_for(user).post(
            f'/api/mobile/review-requests/{review_post.review_request.id}/cancel/'
        )

        assert response.status_code == 200
        review_post.refresh_from_db()
        review_post.review_request.refresh_from_db()
        assert review_post.review_status == Post.ReviewStatus.CANCELLED
        assert review_post.review_request.status == ReviewRequest.Status.CANCELLED

        claim = api_for(another_user).post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )
        assert claim.status_code == 400

    def test_claim_syncs_request_and_declines_offers(self, review_post, another_user):
        offer = ReviewOffer.objects.create(
            request=review_post.review_request,
            reviewer=another_user,
        )

        response = api_for(another_user).post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )

        assert response.status_code == 200
        review_post.refresh_from_db()
        review_post.review_request.refresh_from_db()
        offer.refresh_from_db()
        assert review_post.review_request.status == ReviewRequest.Status.IN_REVIEW
        assert offer.status == ReviewOffer.Status.DECLINED

    def test_release_reopens_request(self, review_post, another_user):
        review_post.reviewer = another_user
        review_post.review_status = Post.ReviewStatus.IN_REVIEW
        review_post.save(update_fields=['reviewer', 'review_status'])

        response = api_for(another_user).post(
            f'/api/mobile/posts/{review_post.slug}/release_review/'
        )

        assert response.status_code == 200
        review_post.review_request.refresh_from_db()
        assert review_post.review_request.status == ReviewRequest.Status.OPEN

    def test_stats_include_acceptance_rate(self, review_post, another_user):
        Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Принятое замечание',
            line_start=1,
            is_accepted=True,
        )
        Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Непринятое замечание',
            line_start=2,
        )

        response = api_for().get(f'/api/mobile/users/{another_user.id}/stats/')

        assert response.status_code == 200
        assert response.data['review_comments_count'] == 2
        assert response.data['review_comments_accepted'] == 1
        assert response.data['review_acceptance_rate'] == 50

    def test_spotlight_returns_review_and_request(self, review_post, another_user):
        review_post.reviewer = another_user
        review_post.review_status = Post.ReviewStatus.COMPLETED
        review_post.review_accepted_at = timezone.now()
        review_post.save(update_fields=['reviewer', 'review_status', 'review_accepted_at'])

        response = api_for().get('/api/mobile/review-spotlight/')

        assert response.status_code == 200
        assert response.data['review_of_day']['id'] == review_post.id

    def test_badge_awarded_for_completed_review(self, review_post, another_user):
        review_post.reviewer = another_user
        review_post.review_status = Post.ReviewStatus.COMPLETED
        review_post.save(update_fields=['reviewer', 'review_status'])

        assert another_user.achievements.filter(badge__key='reviewer').exists()

    def test_deadline_and_budget_can_be_cleared(self, user):
        deadline = (timezone.now() + timedelta(days=3)).isoformat()
        created = api_for(user).post(
            '/api/mobile/posts/',
            review_payload(review_deadline=deadline, review_budget=1000),
            format='json',
        )
        assert created.status_code == 201

        cleared = api_for(user).patch(
            f"/api/mobile/posts/{created.data['slug']}/",
            {'review_deadline': '', 'review_budget': ''},
            format='multipart',
        )

        assert cleared.status_code == 200
        review_request = ReviewRequest.objects.get(post__slug=created.data['slug'])
        assert review_request.deadline is None
        assert review_request.budget is None

    def test_other_reviewer_does_not_see_foreign_offers(self, review_post, another_user, user):
        ReviewOffer.objects.create(
            request=review_post.review_request,
            reviewer=another_user,
            message='Чужой отклик',
            price=9000,
        )
        third = user.__class__.objects.create_user(
            username='third', email='third@example.com', password='testpass123',
        )

        response = api_for(third).get(f'/api/mobile/review-requests/{review_post.review_request.id}/')

        assert response.status_code == 200
        assert response.data['offers'] == []
        assert response.data['offers_count'] == 1
        assert response.data['can_offer'] is True

    def test_actions_hide_foreign_draft_requests(self, user, another_user):
        draft = Post.objects.create(
            title='Черновик разбора',
            content='<p>Черновик</p>',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE,
            code_language='python',
            author=user,
            is_published=Post.Status.DRAFT,
        )

        response = api_for(another_user).post(
            f'/api/mobile/review-requests/{draft.review_request.id}/offer/',
            {'message': 'Возьму в работу', 'price': 1000},
            format='json',
        )

        assert response.status_code == 404


# ===== GitHub import =====

def _b64(text):
    return base64.b64encode(text.encode()).decode()


def test_github_rejects_non_github_hosts():
    with pytest.raises(github_import.GitHubImportError):
        github_import.import_github_source('https://example.com/owner/repo')


def test_github_repo_import(monkeypatch):
    def fake_fetch(path, params=None):
        if path == '/repos/octo/demo':
            return {'full_name': 'octo/demo', 'description': 'Demo repo', 'default_branch': 'main'}
        if path == '/repos/octo/demo/git/trees/main':
            return {'tree': [
                {'type': 'blob', 'path': 'app.py', 'size': 40},
                {'type': 'blob', 'path': 'node_modules/lib.js', 'size': 40},
                {'type': 'blob', 'path': 'README.md', 'size': 20},
            ]}
        if path == '/repos/octo/demo/contents/app.py':
            return {'type': 'file', 'encoding': 'base64', 'size': 40, 'path': 'app.py', 'content': _b64('print("hi")\n')}
        raise AssertionError(path)

    monkeypatch.setattr(github_import, '_fetch_json', fake_fetch)
    result = github_import.import_github_source('https://github.com/octo/demo')

    assert result['kind'] == 'repo'
    assert result['code_language'] == 'Python'
    assert [file['path'] for file in result['files']] == ['app.py']
    assert result['code_snippet'] == 'print("hi")\n'


def test_github_file_and_pull_import(monkeypatch):
    calls = []

    def fake_fetch(path, params=None):
        calls.append(path)
        if path == '/repos/octo/demo/contents/src/main.py':
            return {'type': 'file', 'encoding': 'base64', 'size': 20, 'path': 'src/main.py', 'content': _b64('print(1)\n')}
        if path == '/repos/octo/demo/pulls/7':
            return {'title': 'Fix bug', 'body': 'Описание', 'head': {'sha': 'abc123'}}
        if path == '/repos/octo/demo/pulls/7/files':
            return [{'filename': 'app.ts', 'status': 'modified', 'size': 20, 'additions': 2, 'deletions': 1}]
        if path == '/repos/octo/demo/contents/app.ts':
            return {'type': 'file', 'encoding': 'base64', 'size': 20, 'path': 'app.ts', 'content': _b64('const a = 1\n')}
        raise AssertionError(path)

    monkeypatch.setattr(github_import, '_fetch_json', fake_fetch)

    file_result = github_import.import_github_source(
        'https://github.com/octo/demo/blob/main/src/main.py'
    )
    assert file_result['kind'] == 'file'
    assert file_result['code_language'] == 'Python'

    pr_result = github_import.import_github_source('https://github.com/octo/demo/pull/7')
    assert pr_result['kind'] == 'pr'
    assert pr_result['pr_number'] == 7
    assert pr_result['code_language'] == 'TypeScript'
    assert pr_result['title'] == 'Fix bug'


def test_github_import_endpoint_requires_authentication():
    response = APIClient().post('/api/mobile/import/github/', {'url': 'https://github.com/octo/demo'}, format='json')
    assert response.status_code in (401, 403)
