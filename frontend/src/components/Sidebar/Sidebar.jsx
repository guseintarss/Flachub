import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import '../../styles/Sidebar.css'

const Sidebar = ({ compact }) => {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/mobile/sidebar/')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setData)
      .catch((e) => setError(e.message))
  }, [])

  if (error) return (
    <div className="modern-sidebar">
      <p className="no-posts">Не удалось загрузить сайдбар: {error}</p>
    </div>
  )

  if (!data) return (
    <div className="modern-sidebar">
      <div className="sidebar-widget">
        <div className="skeleton-line" style={{ width: '100%', height: 200, borderRadius: 12 }} />
      </div>
    </div>
  )

  const recentPosts = (
    <div className="recent-posts">
      {data.recent_posts.length === 0 && (
        <p className="no-posts">Публикаций пока нет</p>
      )}
      {data.recent_posts.map((post) => (
        <Link key={post.id} to={`/post/${post.slug}/`} className="recent-post-card">
          {post.photo && (
            <div className="recent-post-img">
              <img src={post.photo} alt="" loading="lazy" decoding="async" />
            </div>
          )}
          <div className="recent-post-content">
            <h5 className="recent-post-title">{post.title}</h5>
            <div className="recent-post-meta">
              <span className="post-author">{post.author}</span>
              <span className="post-time">
                {new Date(post.time_create).toLocaleDateString('ru-RU')}
              </span>
            </div>
            <div className="recent-post-stats">
              <span className="stat" title="Просмотры">
                <i className="far fa-eye" aria-hidden="true" /> {post.views}
              </span>
              <span className="stat" title="Лайки">
                <i className="far fa-heart" aria-hidden="true" /> {post.likes_count}
              </span>
            </div>
          </div>
        </Link>
      ))}
      <Link to="/" className="view-all-link">
        Все публикации <i className="fas fa-chevron-right" aria-hidden="true" />
      </Link>
    </div>
  )

  if (compact) {
    return (
      <div className="modern-sidebar">
        <div className="sidebar-widget">
          <h4 className="widget-title">Что читают</h4>
          {recentPosts}
        </div>
      </div>
    )
  }

  return (
    <div className="modern-sidebar">
      <div className="sidebar-widget">
        <h4 className="widget-title">Что читают</h4>
        {recentPosts}
      </div>

      <div className="sidebar-widget">
        <h4 className="widget-title">Теги</h4>
        <div className="tags-list">
          {data.tags.map((tag) => (
            <Link key={tag.id} to={`/tag/${tag.slug}/`} className="tag">
              {tag.name}
            </Link>
          ))}
        </div>
      </div>

      <div className="sidebar-widget categories-widget">
        <h4 className="widget-title">Категории</h4>
        <div className="category-list">
          {data.categories.map((cat) => (
            <Link key={cat.id} to={`/category/${cat.slug}/`} className="category-item">
              <span className="category-name">{cat.name}</span>
              <span className="category-count">{cat.posts_count}</span>
            </Link>
          ))}
        </div>
      </div>

      <div className="sidebar-widget stats-widget">
        <h4 className="widget-title">Сообщество</h4>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_posts}</div>
            <div className="stat-label">публикаций</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_users}</div>
            <div className="stat-label">авторов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_comments}</div>
            <div className="stat-label">комментариев</div>
          </div>
        </div>
        <p className="sidebar-note">Место, где практики делятся опытом без лишнего шума.</p>
      </div>
    </div>
  )
}

export default Sidebar
