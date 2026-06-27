import { useState, useEffect } from "react"
import "../../../styles/Sidebar.css"

const Sidebar = ({ compact }) => {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch("/api/mobile/sidebar/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setData)
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="modern-sidebar"><p className="no-posts">Ошибка загрузки: {error}</p></div>
  if (!data) return <div className="modern-sidebar"><p className="no-posts">Загрузка...</p></div>

  if (compact) {
    return (
      <div className="modern-sidebar">
        <div className="sidebar-widget">
          <h4 className="widget-title">
            <i className="fas fa-clock"></i> Свежие статьи
          </h4>
          <div className="recent-posts">
            {data.recent_posts.length === 0 && (
              <p className="no-posts">Статей пока нет</p>
            )}
            {data.recent_posts.map((post) => (
              <a
                key={post.id}
                href={`/post/${post.slug}/`}
                className="text-decoration-none recent-post-card"
              >
                {post.photo && (
                  <div className="recent-post-img">
                    <img src={post.photo} alt={post.title} />
                  </div>
                )}
                <div className="recent-post-content">
                  <h5 className="recent-post-title">
                    {post.title.length > 50
                      ? post.title.slice(0, 50) + "..."
                      : post.title}
                  </h5>
                  <div className="recent-post-meta">
                    <span className="post-author">
                      <i className="fas fa-user"></i> {post.author}
                    </span>
                    <span className="post-time" title={post.time_create}>
                      <i className="fas fa-clock"></i>{" "}
                      {new Date(post.time_create).toLocaleDateString("ru-RU")}
                    </span>
                  </div>
                  <div className="recent-post-stats">
                    <span className="stat" title="Просмотры">
                      <i className="fas fa-eye"></i> {post.views}
                    </span>
                    <span className="stat" title="Лайки">
                      <i className="fas fa-heart"></i> {post.likes_count}
                    </span>
                  </div>
                </div>
              </a>
            ))}
          </div>
          <a href="/" className="text-decoration-none view-all-link">
            Смотреть все статьи <i className="fas fa-arrow-right"></i>
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="modern-sidebar">
      {/* Свежие статьи */}
      <div className="sidebar-widget">
        <h4 className="widget-title">
          <i className="fas fa-clock"></i> Свежие статьи
        </h4>
        <div className="recent-posts">
          {data.recent_posts.length === 0 && (
            <p className="no-posts">Статей пока нет</p>
          )}
          {data.recent_posts.map((post) => (
            <a
              key={post.id}
              href={`/post/${post.slug}/`}
              className="text-decoration-none recent-post-card"
            >
              {post.photo && (
                <div className="recent-post-img">
                  <img src={post.photo} alt={post.title} />
                </div>
              )}
              <div className="recent-post-content">
                <h5 className="recent-post-title">
                  {post.title.length > 50
                    ? post.title.slice(0, 50) + "..."
                    : post.title}
                </h5>
                <div className="recent-post-meta">
                  <span className="post-author">
                    <i className="fas fa-user"></i> {post.author}
                  </span>
                  <span className="post-time" title={post.time_create}>
                    <i className="fas fa-clock"></i>{" "}
                    {new Date(post.time_create).toLocaleDateString("ru-RU")}
                  </span>
                </div>
                <div className="recent-post-stats">
                  <span className="stat" title="Просмотры">
                    <i className="fas fa-eye"></i> {post.views}
                  </span>
                  <span className="stat" title="Лайки">
                    <i className="fas fa-heart"></i> {post.likes_count}
                  </span>
                </div>
              </div>
            </a>
          ))}
        </div>
        <a href="/" className="text-decoration-none view-all-link">
          Смотреть все статьи <i className="fas fa-arrow-right"></i>
        </a>
      </div>

      {/* Теги */}
      <div className="sidebar-widget">
        <h4 className="widget-title">
          <i className="fas fa-tags"></i> Теги
        </h4>
        <div className="tags-list">
          {data.tags.map((tag) => (
            <a
              key={tag.id}
              href={`/tag/${tag.slug}/`}
              className="tag"
            >
              {tag.name}
            </a>
          ))}
        </div>
      </div>

      {/* Категории */}
      <div className="sidebar-widget categories-widget">
        <h4 className="widget-title">
          <i className="fas fa-folder"></i> Категории
        </h4>
        <div className="category-list">
          {data.categories.map((cat) => (
            <a
              key={cat.id}
              href={`/category/${cat.slug}/`}
              className="text-decoration-none category-item"
            >
              <span className="category-name">{cat.name}</span>
              <span className="category-count">{cat.posts_count}</span>
            </a>
          ))}
        </div>
      </div>

      {/* Статистика */}
      <div className="sidebar-widget stats-widget">
        <h4 className="widget-title">
          <i className="fas fa-chart-bar"></i> Статистика
        </h4>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_posts}</div>
            <div className="stat-label">Статей</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_users}</div>
            <div className="stat-label">Авторов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{data.stats.total_comments}</div>
            <div className="stat-label">Комментариев</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
