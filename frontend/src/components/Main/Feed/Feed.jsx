import { useState, useEffect } from "react"
import PostCard from "./PostCard"

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
  if (loading) return <div className="content"><p style={{ color: "var(--muted)" }}>Загрузка...</p></div>

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
