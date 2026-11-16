import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import PostCard from '../components/Feed/PostCard'
import Sidebar from '../components/Sidebar/Sidebar'
import { PostListSkeleton } from '../components/Skeleton'

function PostListPage({ endpoint, title, eyebrow }) {
  const { slug } = useParams()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)
    setPosts([])
    fetch(endpoint(slug, page))
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        setPosts(data.results || [])
        setTotalPages(Math.ceil((data.count || 0) / 20))
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [slug, page, endpoint])

  if (error) return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content" style={{ textAlign: 'center', padding: 60, color: 'var(--muted)' }}>
          <p>Ошибка загрузки: {error}</p>
        </div>
      </div>
    </main>
  )

  if (loading) return <PostListSkeleton />

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          {title && (
            <div className="feed-header">
              <div>
                <p className="feed-kicker">{eyebrow}</p>
                <h1 className="feed-title">{title}</h1>
                <p className="feed-subtitle">Материалы сообщества по этой теме.</p>
              </div>
            </div>
          )}

          {!loading && posts.length === 0 && (
            <div className="feed-empty">
              <span className="feed-empty-mark"><i className="fas fa-tag" /></span>
              <h3>Публикаций не найдено</h3>
              <p>По этому тегу пока нет материалов. Загляните позже или выберите другой раздел.</p>
            </div>
          )}

          {!loading && posts.length > 0 && (
            <>
              <div className="feed-container">
                {posts.map(p => <PostCard key={p.id} post={p} />)}
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="pagination-btn"
                    disabled={page <= 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                  >
                    <i className="fas fa-arrow-left" /> Назад
                  </button>
                  <span className="pagination-status">{page} / {totalPages}</span>
                  <button
                    className="pagination-btn"
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => p + 1)}
                  >
                    Далее <i className="fas fa-arrow-right" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export function TagPosts() {
  const { slug } = useParams()
  const endpoint = (tagSlug, page) => `/api/mobile/posts/?tag=${tagSlug}&page=${page}`
  return <PostListPage endpoint={endpoint} eyebrow="Тег" title={`#${slug}`} />
}

export function CategoryPosts() {
  const { slug } = useParams()
  const endpoint = (catSlug, page) => `/api/mobile/posts/?cat=${catSlug}&page=${page}`
  const title = slug ? slug.replace(/-/g, ' ') : 'Категория'
  return <PostListPage endpoint={endpoint} eyebrow="Категория" title={title} />
}

export default PostListPage
