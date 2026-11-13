import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import PostCard from './PostCard'

function FeedSkeleton() {
  return (
    <div className="feed-skeleton" aria-hidden="true">
      {[1, 2, 3].map((card) => (
        <div key={card} className="post skeleton-post">
          <div className="skeleton-author">
            <div className="skeleton-circle" />
            <div>
              <div className="skeleton-line" style={{ width: 96, height: 12 }} />
              <div className="skeleton-line" style={{ width: 64, height: 10 }} />
            </div>
          </div>
          <div className="skeleton-line" style={{ width: '64%', height: 22 }} />
          {card === 1 && <div className="skeleton-line" style={{ width: '100%', height: 180, borderRadius: 12 }} />}
          <div className="skeleton-line" style={{ width: '100%', height: 12 }} />
          <div className="skeleton-line" style={{ width: '82%', height: 12 }} />
          <div className="skeleton-line" style={{ width: '100%', height: 1, marginTop: 18 }} />
        </div>
      ))}
    </div>
  )
}

const Feed = () => {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    // Загрузка страницы ленты при смене пагинации.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)
    fetch(`/api/mobile/posts/?page=${page}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setPosts(data.results || [])
        setTotalPages(Math.ceil((data.count || 0) / 20))
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [page])

  if (error) {
    return (
      <div className="content">
        <div className="feed-empty">
          <h3>Не удалось загрузить ленту</h3>
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={() => window.location.reload()}>
            Попробовать снова
          </button>
        </div>
      </div>
    )
  }

  if (loading) return <FeedSkeleton />

  if (posts.length === 0) {
    return (
      <div className="content">
        <div className="feed-empty">
          <span className="feed-empty-mark" aria-hidden="true">✦</span>
          <h3>Здесь пока тихо</h3>
          <p>Опубликуйте первую статью, разбор или заметку — начните разговор.</p>
          <Link className="btn btn-primary" to="/add-post/">Написать публикацию</Link>
        </div>
      </div>
    )
  }

  const featured = posts.find((p) => p.photo) || posts[0]
  const rest = posts.filter((p) => p.id !== featured.id)

  return (
    <div className="content">
      <header className="feed-header">
        <div>
          <p className="feed-kicker">Сообщество практиков</p>
          <h1 className="feed-title">Что нового</h1>
          <p className="feed-subtitle">Статьи, разборы и заметки от людей, которые делают продукт.</p>
        </div>
      </header>

      <PostCard post={featured} featured />

      {rest.length > 0 && (
        <>
          <div className="feed-section-head">
            <h2>Свежее</h2>
            <span>{posts.length} публикаций</span>
          </div>
          <div className="feed-container">
            {rest.map((p) => (
              <PostCard key={p.id} post={p} />
            ))}
          </div>
        </>
      )}

      {totalPages > 1 && (
        <nav className="pagination" aria-label="Страницы ленты">
          <button
            className="pagination-btn"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Назад
          </button>
          <span className="pagination-status">{page} / {totalPages}</span>
          <button
            className="pagination-btn"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Далее →
          </button>
        </nav>
      )}
    </div>
  )
}

export default Feed
