import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  fetchPost, toggleLike, toggleBookmark, toggleFavorite,
  toggleSubscribe, addComment, deleteComment, toggleCommentLike,
} from '../api'
import '../styles/PostDetail.css'
import Sidebar from '../components/Sidebar/Sidebar'

const postTypeLabel = {
  article: 'Статья', news: 'Новость', idea: 'Идея', post: 'Пост',
}
const postTypeIcon = {
  article: 'fa-file-alt', news: 'fa-newspaper', idea: 'fa-lightbulb', post: 'fa-sticky-note',
}

function ReadingProgress() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const el = document.querySelector('.article-wrapper')
    if (!el) return
    function onScroll() {
      const scrolled = window.scrollY
      const wh = window.innerHeight
      const top = el.offsetTop
      const height = el.offsetHeight
      const start = top
      const end = top + height - wh
      const total = end - start
      const cur = scrolled - start
      let p = (cur / total) * 100
      p = Math.min(100, Math.max(0, p))
      setProgress(p)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return <div className="reading-progress-bar" style={{ width: `${progress}%` }} />
}

function ShareMenu({ slug }) {
  const [open, setOpen] = useState(false)
  const ref = useRef()
  const url = window.location.href

  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('click', onClick)
    return () => document.removeEventListener('click', onClick)
  }, [])

  return (
    <div className="share-dropdown" ref={ref}>
      <button className="action-btn share-toggle" onClick={() => setOpen(o => !o)} title="Поделиться">
        <i className="fas fa-share-alt" />
        <span className="share-count">4</span>
      </button>
      {open && (
        <div className="share-menu show">
            <div className="share-menu-header">
              <span>Поделиться</span>
              <button className="share-menu-close" onClick={() => setOpen(false)}>
                <i className="fas fa-times" />
              </button>
            </div>
            <div className="share-menu-body">
              <a href={`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(document.title)}`}
                target="_blank" rel="noopener noreferrer" className="share-menu-item share-telegram"
                onClick={() => setOpen(false)}>
                <i className="fab fa-telegram-plane" /> <span>Telegram</span>
              </a>
              <a href={`https://vk.com/share.php?url=${encodeURIComponent(url)}&title=${encodeURIComponent(document.title)}`}
                target="_blank" rel="noopener noreferrer" className="share-menu-item share-vk"
                onClick={() => setOpen(false)}>
                <i className="fab fa-vk" /> <span>ВКонтакте</span>
              </a>
              <a href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(document.title)}`}
                target="_blank" rel="noopener noreferrer" className="share-menu-item share-twitter"
                onClick={() => setOpen(false)}>
                <i className="fab fa-twitter" /> <span>Twitter</span>
              </a>
              <button className="share-menu-item share-copy" onClick={() => {
                navigator.clipboard.writeText(url)
                setOpen(false)
              }}>
                <i className="fas fa-link" /> <span>Копировать ссылку</span>
              </button>
            </div>
          </div>
        )}
      </div>
  )
}

function formatCommentDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric', month: 'long', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return dateStr }
}

function getAuthorName(comment) {
  if (typeof comment.author === 'string') return comment.author
  return comment.author?.username || 'Неизвестно'
}

function CommentItem({ comment, postId, currentUser, onCommentAction }) {
  const [liked, setLiked] = useState(comment.is_liked || false)
  const [likesCount, setLikesCount] = useState(comment.likes_count || 0)
  const [showReplyForm, setShowReplyForm] = useState(false)
  const [replyContent, setReplyContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [shareOpen, setShareOpen] = useState(false)
  const shareRef = useRef()
  const url = `${window.location.origin}/post/${postId}/`

  useEffect(() => {
    if (!shareOpen) return
    function onClick(e) {
      if (shareRef.current && !shareRef.current.contains(e.target)) setShareOpen(false)
    }
    document.addEventListener('click', onClick)
    return () => document.removeEventListener('click', onClick)
  }, [shareOpen])

  const handleLike = useCallback(async () => {
    const newLiked = !liked
    setLiked(newLiked)
    setLikesCount(c => newLiked ? c + 1 : Math.max(0, c - 1))
    try { await toggleCommentLike(comment.id) } catch {}
  }, [liked, comment.id])

  const handleReply = useCallback(async (e) => {
    e.preventDefault()
    if (!replyContent.trim()) return
    setSubmitting(true)
    setError('')
    try {
      const data = await addComment(postId, replyContent, String(comment.id))
      if (data.success) {
        setReplyContent('')
        setShowReplyForm(false)
        setError('')
        onCommentAction(data.comment)
      } else {
        setError(data.error || 'Ошибка при отправке ответа')
      }
    } catch {
      setError('Ошибка при отправке ответа')
    }
    setSubmitting(false)
  }, [replyContent, postId, comment.id, onCommentAction])

  const handleDelete = useCallback(async () => {
    if (!confirm('Удалить комментарий?')) return
    try {
      const data = await deleteComment(comment.id)
      if (data.success) onCommentAction(null, comment.id)
    } catch {}
  }, [comment.id, onCommentAction])

  const canDelete = currentUser && getAuthorName(comment) === currentUser

  return (
    <div className="comment" data-comment-id={comment.id}>
      <div className="comment-header">
        <div className="comment-author-info">
          <strong className="comment-author">{getAuthorName(comment)}</strong>
          <small className="comment-time">{formatCommentDate(comment.created_at)}</small>
          {comment.parent_author && (
            <small className="reply-to"><i className="fas fa-arrow-right" /> {comment.parent_author}</small>
          )}
        </div>
        <div className="comment-header-actions">
          {canDelete && (
            <button className="comment-action-btn delete-comment-btn" onClick={handleDelete} title="Удалить">
              <i className="fas fa-trash" />
            </button>
          )}
        </div>
      </div>
      <p className="comment-content">{comment.content}</p>
      <div className="comment-actions">
        <button className={`comment-action-btn comment-like-btn ${liked ? 'liked' : ''}`} onClick={handleLike}
          data-comment-id={comment.id} data-is-liked={String(liked)}>
          <i className={`fas fa-heart ${liked ? 'fa-bounce' : ''}`} />
          <span className="comment-likes-count">{likesCount}</span>
        </button>
        {!comment.parent_id && !comment.parent && (
          <button className="comment-action-btn comment-reply-btn" onClick={() => setShowReplyForm(o => !o)}>
            <i className="fas fa-reply" /> Ответить
          </button>
        )}
        <div className="comment-share-wrap" ref={shareRef}>
          <button className="comment-action-btn comment-share-btn" onClick={() => setShareOpen(o => !o)} title="Поделиться">
            <i className="fas fa-share-alt" />
          </button>
          {shareOpen && (
            <div className="comment-share-menu">
              <a href={`https://t.me/share/url?url=${encodeURIComponent(url)}`}
                target="_blank" rel="noopener noreferrer" className="share-menu-item share-telegram"
                onClick={() => setShareOpen(false)}>
                <i className="fab fa-telegram-plane" /> Telegram
              </a>
              <a href={`https://vk.com/share.php?url=${encodeURIComponent(url)}`}
                target="_blank" rel="noopener noreferrer" className="share-menu-item share-vk"
                onClick={() => setShareOpen(false)}>
                <i className="fab fa-vk" /> ВКонтакте
              </a>
              <button className="share-menu-item share-copy" onClick={() => {
                navigator.clipboard.writeText(url)
                setShareOpen(false)
              }}>
                <i className="fas fa-link" /> Копировать
              </button>
            </div>
          )}
        </div>
      </div>
      {showReplyForm && !comment.parent && (
        <form className="reply-form" onSubmit={handleReply}>
          <textarea rows={2} className="form-control reply-textarea" placeholder="Напишите ответ..."
            value={replyContent} onChange={e => setReplyContent(e.target.value)} />
          {error && <div className="comment-error">{error}</div>}
          <div className="reply-form-actions">
            <button type="submit" className="btn btn-sm btn-primary" disabled={submitting || !replyContent.trim()}>
              {submitting ? <i className="fas fa-spinner fa-spin" /> : null} Отправить
            </button>
            <button type="button" className="btn btn-sm btn-secondary" onClick={() => { setShowReplyForm(false); setReplyContent(''); setError('') }}>
              Отмена
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

function CommentsSection({ comments: initialComments, postId, currentUser }) {
  const [comments, setComments] = useState(initialComments || [])
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { setComments(initialComments || []) }, [initialComments])

  const handleAddComment = useCallback(async (e) => {
    e.preventDefault()
    if (!content.trim()) return
    setSubmitting(true)
    setError('')
    try {
      const data = await addComment(postId, content)
      if (data.success) {
        setContent('')
        setComments(prev => [data.comment, ...prev])
      } else {
        setError(data.error || 'Ошибка при отправке комментария')
      }
    } catch (err) {
      setError('Ошибка при отправке комментария')
    }
    setSubmitting(false)
  }, [content, postId])

  const handleCommentAction = useCallback((newComment, deleteId) => {
    if (deleteId) {
      setComments(prev => prev.filter(c => c.id !== deleteId))
    } else if (newComment) {
      setComments(prev => {
        if (newComment.parent_id || newComment.parent) {
          const parentId = newComment.parent_id || newComment.parent
          return prev.map(c => c.id === parentId ? { ...c, replies: [...(c.replies || []), newComment] } : c)
        }
        return [newComment, ...prev]
      })
    }
  }, [])

  const topComments = comments.filter(c => !c.parent)

  return (
    <div className="comments-section">
      <div className="comments-header">
        <h3><i className="fas fa-comments" /> Комментарии ({comments.length})</h3>
      </div>

      <form className="comment-form" onSubmit={handleAddComment}>
        <textarea rows={3} className="form-control" placeholder="Напишите комментарий..."
          value={content} onChange={e => setContent(e.target.value)} />
        {error && <div className="comment-error">{error}</div>}
        <div className="comment-form-actions">
          <button type="submit" className="btn btn-primary" disabled={submitting || !content.trim()}>
            {submitting ? <i className="fas fa-spinner fa-spin" /> : null} Отправить
          </button>
        </div>
      </form>

      <div className="comments-list">
        {topComments.length === 0 && (
          <div className="no-comments">
            <i className="fas fa-comments" />
            <p>Комментариев пока нет. Будьте первым!</p>
          </div>
        )}
        {topComments.map(comment => (
          <div key={comment.id}>
            <CommentItem comment={comment} postId={postId} currentUser={currentUser}
              onCommentAction={handleCommentAction} />
            {comment.replies && comment.replies.length > 0 && (
              <div className="comment-replies">
                {comment.replies.map(reply => (
                  <CommentItem key={reply.id} comment={reply} postId={postId}
                    currentUser={currentUser} onCommentAction={handleCommentAction} />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function PostDetail() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [liked, setLiked] = useState(false)
  const [likesCount, setLikesCount] = useState(0)
  const [favorited, setFavorited] = useState(false)
  const [subscribed, setSubscribed] = useState(false)

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetchPost(slug)
      .then(data => {
        setPost(data)
        setLiked(data.is_liked || false)
        setLikesCount(data.likes_count || 0)
        setFavorited(data.is_favorited || false)
        setSubscribed(data.is_subscribed || false)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [slug])

  useEffect(() => {
    if (!post) return
    function onScroll() {
      const btn = document.getElementById('scrollToTop')
      if (!btn) return
      if (window.scrollY > 300) btn.classList.add('visible')
      else btn.classList.remove('visible')
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [post])

  useEffect(() => {
    if (!post) return
    const imgs = document.querySelectorAll('.article-body img:not([loading])')
    imgs.forEach(img => { img.loading = 'lazy' })
  }, [post])

  const handleLike = useCallback(async () => {
    if (!post) return
    const newLiked = !liked
    setLiked(newLiked)
    setLikesCount(c => newLiked ? c + 1 : Math.max(0, c - 1))
    try { await toggleLike(post.id) } catch {}
  }, [liked, post])

  const handleFavorite = useCallback(async () => {
    if (!post) return
    setFavorited(f => !f)
    try { await toggleFavorite(post.id) } catch {}
  }, [post])

  const isOwnPost = post?.current_user && post?.author?.username === post.current_user

  const handleSubscribe = useCallback(async () => {
    if (!post || isOwnPost) return
    setSubscribed(s => !s)
    try { await toggleSubscribe(post.author.id) } catch {}
  }, [post, isOwnPost])

  if (loading) return (
    <div className="page">
      <div className="pg-container">
        <div className="post-loading">Загрузка...</div>
      </div>
    </div>
  )

  if (error) return (
    <div className="page">
      <div className="pg-container">
        <div className="post-error">Ошибка загрузки: {error}</div>
      </div>
    </div>
  )

  if (!post) return null

  return (
    <div className="page">
      <ReadingProgress />

      <div className="pg-container layout">
        <div className="content">
          <div className="article-container">
          <div className="article-wrapper">
            <div className="article-header">
              <div className="post-meta-header">
                <div className="author-info">
                  <Link to={`/user/${post.author.username}/`} className="author-avatar-link">
                    {post.author.avatar ? (
                      <img className="author-avatar" src={post.author.avatar} alt={post.author.username} />
                    ) : (
                      <div className="author-avatar author-avatar-placeholder">
                        {post.author.username?.[0]?.toUpperCase() || '?'}
                      </div>
                    )}
                  </Link>
                  <div className="author-details">
                    <Link to={`/user/${post.author.username}/`} className="author-name">
                      {post.author.username}
                    </Link>
                    <span className="post-date" title={post.time_update}>
                      {new Date(post.time_update).toLocaleDateString('ru-RU', {
                        day: 'numeric', month: 'long', year: 'numeric',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
                {!isOwnPost && post.current_user && (
                <button id="subscribe-btn"
                  className={`btn btn-sm ${subscribed ? 'btn-secondary' : 'btn-primary'}`}
                  onClick={handleSubscribe}>
                  {subscribed ? 'Отписаться' : 'Подписаться'}
                </button>
                )}
              </div>

              <h1 className="article-title">{post.title}</h1>

              <div className="article-meta">
                {post.category && (
                  <Link to={`/category/${post.category.slug}/`} className="meta-badge">
                    <i className="fas fa-folder" /> {post.category.name}
                  </Link>
                )}
                <span className="meta-badge">
                  <i className="fas fa-clock" /> {post.reading_time_minutes} мин
                </span>
                <span className="meta-badge">
                  <i className="fas fa-eye" /> {post.views}
                </span>
                {post.post_type && (
                  <span className="meta-badge">
                    <i className={`fas ${postTypeIcon[post.post_type] || 'fa-tag'}`} />
                    {postTypeLabel[post.post_type] || 'Пост'}
                  </span>
                )}
              </div>

              {post.photo && (
                <div className="article-cover">
                  <img src={post.photo} alt={post.title} loading="lazy" />
                </div>
              )}
            </div>

            <div className="article-body" dangerouslySetInnerHTML={{ __html: post.content }} />

            {post.tags && post.tags.length > 0 && (
              <div className="article-tags">
                <span className="tags-label"><i className="fas fa-tags" /> Теги:</span>
                {post.tags.map(tag => (
                  <Link key={tag.id} to={`/tag/${tag.slug}/`} className="tag-chip">{tag.tag}</Link>
                ))}
              </div>
            )}

            <div className="article-actions">
              <button id="like-btn"
                className={`action-btn ${liked ? 'liked' : ''}`}
                onClick={handleLike}
                data-post-id={post.id} data-liked={String(liked)}>
                <i className="fas fa-heart" />{likesCount}
              </button>

              <button id="favorite-btn"
                className={`action-btn ${favorited ? 'favorited' : ''}`}
                onClick={handleFavorite}
                data-post-id={post.id} data-favorited={String(favorited)}>
                <i className="fas fa-star" />
              </button>

              <ShareMenu slug={slug} />
            </div>
          </div>

          {post.similar_posts && post.similar_posts.length > 0 && (
            <div className="similar-articles">
              <h3><i className="fas fa-copy" /> Читайте также</h3>
              <div className="similar-posts-grid">
                {post.similar_posts.map(p => (
                  <Link key={p.id} to={`/post/${p.slug}/`} className="similar-article-card">
                    <div className="similar-article-image">
                      {p.photo ? (
                        <img src={p.photo} alt={p.title} />
                      ) : (
                        <div className="similar-article-placeholder">
                          <i className="fas fa-file-alt" />
                        </div>
                      )}
                    </div>
                    <div className="similar-article-content">
                      <h4 className="similar-article-title">
                        {p.title.length > 60 ? p.title.slice(0, 60) + '...' : p.title}
                      </h4>
                      <div className="similar-article-meta">
                        {p.category && (
                          <span className="similar-article-category">
                            <i className="fas fa-folder" /> {p.category.name}
                          </span>
                        )}
                        <span className="similar-article-views">
                          <i className="fas fa-eye" /> {p.views || 0}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          <CommentsSection comments={post.comments || []} postId={post.id}
            currentUser={post.current_user} />
          </div>
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>

      <button id="scrollToTop" className="scroll-to-top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
        <i className="fas fa-arrow-up" />
      </button>
    </div>
  )
}

export default PostDetail
