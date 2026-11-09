"""
Тесты MVP «Разборы»: review-посты, очередь, claim/release, строчные
замечания, приём разбора, resolve, профиль и статистика.
"""
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from main.models import Comment, Notification, Post
from users.models import UserReputationLog

CODE_SNIPPET = 'def add(a, b):\n    return a + b\n\nprint(add(1, 2))'
CODE_LINES = len(CODE_SNIPPET.splitlines())  # 4


def api_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def review_payload(**overrides):
    data = {
        'title': 'Разбор функции add',
        'content': '<p>Проверьте код</p>',
        'post_type': 'review',
        'is_published': True,
        'code_snippet': CODE_SNIPPET,
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
        code_snippet=CODE_SNIPPET,
        code_language='python',
        author=user,
        is_published=Post.Status.PUBLISHED,
    )


@pytest.fixture
def line_comment(review_post, another_user):
    return Comment.objects.create(
        post=review_post,
        author=another_user,
        content='Здесь ошибка',
        line_start=2,
        severity=Comment.Severity.MAJOR,
    )


# ===== Создание review-поста =====

@pytest.mark.django_db
class TestReviewPostCreation:
    def test_create_review_with_code(self, user):
        api = api_for(user)

        response = api.post('/api/mobile/posts/', review_payload(), format='json')

        assert response.status_code == 201
        post = Post.objects.get(slug=response.data['slug'])
        assert post.post_type == Post.PostType.REVIEW
        assert post.code_snippet == CODE_SNIPPET
        assert post.code_language == 'python'
        assert post.review_status == Post.ReviewStatus.OPEN
        assert post.reviewer is None
        assert post.review_accepted_at is None

    def test_review_requires_code(self, user):
        api = api_for(user)

        response = api.post(
            '/api/mobile/posts/',
            review_payload(code_snippet='   '),
            format='json',
        )

        assert response.status_code == 400
        assert 'code_snippet' in response.data
        assert not Post.objects.exists()

    def test_review_requires_language(self, user):
        api = api_for(user)

        response = api.post(
            '/api/mobile/posts/',
            review_payload(code_language=''),
            format='json',
        )

        assert response.status_code == 400
        assert 'code_language' in response.data

    def test_switch_from_review_clears_review_fields(self, user, review_post):
        review_post.reviewer = user
        review_post.review_status = Post.ReviewStatus.COMPLETED
        review_post.review_accepted_at = timezone.now()
        review_post.review_focus = 'Безопасность'
        review_post.save()
        api = api_for(user)

        response = api.patch(
            f'/api/mobile/posts/{review_post.slug}/',
            {'post_type': 'article'},
            format='json',
        )

        assert response.status_code == 200
        review_post.refresh_from_db()
        assert review_post.post_type == Post.PostType.ARTICLE
        assert review_post.code_snippet == ''
        assert review_post.code_language == ''
        assert review_post.review_focus == ''
        assert review_post.reviewer is None
        assert review_post.review_status == Post.ReviewStatus.OPEN
        assert review_post.review_accepted_at is None

    def test_client_cannot_set_review_state(self, user):
        api = api_for(user)
        payload = review_payload(
            review_status='completed',
            reviewer=user.id,
            review_accepted_at=timezone.now().isoformat(),
        )

        response = api.post('/api/mobile/posts/', payload, format='json')

        assert response.status_code == 201
        post = Post.objects.get(slug=response.data['slug'])
        assert post.review_status == Post.ReviewStatus.OPEN
        assert post.reviewer is None
        assert post.review_accepted_at is None


@pytest.mark.django_db
class TestReviewDetail:
    def test_detail_flags_for_author_and_reviewer(self, review_post, another_user):
        author_data = api_for(review_post.author).get(
            f'/api/mobile/posts/{review_post.slug}/'
        ).data
        assert author_data['is_review_author'] is True
        assert author_data['can_claim_review'] is False
        assert author_data['can_release_review'] is False
        assert author_data['reviewer'] is None
        assert author_data['code_snippet'] == CODE_SNIPPET
        assert author_data['review_status'] == 'open'

        reviewer_data = api_for(another_user).get(
            f'/api/mobile/posts/{review_post.slug}/'
        ).data
        assert reviewer_data['is_review_author'] is False
        assert reviewer_data['can_claim_review'] is True
        assert reviewer_data['can_release_review'] is False

    def test_detail_comments_include_review_fields(self, review_post, another_user):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Строчное замечание',
            line_start=1,
            severity=Comment.Severity.NIT,
        )
        api = api_for(review_post.author)

        data = api.get(f'/api/mobile/posts/{review_post.slug}/').data

        item = data['comments'][0]
        assert item['id'] == comment.id
        assert item['line_start'] == 1
        assert item['severity'] == 'nit'
        assert item['can_accept'] is True
        assert item['can_resolve'] is True


# ===== Очередь разборов =====

@pytest.mark.django_db
class TestReviewQueue:
    def test_queue_shows_only_open_reviews(
        self, api_client, review_post, another_user, user
    ):
        completed = Post.objects.create(
            title='Завершённый разбор',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE_SNIPPET,
            code_language='python',
            author=user,
            reviewer=another_user,
            review_status=Post.ReviewStatus.COMPLETED,
            is_published=Post.Status.PUBLISHED,
        )
        article = Post.objects.create(
            title='Обычная статья',
            post_type=Post.PostType.ARTICLE,
            author=user,
            is_published=Post.Status.PUBLISHED,
        )

        response = api_client.get(
            '/api/mobile/posts/',
            {'post_type': 'review', 'review_status': 'open'},
        )

        assert response.status_code == 200
        slugs = [item['slug'] for item in response.data['results']]
        assert slugs == [review_post.slug]
        assert completed.slug not in slugs
        assert article.slug not in slugs

        item = response.data['results'][0]
        assert item['review_status'] == 'open'
        assert item['code_language'] == 'python'


# ===== Claim / release =====

@pytest.mark.django_db
class TestClaimRelease:
    def test_claim_review(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(f'/api/mobile/posts/{review_post.slug}/claim_review/')

        assert response.status_code == 200
        review_post.refresh_from_db()
        assert review_post.reviewer == another_user
        assert review_post.review_status == Post.ReviewStatus.IN_REVIEW
        assert response.data['reviewer']['id'] == another_user.id
        assert response.data['can_release_review'] is True
        assert Notification.objects.filter(
            recipient=review_post.author,
            sender=another_user,
            notification_type=Notification.NotificationType.REVIEW_CLAIMED,
            post=review_post,
        ).exists()

    def test_author_cannot_claim_own_review(self, user, review_post):
        api = api_for(user)

        response = api.post(f'/api/mobile/posts/{review_post.slug}/claim_review/')

        assert response.status_code == 403
        review_post.refresh_from_db()
        assert review_post.reviewer is None
        assert review_post.review_status == Post.ReviewStatus.OPEN

    def test_second_claim_is_rejected(
        self, review_post, another_user, user_factory
    ):
        first = api_for(another_user)
        second_user = user_factory(username='thirduser', email='third@example.com')
        second = api_for(second_user)

        first_response = first.post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )
        second_response = second.post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 400
        review_post.refresh_from_db()
        assert review_post.reviewer == another_user

    def test_claim_requires_auth(self, review_post):
        response = APIClient().post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )

        assert response.status_code in (401, 403)

    def test_cannot_claim_non_review_post(self, user, another_user, post):
        api = api_for(another_user)

        response = api.post(f'/api/mobile/posts/{post.slug}/claim_review/')

        assert response.status_code == 404

    def test_release_review(self, review_post, another_user):
        api = api_for(another_user)
        api.post(f'/api/mobile/posts/{review_post.slug}/claim_review/')

        response = api.post(f'/api/mobile/posts/{review_post.slug}/release_review/')

        assert response.status_code == 200
        review_post.refresh_from_db()
        assert review_post.reviewer is None
        assert review_post.review_status == Post.ReviewStatus.OPEN
        assert response.data['review_status'] == 'open'

    def test_stranger_cannot_release_review(
        self, review_post, another_user, user_factory
    ):
        api_for(another_user).post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )
        stranger = api_for(user_factory(username='stranger', email='s@example.com'))

        response = stranger.post(
            f'/api/mobile/posts/{review_post.slug}/release_review/'
        )

        assert response.status_code == 403
        review_post.refresh_from_db()
        assert review_post.reviewer == another_user

    def test_release_requires_in_review_status(self, review_post, another_user):
        review_post.reviewer = another_user
        review_post.review_status = Post.ReviewStatus.OPEN
        review_post.save(update_fields=['reviewer', 'review_status'])
        api = api_for(another_user)

        response = api.post(f'/api/mobile/posts/{review_post.slug}/release_review/')

        assert response.status_code == 400

    def test_staff_can_release_review(self, review_post, another_user, admin_user):
        api_for(another_user).post(
            f'/api/mobile/posts/{review_post.slug}/claim_review/'
        )
        staff = api_for(admin_user)

        response = staff.post(f'/api/mobile/posts/{review_post.slug}/release_review/')

        assert response.status_code == 200
        review_post.refresh_from_db()
        assert review_post.review_status == Post.ReviewStatus.OPEN


# ===== Строчные замечания =====

@pytest.mark.django_db
class TestLineComments:
    def test_create_line_comment(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {
                'content': 'Тут ошибка',
                'post_id': review_post.id,
                'line_start': 2,
                'severity': 'major',
            },
            format='json',
        )

        assert response.status_code == 201
        assert response.data['line_start'] == 2
        assert response.data['line_end'] == 2
        assert response.data['severity'] == 'major'
        assert response.data['is_resolved'] is False
        assert response.data['is_accepted'] is False

    def test_line_end_defaults_to_line_start(self, review_post, another_user):
        response = api_for(another_user).post(
            '/api/mobile/comments/',
            {'content': 'Ещё замечание', 'post_id': review_post.id, 'line_start': 3},
            format='json',
        )

        assert response.status_code == 201
        assert response.data['line_start'] == 3
        assert response.data['line_end'] == 3

    def test_line_out_of_range_is_rejected(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Замечание', 'post_id': review_post.id, 'line_start': CODE_LINES + 1},
            format='json',
        )

        assert response.status_code == 400
        assert 'line_start' in response.data

    def test_line_end_out_of_range_is_rejected(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {
                'content': 'Замечание',
                'post_id': review_post.id,
                'line_start': 1,
                'line_end': CODE_LINES + 5,
            },
            format='json',
        )

        assert response.status_code == 400
        assert 'line_end' in response.data

    def test_line_end_before_line_start_is_rejected(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {
                'content': 'Замечание',
                'post_id': review_post.id,
                'line_start': 3,
                'line_end': 1,
            },
            format='json',
        )

        assert response.status_code == 400
        assert 'line_end' in response.data

    def test_line_end_without_line_start_is_rejected(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Замечание', 'post_id': review_post.id, 'line_end': 2},
            format='json',
        )

        assert response.status_code == 400
        assert 'line_end' in response.data

    def test_lines_on_non_review_post_are_rejected(self, post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Замечание', 'post_id': post.id, 'line_start': 1},
            format='json',
        )

        assert response.status_code == 400
        assert 'line_start' in response.data

    def test_invalid_severity_is_rejected(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {
                'content': 'Замечание',
                'post_id': review_post.id,
                'line_start': 1,
                'severity': 'critical',
            },
            format='json',
        )

        assert response.status_code == 400
        assert 'severity' in response.data

    def test_plain_comment_on_review_is_allowed(self, review_post, another_user):
        api = api_for(another_user)

        response = api.post(
            '/api/mobile/comments/',
            {'content': 'Общий комментарий', 'post_id': review_post.id},
            format='json',
        )

        assert response.status_code == 201
        assert response.data['line_start'] is None
        assert response.data['line_end'] is None
        assert response.data['severity'] == ''


# ===== Приём разбора =====

@pytest.mark.django_db
class TestAcceptComment:
    def test_post_author_accepts_comment(self, review_post, another_user):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Лучший разбор',
            line_start=2,
            severity=Comment.Severity.MAJOR,
        )
        api = api_for(review_post.author)

        detail = api.get(f'/api/mobile/comments/{comment.id}/')
        assert detail.status_code == 200
        assert detail.data['can_accept'] is True

        response = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code == 200
        assert response.data['is_accepted'] is True
        assert response.data['can_accept'] is False

        comment.refresh_from_db()
        review_post.refresh_from_db()
        assert comment.is_accepted is True
        assert review_post.review_status == Post.ReviewStatus.COMPLETED
        assert review_post.review_accepted_at is not None
        assert review_post.reviewer == another_user

        logs = UserReputationLog.objects.filter(
            user=another_user,
            reason=UserReputationLog.ReasonType.ANSWER_ACCEPTED,
            comment=comment,
        )
        assert logs.count() == 1
        assert logs.first().amount == 15
        assert another_user.reputation == 15

        assert Notification.objects.filter(
            recipient=another_user,
            notification_type=Notification.NotificationType.REVIEW_ACCEPTED,
            post=review_post,
            comment=comment,
        ).exists()

    def test_double_accept_does_not_award_twice(self, review_post, another_user):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Разбор',
            line_start=1,
        )
        api = api_for(review_post.author)

        first = api.post(f'/api/mobile/comments/{comment.id}/accept/')
        second = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert first.status_code == 200
        assert second.status_code == 400
        assert UserReputationLog.objects.filter(
            user=another_user,
            reason=UserReputationLog.ReasonType.ANSWER_ACCEPTED,
            comment=comment,
        ).count() == 1
        assert another_user.reputation == 15

    def test_cannot_accept_second_comment_after_completion(
        self, review_post, another_user, user_factory
    ):
        first_comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Первый разбор',
            line_start=1,
        )
        second_author = user_factory(username='second', email='second@example.com')
        second_comment = Comment.objects.create(
            post=review_post,
            author=second_author,
            content='Второй разбор',
            line_start=2,
        )
        api = api_for(review_post.author)

        first = api.post(f'/api/mobile/comments/{first_comment.id}/accept/')
        second = api.post(f'/api/mobile/comments/{second_comment.id}/accept/')

        assert first.status_code == 200
        assert second.status_code == 400
        second_comment.refresh_from_db()
        review_post.refresh_from_db()
        assert second_comment.is_accepted is False
        assert review_post.review_status == Post.ReviewStatus.COMPLETED
        assert UserReputationLog.objects.filter(
            user=second_author,
            reason=UserReputationLog.ReasonType.ANSWER_ACCEPTED,
        ).count() == 0
        assert second_author.reputation == 0

        detail = api.get(f'/api/mobile/comments/{second_comment.id}/')
        assert detail.data['can_accept'] is False

    def test_only_post_author_can_accept(
        self, review_post, another_user, user_factory
    ):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Разбор',
            line_start=1,
        )
        stranger = user_factory(username='stranger', email='stranger@example.com')
        api = api_for(stranger)

        response = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code == 403
        comment.refresh_from_db()
        assert comment.is_accepted is False

    def test_author_cannot_accept_own_comment(self, user, review_post):
        comment = Comment.objects.create(
            post=review_post,
            author=user,
            content='Свой комментарий',
            line_start=1,
        )
        api = api_for(user)

        response = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code == 400
        comment.refresh_from_db()
        review_post.refresh_from_db()
        assert comment.is_accepted is False
        assert review_post.review_status == Post.ReviewStatus.OPEN

    def test_cannot_accept_comment_on_non_review_post(self, post, user, another_user):
        comment = Comment.objects.create(
            post=post,
            author=another_user,
            content='Комментарий к статье',
        )
        api = api_for(user)

        response = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code == 400
        comment.refresh_from_db()
        assert comment.is_accepted is False

    def test_accept_keeps_existing_reviewer(
        self, review_post, another_user, user_factory
    ):
        assigned = user_factory(username='assigned', email='assigned@example.com')
        review_post.reviewer = assigned
        review_post.review_status = Post.ReviewStatus.IN_REVIEW
        review_post.save(update_fields=['reviewer', 'review_status'])
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Разбор от другого автора',
            line_start=2,
        )
        api = api_for(review_post.author)

        response = api.post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code == 200
        review_post.refresh_from_db()
        assert review_post.reviewer == assigned

    def test_accept_requires_auth(self, review_post, another_user):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Разбор',
            line_start=1,
        )

        response = APIClient().post(f'/api/mobile/comments/{comment.id}/accept/')

        assert response.status_code in (401, 403)


# ===== Resolve =====

@pytest.mark.django_db
class TestResolveComment:
    def test_comment_author_toggles_resolve(self, line_comment, another_user):
        api = api_for(another_user)

        first = api.post(f'/api/mobile/comments/{line_comment.id}/resolve/')
        second = api.post(f'/api/mobile/comments/{line_comment.id}/resolve/')

        assert first.status_code == 200
        assert first.data['is_resolved'] is True
        assert second.status_code == 200
        assert second.data['is_resolved'] is False

    def test_post_author_can_resolve(self, line_comment, review_post):
        api = api_for(review_post.author)

        response = api.post(f'/api/mobile/comments/{line_comment.id}/resolve/')

        assert response.status_code == 200
        line_comment.refresh_from_db()
        assert line_comment.is_resolved is True

    def test_stranger_cannot_resolve(
        self, line_comment, review_post, user_factory
    ):
        stranger = user_factory(username='stranger', email='stranger@example.com')
        api = api_for(stranger)

        response = api.post(f'/api/mobile/comments/{line_comment.id}/resolve/')

        assert response.status_code == 403
        line_comment.refresh_from_db()
        assert line_comment.is_resolved is False

    def test_general_comment_cannot_be_resolved(self, review_post, another_user):
        comment = Comment.objects.create(
            post=review_post,
            author=another_user,
            content='Общий комментарий',
        )
        api = api_for(another_user)

        response = api.post(f'/api/mobile/comments/{comment.id}/resolve/')

        assert response.status_code == 400

    def test_staff_can_resolve(self, line_comment, admin_user):
        api = api_for(admin_user)

        response = api.post(f'/api/mobile/comments/{line_comment.id}/resolve/')

        assert response.status_code == 200
        line_comment.refresh_from_db()
        assert line_comment.is_resolved is True


# ===== Профиль: разборы и статистика =====

@pytest.mark.django_db
class TestUserReviewsAndStats:
    @pytest.fixture
    def reviews_setup(self, user_factory):
        owner = user_factory(username='owner', email='owner@example.com')
        reviewer = user_factory(username='reviewer', email='reviewer@example.com')

        reviewed = Post.objects.create(
            title='Разбор для владельца',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE_SNIPPET,
            code_language='python',
            author=owner,
            reviewer=reviewer,
            review_status=Post.ReviewStatus.COMPLETED,
            review_accepted_at=timezone.now(),
            is_published=Post.Status.PUBLISHED,
        )
        authored_completed = Post.objects.create(
            title='Разбор от ревьюера',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE_SNIPPET,
            code_language='go',
            author=reviewer,
            reviewer=owner,
            review_status=Post.ReviewStatus.COMPLETED,
            review_accepted_at=timezone.now(),
            is_published=Post.Status.PUBLISHED,
        )
        authored_open = Post.objects.create(
            title='Открытый запрос ревьюера',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE_SNIPPET,
            code_language='rust',
            author=reviewer,
            is_published=Post.Status.PUBLISHED,
        )
        authored_draft = Post.objects.create(
            title='Черновик запроса ревьюера',
            post_type=Post.PostType.REVIEW,
            code_snippet=CODE_SNIPPET,
            code_language='c',
            author=reviewer,
            is_published=Post.Status.DRAFT,
        )
        return {
            'owner': owner,
            'reviewer': reviewer,
            'reviewed': reviewed,
            'authored_completed': authored_completed,
            'authored_open': authored_open,
            'authored_draft': authored_draft,
        }

    def test_reviews_given_by_default(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(f'/api/mobile/users/{user.id}/reviews/')

        assert response.status_code == 200
        slugs = [item['slug'] for item in response.data['results']]
        assert slugs == [reviews_setup['reviewed'].slug]

    def test_reviews_received(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(
            f'/api/mobile/users/{user.id}/reviews/',
            {'role': 'received'},
        )

        assert response.status_code == 200
        slugs = [item['slug'] for item in response.data['results']]
        assert slugs == [reviews_setup['authored_completed'].slug]

    def test_reviews_requested_hides_drafts(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(
            f'/api/mobile/users/{user.id}/reviews/',
            {'role': 'requested'},
        )

        assert response.status_code == 200
        slugs = {item['slug'] for item in response.data['results']}
        assert slugs == {
            reviews_setup['authored_completed'].slug,
            reviews_setup['authored_open'].slug,
        }
        assert reviews_setup['authored_draft'].slug not in slugs

    def test_invalid_role_is_rejected(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(
            f'/api/mobile/users/{user.id}/reviews/',
            {'role': 'unknown'},
        )

        assert response.status_code == 400

    def test_reviews_pagination(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(
            f'/api/mobile/users/{user.id}/reviews/',
            {'role': 'requested', 'page_size': 1},
        )

        assert response.status_code == 200
        assert response.data['count'] == 2
        assert len(response.data['results']) == 1

    def test_reviews_list_includes_review_fields(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(f'/api/mobile/users/{user.id}/reviews/')

        item = response.data['results'][0]
        assert item['review_status'] == 'completed'
        assert item['code_language'] == 'python'

    def test_stats_counts_reviews(self, api_client, reviews_setup):
        user = reviews_setup['reviewer']

        response = api_client.get(f'/api/mobile/users/{user.id}/stats/')

        assert response.status_code == 200
        assert response.data['reviews_given'] == 1
        assert response.data['reviews_received'] == 1
        assert response.data['reviews_requested'] == 2
        assert response.data['review_languages'] == ['python']
