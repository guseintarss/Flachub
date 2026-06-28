import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import PostCard from '../components/Feed/PostCard'
import Sidebar from '../components/Sidebar/Sidebar'
import { PostListSkeleton } from '../components/Skeleton'

function PostListPage({ endpoint }) {
  const { slug } = useParams()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
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
          {!loading && posts.length === 0 && (
            <div style={{ textAlign: 'center', padding: 60, color: 'var(--muted)' }}>
              <i className="fas fa-tag" style={{ fontSize: 48, marginBottom: 16 }}></i>
              <h3>Постов не найдено</h3>
              <p>По этому тегу пока нет публикаций.</p>
            </div>
          )}

          {!loading && posts.length > 0 && (
            <>
              <div className="feed-container">
                {posts.map(p => <PostCard key={p.id} post={p} />)}
              </div>

              {totalPages > 1 && (
                <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 24 }}>
                  <button
                    disabled={page <= 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', cursor: page > 1 ? 'pointer' : 'not-allowed', opacity: page > 1 ? 1 : 0.5 }}
                  >
                    ← Назад
                  </button>
                  <span style={{ display: 'flex', alignItems: 'center', padding: '0 12px', fontSize: '0.9rem', color: 'var(--muted)' }}>
                    {page} / {totalPages}
                  </span>
                  <button
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => p + 1)}
                    style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', cursor: page < totalPages ? 'pointer' : 'not-allowed', opacity: page < totalPages ? 1 : 0.5 }}
                  >
                    Далее →
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
  const endpoint = (slug, page) => `/api/mobile/posts/?tag=${slug}&page=${page}`
  return <PostListPage endpoint={endpoint} />
}

export function CategoryPosts() {
  const endpoint = (slug, page) => `/api/mobile/posts/?cat=${slug}&page=${page}`
  return <PostListPage endpoint={endpoint} />
}

export default PostListPage
