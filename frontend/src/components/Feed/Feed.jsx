import { useState, useEffect } from "react"
import PostCard from "./PostCard"

function FeedSkeleton() {
  return (
    <div className="content">
      {[1, 2, 3, 4].map(card => (
        <div key={card} className="post" style={{ marginBottom: 20, padding: 20, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div className="skeleton-circle" style={{ width: 36, height: 36 }} />
              <div>
                <div className="skeleton-line" style={{ width: 100, height: 13, marginBottom: 4 }} />
                <div className="skeleton-line" style={{ width: 70, height: 11 }} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <div className="skeleton-line" style={{ width: 50, height: 18, borderRadius: 12 }} />
              <div className="skeleton-line" style={{ width: 60, height: 18, borderRadius: 12 }} />
            </div>
          </div>
          <div className="skeleton-line" style={{ width: '60%', height: 20, marginBottom: 10 }} />
          {card % 2 === 0 && <div className="skeleton-line" style={{ width: '100%', height: 180, borderRadius: 8, marginBottom: 10 }} />}
          <div className="skeleton-line" style={{ width: '100%', height: 13, marginBottom: 4 }} />
          <div className="skeleton-line" style={{ width: '85%', height: 13, marginBottom: 16 }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 12, borderTop: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', gap: 16 }}>
              <div className="skeleton-line" style={{ width: 40, height: 14 }} />
              <div className="skeleton-line" style={{ width: 40, height: 14 }} />
              <div className="skeleton-line" style={{ width: 40, height: 14 }} />
              <div className="skeleton-line" style={{ width: 40, height: 14 }} />
            </div>
            <div className="skeleton-line" style={{ width: 90, height: 14 }} />
          </div>
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

  if (error) return <div className="content"><p style={{ color: "var(--muted)" }}>Ошибка загрузки: {error}</p></div>
  if (loading) return <FeedSkeleton />

  if (posts.length === 0) {
    return (
      <div className="content">
        <div className="empty-feed" style={{ textAlign: "center", padding: 60, color: "var(--muted)" }}>
          <i className="fas fa-inbox" style={{ fontSize: 48, marginBottom: 16 }}></i>
          <h3>Пока нет публикаций</h3>
          <p>Будьте первым, кто опубликует материал!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="content">
      <div className="feed-container">
        {posts.map((p) => (
          <PostCard key={p.id} post={p} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination" style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            style={{ padding: "8px 16px", borderRadius: 8, border: "1px solid var(--border)", background: "var(--surface)", cursor: page > 1 ? "pointer" : "not-allowed", opacity: page > 1 ? 1 : 0.5 }}
          >
            ← Назад
          </button>
          <span style={{ display: "flex", alignItems: "center", padding: "0 12px", fontSize: "0.9rem", color: "var(--muted)" }}>
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            style={{ padding: "8px 16px", borderRadius: 8, border: "1px solid var(--border)", background: "var(--surface)", cursor: page < totalPages ? "pointer" : "not-allowed", opacity: page < totalPages ? 1 : 0.5 }}
          >
            Далее →
          </button>
        </div>
      )}
    </div>
  )
}

export default Feed
