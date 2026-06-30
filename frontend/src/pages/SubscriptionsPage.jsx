import { useState, useEffect } from 'react'
import PostCard from '../components/Feed/PostCard'
import UserAvatar from '../components/UserAvatar'
import Sidebar from '../components/Sidebar/Sidebar'
import '../styles/subscriptions.css'

function SubscriptionsSkeleton() {
  return (
    <div className="content">
      <div className="subs-authors-skeleton">
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="subs-author-skel">
            <div className="skeleton-circle" style={{ width: 56, height: 56 }} />
            <div className="skeleton-line" style={{ width: 60, height: 12, marginTop: 8 }} />
          </div>
        ))}
      </div>
      {[1, 2, 3].map(card => (
        <div key={card} className="post" style={{ marginBottom: 20, padding: 20, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div className="skeleton-circle" style={{ width: 36, height: 36 }} />
              <div>
                <div className="skeleton-line" style={{ width: 100, height: 13, marginBottom: 4 }} />
                <div className="skeleton-line" style={{ width: 70, height: 11 }} />
              </div>
            </div>
          </div>
          <div className="skeleton-line" style={{ width: '60%', height: 20, marginBottom: 10 }} />
          <div className="skeleton-line" style={{ width: '100%', height: 13, marginBottom: 4 }} />
          <div className="skeleton-line" style={{ width: '85%', height: 13, marginBottom: 16 }} />
        </div>
      ))}
    </div>
  )
}

function SubscriptionsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/mobile/subscriptions/feed/?page=${page}`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(d => {
        setData(d)
        setTotalPages(d.total_pages || 0)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [page])

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          {loading && page === 1 ? (
            <SubscriptionsSkeleton />
          ) : data ? (
            <>
              {data.authors && data.authors.length > 0 && (
                <div className="subs-authors-row">
                  <div className="subs-authors-header">
                    <h1><i className="fas fa-users"></i> Подписки</h1>
                    <p>Новые публикации от авторов, на которых вы подписаны</p>
                  </div>
                  <div className="subs-authors-scroll-wrap">
                    <button className="subs-scroll-btn subs-scroll-left" onClick={e => {
                    const el = e.currentTarget.parentElement.querySelector('.subs-authors-scroll')
                    el.scrollBy({ left: -300, behavior: 'smooth' })
                  }}><i className="fas fa-chevron-left"></i></button>
                  <div className="subs-authors-scroll">
                    {data.authors.map(a => (
                      <a key={a.id} href={`/user/${a.username}/`} className="subs-author-card">
                        <UserAvatar user={{ avatar: a.avatar, username: a.username, first_name: a.first_name }} size={56} />
                        <span className="subs-author-name">{a.first_name || a.username}</span>
                        <span className="subs-author-posts">{a.posts_count} {a.posts_count === 1 ? 'пост' : a.posts_count >= 2 && a.posts_count <= 4 ? 'поста' : 'постов'}</span>
                      </a>
                    ))}
                  </div>
                  <button className="subs-scroll-btn subs-scroll-right" onClick={e => {
                    const el = e.currentTarget.parentElement.querySelector('.subs-authors-scroll')
                    el.scrollBy({ left: 300, behavior: 'smooth' })
                  }}><i className="fas fa-chevron-right"></i></button>
                    </div>
                  </div>
              )}

              {data.authors && data.authors.length === 0 && (
                <div className="subs-empty">
                  <i className="fas fa-users"></i>
                  <h3>Вы пока ни на кого не подписаны</h3>
                  <p>Подпишитесь на авторов, чтобы видеть их новые публикации в этой ленте</p>
                  <a href="/" className="btn btn-primary">Перейти к ленте</a>
                </div>
              )}

              <div className="subs-posts">
                {data.posts && data.posts.map(post => (
                  <PostCard key={post.id} post={post} />
                ))}
                {data.posts && data.posts.length === 0 && data.authors && data.authors.length > 0 && (
                  <div className="subs-empty" style={{ marginTop: 20 }}>
                    <i className="fas fa-newspaper"></i>
                    <h3>Новых публикаций пока нет</h3>
                    <p>Авторы ещё ничего не опубликовали. Загляните позже!</p>
                  </div>
                )}
              </div>

              {totalPages > 1 && (
                <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 24 }}>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                    <button key={p} className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => setPage(p)} disabled={p === page}>
                      {p}
                    </button>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="subs-empty">
              <i className="fas fa-exclamation-triangle"></i>
              <h3>Ошибка загрузки</h3>
              <p>Не удалось загрузить ленту подписок. Попробуйте позже.</p>
              <button className="btn btn-primary" onClick={() => setPage(1)}>Повторить</button>
            </div>
          )}
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export default SubscriptionsPage