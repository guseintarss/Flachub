import { useState, useCallback } from 'react'
import { toggleLike } from '../../api'
import UserAvatar from '../UserAvatar'

const PostCard = ({ post, extra, badge, noReadMore }) => {
  const [liked, setLiked] = useState(post.is_liked || false)
  const [likesCount, setLikesCount] = useState(post.likes_count || 0)

  const handleLike = useCallback(async (e) => {
    e.preventDefault()
    e.stopPropagation()
    const newLiked = !liked
    setLiked(newLiked)
    setLikesCount(c => newLiked ? c + 1 : Math.max(0, c - 1))
    try { await toggleLike(post.id) } catch {}
  }, [liked, post.id])

  const postTypeIcon = {
    article: "fa-file-alt",
    news: "fa-newspaper",
    idea: "fa-lightbulb",
    post: "fa-sticky-note",
  }

  const postTypeLabel = {
    article: "Статья",
    news: "Новость",
    idea: "Идея",
    post: "Пост",
  }

  return (
    <article className={`post ${post.post_type ? `post-type-${post.post_type}` : ""}`}>
      <div className="post-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <div className="post-author" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <a href={`/user/${post.author?.username || ""}/`} style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "8px", color: "inherit" }}>
            <UserAvatar user={post.author} size={32} />
            <div className="author-info">
              <span className="author-name" style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                {post.author?.username || "Неизвестно"}
              </span>
              <span className="post-time" style={{ fontSize: "0.75rem", opacity: 0.7, display: "block" }}>
                {new Date(post.time_create).toLocaleDateString("ru-RU", {
                  day: "numeric", month: "long", year: "numeric",
                })}
              </span>
            </div>
          </a>
        </div>
        <div className="post-meta-badges" style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          <span className="post-type-badge" style={{ fontSize: "0.75rem", opacity: 0.7 }}>
            <i className={`fas ${postTypeIcon[post.post_type] || "fa-sticky-note"}`}></i> {postTypeLabel[post.post_type] || "Пост"}
          </span>
          {post.category && (
            <span className="category-badge" style={{ fontSize: "0.75rem", padding: "2px 8px", borderRadius: 10, background: "var(--tags-bg)", color: "var(--tags-color)" }}>
              {post.category.name}
            </span>
          )}
        </div>
      </div>

      <div className="post-body">
        <h2 className="post-title" style={{ margin: "0 0 8px 0", fontSize: "1.15rem" }}>
          <a href={`/post/${post.slug}/`} style={{ textDecoration: "none", color: "inherit" }}>
            {post.title}
          </a>
        </h2>

        {post.photo && (
          <div className="post-cover" style={{ marginBottom: 10 }}>
            <a href={`/post/${post.slug}/`}>
              <img className="cover-image" src={post.photo} alt={post.title} style={{ width: "100%", maxHeight: 220, objectFit: "cover", borderRadius: 8 }} />
            </a>
          </div>
        )}

        {badge}

        {post.excerpt && (
          <div className="post-excerpt" style={{ opacity: 0.85, lineHeight: 1.55 }} dangerouslySetInnerHTML={{ __html: post.excerpt }} />
        )}
      </div>

      <div className="post-footer" style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
        <div className="post-stats-and-btn" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div className="post-stats" style={{ display: "flex", gap: 12, fontSize: "0.78rem", opacity: 0.7 }}>
            <span className="stat-item" title="Просмотры">
              <i className="fas fa-eye"></i> {post.views || 0}
            </span>
            <button className={`stat-item like-btn ${liked ? 'liked' : ''}`}
              title="Лайки" onClick={handleLike}>
              <i className={`fas fa-heart ${liked ? 'fa-bounce' : ''}`}></i> {likesCount}
            </button>
            <span className="stat-item" title="Время чтения">
              <i className="fas fa-clock"></i> {post.reading_time_minutes || 1} мин
            </span>
            <span className="stat-item" title="Комментарии">
              <i className="fas fa-comment"></i> {post.comments_count || 0}
            </span>
          </div>
          {!noReadMore && (
            <a className="read-more" href={`/post/${post.slug}/`} style={{ textDecoration: "none" }}>
              Читать далее <i className="fas fa-arrow-right"></i>
            </a>
          )}
        </div>
        {extra}
      </div>
    </article>
  )
}

export default PostCard
