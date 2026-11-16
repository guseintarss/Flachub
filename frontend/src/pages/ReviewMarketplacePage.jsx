import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { fetchReviewRequests } from '../api'
import {
  reviewStatusKey, reviewStatusLabel,
  OFFER_STATUS_LABELS, formatMoney, formatDeadline,
} from '../reviewMeta'
import '../styles/review.css'
import '../styles/Sidebar.css'

const TABS = [
  { key: 'open', label: 'Открытые', icon: 'fa-door-open' },
  { key: 'mine', label: 'Мои запросы', icon: 'fa-briefcase', auth: true },
  { key: 'reviewer', label: 'Мои отклики', icon: 'fa-hand-paper', auth: true },
]

function ReviewRequestCard({ reviewRequest }) {
  const post = reviewRequest.post
  const offers = reviewRequest.offers_count || 0
  return (
    <article className="marketplace-card">
      <header className="marketplace-card-head">
        <div>
          <Link to={`/post/${post.slug}/`} className="marketplace-card-title">
            {post.title}
          </Link>
          <p className="marketplace-card-author">
            <i className="fas fa-user" />{' '}
            <Link to={`/user/${post.author?.username}/`}>{post.author?.username}</Link>
            {post.category?.name && <span className="marketplace-card-category"> · {post.category.name}</span>}
          </p>
        </div>
        <span className={`review-status-badge review-status-${reviewStatusKey(reviewRequest.status)}`}>
          {reviewStatusLabel(reviewRequest.status)}
        </span>
      </header>

      {post.excerpt && <p className="marketplace-card-excerpt">{post.excerpt}</p>}

      {post.code_preview && (
        <pre className="marketplace-card-code"><code>{post.code_preview}</code></pre>
      )}

      <dl className="marketplace-card-meta">
        <div>
          <dt><i className="fas fa-language" /> Язык</dt>
          <dd>{post.code_language || '—'}</dd>
        </div>
        <div>
          <dt><i className="fas fa-crosshairs" /> Фокус</dt>
          <dd>{post.review_focus || 'Не указан'}</dd>
        </div>
        <div>
          <dt><i className="fas fa-wallet" /> Бюджет</dt>
          <dd>{formatMoney(reviewRequest.budget)}</dd>
        </div>
        <div>
          <dt><i className="fas fa-hourglass-half" /> Дедлайн</dt>
          <dd>{reviewRequest.deadline ? formatDeadline(reviewRequest.deadline) : 'Без срока'}</dd>
        </div>
      </dl>

      <footer className="marketplace-card-foot">
        <span className="marketplace-card-offers">
          <i className="fas fa-comments" /> {offers} {offers === 1 ? 'отклик' : offers > 1 && offers < 5 ? 'отклика' : 'откликов'}
        </span>
        {reviewRequest.my_offer && (
          <span className={`marketplace-card-my-offer is-${reviewRequest.my_offer.status}`}>
            Мой отклик: {OFFER_STATUS_LABELS[reviewRequest.my_offer.status] || reviewRequest.my_offer.status}
          </span>
        )}
        <Link to={`/post/${post.slug}/`} className="btn btn-primary">
          {reviewRequest.my_offer ? 'Открыть разбор' : 'Откликнуться'} <i className="fas fa-arrow-right" />
        </Link>
      </footer>
    </article>
  )
}

function ReviewMarketplacePage() {
  const { user } = useAuth()
  const [tab, setTab] = useState('open')
  const [items, setItems] = useState([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    setError('')
    const params = { page }
    if (tab === 'mine') {
      params.mine = true
      params.status = 'all'
    } else if (tab === 'reviewer') {
      params.reviewer = 'me'
      params.status = 'all'
    } else {
      params.status = 'open'
    }
    fetchReviewRequests(params)
      .then(data => {
        setItems(data.results || [])
        setCount(data.count || 0)
      })
      .catch(() => setError('Не удалось загрузить запросы на разбор. Обновите страницу.'))
      .finally(() => setLoading(false))
  }, [tab, page])

  // Загрузка списка при смене вкладки и страницы.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { load() }, [load])

  function changeTab(next) {
    setTab(next)
    setPage(1)
  }

  const totalPages = Math.max(1, Math.ceil(count / 20))

  return (
    <main className="page">
      <div className="pg-container">
        <div className="marketplace">
          <header className="marketplace-hero">
            <div>
              <p className="marketplace-kicker">Разборы кода</p>
              <h1>Маркетплейс разборов</h1>
              <p className="marketplace-subtitle">
                Опубликуйте код, найдите ревьюера и договоритесь о сроках и ставке.
                Ревьюеры оставляют отклики, автор выбирает лучший.
              </p>
            </div>
            <Link to="/add-post/" className="btn btn-primary marketplace-cta">
              <i className="fas fa-plus" /> Опубликовать разбор
            </Link>
          </header>

          <div className="marketplace-tabs" role="tablist" aria-label="Фильтр запросов">
            {TABS.filter(item => !item.auth || user).map(item => (
              <button
                key={item.key}
                type="button"
                role="tab"
                aria-selected={tab === item.key}
                className={`marketplace-tab${tab === item.key ? ' is-active' : ''}`}
                onClick={() => changeTab(item.key)}
              >
                <i className={`fas ${item.icon}`} /> {item.label}
              </button>
            ))}
          </div>

          {error && <div className="comment-error" role="alert">{error}</div>}

          {loading && (
            <div className="marketplace-list" aria-busy="true">
              {[1, 2, 3].map(item => (
                <div key={item} className="marketplace-card marketplace-card-skeleton">
                  <div className="skeleton-line" style={{ width: '60%', height: 22 }} />
                  <div className="skeleton-line" style={{ width: '100%', height: 12, marginTop: 14 }} />
                  <div className="skeleton-line" style={{ width: '82%', height: 12, marginTop: 8 }} />
                  <div className="skeleton-line" style={{ width: '100%', height: 90, marginTop: 18 }} />
                </div>
              ))}
            </div>
          )}

          {!loading && items.length === 0 && (
            <div className="marketplace-empty">
              <i className="fas fa-code-branch" />
              <h2>{tab === 'open' ? 'Открытых запросов пока нет' : 'Здесь пока пусто'}</h2>
              <p>
                {tab === 'open'
                  ? 'Опубликуйте фрагмент кода — ревьюеры увидят запрос и смогут откликнуться.'
                  : 'Запросы и отклики появятся здесь, когда вы начнёте работать с разборами.'}
              </p>
              {tab === 'open' && <Link to="/add-post/" className="btn btn-primary">Создать запрос</Link>}
            </div>
          )}

          {!loading && items.length > 0 && (
            <div className="marketplace-list">
              {items.map(item => <ReviewRequestCard key={item.id} reviewRequest={item} />)}
            </div>
          )}

          {totalPages > 1 && (
            <nav className="pagination" aria-label="Страницы запросов">
              <button className="pagination-btn" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>
                ← Назад
              </button>
              <span className="pagination-status">{page} / {totalPages}</span>
              <button className="pagination-btn" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                Вперёд →
              </button>
            </nav>
          )}
        </div>
      </div>
    </main>
  )
}

export default ReviewMarketplacePage
