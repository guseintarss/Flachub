import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { toggleLike } from '../../api'
import { reviewStatusKey, reviewStatusLabel } from '../../reviewMeta'
import UserAvatar from '../UserAvatar'

const POST_TYPE_ICONS = {
  article: 'fa-file-alt',
  news: 'fa-newspaper',
  idea: 'fa-lightbulb',
  post: 'fa-sticky-note',
  review: 'fa-code',
}

const POST_TYPE_LABELS = {
  article: 'Статья',
  news: 'Новость',
  idea: 'Идея',
  post: 'Пост',
  review: 'Разбор',
}

const PostCard = ({ post, extra, badge, noReadMore, featured = false }) => {
  const [liked, setLiked] = useState(post.is_liked || false)
  const [likesCount, setLikesCount] = useState(post.likes_count || 0)

  const handleLike = useCallback(async (e) => {
    e.preventDefault()
    e.stopPropagation()
    const newLiked = !liked
    setLiked(newLiked)
    setLikesCount(c => newLiked ? c + 1 : Math.max(0, c - 1))
    try { await toggleLike(post.id) } catch { /* лайк не критичен */ }
  }, [liked, post.id])

  const type = post.post_type || 'post'
  const author = post.author || {}
  const authorName = author.username || 'Неизвестно'
  const date = new Date(post.time_create).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
  })

  return (
    <article className={`post post-type-${type}${featured ? ' post--featured' : ''}`}>
      <div className="post-header">
        <div className="post-author">
          <Link to={`/user/${author.username || ''}/`} className="post-author-link">
            <UserAvatar user={author} size={featured ? 40 : 30} />
            <div className="author-info">
              <span className="author-name">{authorName}</span>
              <span className="post-time">{date}</span>
            </div>
          </Link>
        </div>
        <div className="post-meta-badges">
          <span className={`post-type-badge post-type-badge--${type}`}>
            <i className={`fas ${POST_TYPE_ICONS[type] || 'fa-sticky-note'}`} aria-hidden="true" />
            {POST_TYPE_LABELS[type] || 'Пост'}
          </span>
          {type === 'review' && (
            <span className={`review-status-badge review-status-${reviewStatusKey(post.review_status)}`}>
              {reviewStatusLabel(post.review_status)}
            </span>
          )}
          {type === 'review' && post.code_language && (
            <span className="review-language-badge">
              <i className="fas fa-code" aria-hidden="true" /> {post.code_language}
            </span>
          )}
          {post.category && (
            <Link to={`/category/${post.category.slug}/`} className="category-badge">
              {post.category.name}
            </Link>
          )}
        </div>
      </div>

      <div className="post-body">
        <h2 className="post-title">
          <Link to={`/post/${post.slug}/`}>{post.title}</Link>
        </h2>

        {post.photo && (
          <Link to={`/post/${post.slug}/`} className="post-cover" tabIndex={-1} aria-hidden="true">
            <img
              className="cover-image"
              src={post.photo}
              alt=""
              loading="lazy"
              decoding="async"
            />
          </Link>
        )}

        <div className="post-text">
          {badge}
          {post.excerpt && (
            <div className="post-excerpt" dangerouslySetInnerHTML={{ __html: post.excerpt }} />
          )}
        </div>
      </div>

      <div className="post-footer">
        <div className="post-stats">
          <span className="stat-item" title="Просмотры">
            <i className="far fa-eye" aria-hidden="true" /> {post.views || 0}
          </span>
          <button
            type="button"
            className={`stat-item like-btn${liked ? ' is-liked' : ''}`}
            title={liked ? 'Убрать лайк' : 'Поставить лайк'}
            aria-pressed={liked}
            onClick={handleLike}
          >
            <i className={`${liked ? 'fas' : 'far'} fa-heart`} aria-hidden="true" /> {likesCount}
          </button>
          <span className="stat-item" title="Время чтения">
            <i className="far fa-clock" aria-hidden="true" /> {post.reading_time_minutes || 1} мин
          </span>
          <span className="stat-item" title="Комментарии">
            <i className="far fa-comment" aria-hidden="true" /> {post.comments_count || 0}
          </span>
        </div>
        {!noReadMore && (
          <Link className="read-more" to={`/post/${post.slug}/`}>
            Читать <i className="fas fa-chevron-right" aria-hidden="true" />
          </Link>
        )}
      </div>
      {extra}
    </article>
  )
}

export default PostCard
