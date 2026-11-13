import { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { toggleSubscribe, deletePost, createChat } from '../api'
import PostCard from '../components/Feed/PostCard'
import UserAvatar from '../components/UserAvatar'
import { ProfileSkeleton } from '../components/Skeleton'
import '../styles/Sidebar.css'

function ProfilePage() {
  const { username } = useParams()
  const { user: currentUser, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('published')
  const [posts, setPosts] = useState([])
  const [drafts, setDrafts] = useState([])
  const [favorites, setFavorites] = useState([])
  const [postsLoading, setPostsLoading] = useState(false)
  const [subscribing, setSubscribing] = useState(false)
  const [userStats, setUserStats] = useState(null)
  const [recentUserPosts, setRecentUserPosts] = useState([])
  const [reviews, setReviews] = useState({ given: [], requested: [] })
  const [reviewsLoading, setReviewsLoading] = useState(true)

  const isOwn = !username

  const fetchProfile = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      let res
      if (isOwn) {
        res = await fetch('/api/mobile/me/')
      } else {
        res = await fetch(`/api/mobile/users/by-username/${username}/`)
      }
      if (!res.ok) {
        if (res.status === 404) throw new Error('Пользователь не найден')
        throw new Error('Ошибка загрузки профиля')
      }
      const data = await res.json()
      setProfile(data)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }, [isOwn, username])

  useEffect(() => {
    if (!authLoading) {
      if (isOwn && !currentUser) {
        navigate('/login/', { replace: true })
        return
      }
      // Профиль загружается после восстановления сессии.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchProfile()
    }
  }, [authLoading, isOwn, currentUser, navigate, fetchProfile])

  useEffect(() => {
    if (!profile) return

    async function loadPosts() {
      setPostsLoading(true)
      try {
        const res = await fetch(`/api/mobile/posts/?author=${profile.id}&page_size=50`)
        if (res.ok) {
          const data = await res.json()
          setPosts(data.results || [])
        }
      } catch { /* блок профиля не критичен */ }
      setPostsLoading(false)
    }

    async function loadDrafts() {
      if (!isOwn) return
      try {
        const res = await fetch(`/api/mobile/posts/?author=${profile.id}&is_published=0&page_size=50`)
        if (res.ok) {
          const data = await res.json()
          setDrafts(data.results || [])
        }
      } catch { /* блок профиля не критичен */ }
    }

    async function loadFavorites() {
      if (!isOwn) return
      try {
        const res = await fetch(`/api/mobile/users/${profile.id}/favorites/`)
        if (res.ok) {
          const data = await res.json()
          setFavorites(data.results || data || [])
        }
      } catch { /* блок профиля не критичен */ }
    }

    async function loadStats() {
      try {
        const res = await fetch(`/api/mobile/users/${profile.id}/stats/`)
        if (res.ok) setUserStats(await res.json())
      } catch { /* блок профиля не критичен */ }
    }

    async function loadRecentPosts() {
      try {
        const res = await fetch(`/api/mobile/posts/?author=${profile.id}&page_size=5`)
        if (res.ok) {
          const data = await res.json()
          setRecentUserPosts(data.results || [])
        }
      } catch { /* блок профиля не критичен */ }
    }

    async function loadReviews() {
      setReviewsLoading(true)
      try {
        const [givenRes, requestedRes] = await Promise.all([
          fetch(`/api/mobile/users/${profile.id}/reviews/?role=given&page_size=50`),
          fetch(`/api/mobile/users/${profile.id}/reviews/?role=requested&page_size=50`),
        ])
        const given = givenRes.ok ? await givenRes.json() : null
        const requested = requestedRes.ok ? await requestedRes.json() : null
        setReviews({
          given: given?.results || (Array.isArray(given) ? given : []),
          requested: requested?.results || (Array.isArray(requested) ? requested : []),
        })
      } catch (e) {
        console.error('[Profile] reviews load failed:', e)
      }
      setReviewsLoading(false)
    }

    loadPosts()
    loadDrafts()
    loadFavorites()
    loadStats()
    loadRecentPosts()
    loadReviews()
  }, [profile, isOwn])

  async function handleSubscribe() {
    if (!currentUser) {
      navigate('/login/', { replace: true })
      return
    }
    setSubscribing(true)
    try {
      const data = await toggleSubscribe(profile.id)
      if (data.success) {
        setProfile(prev => ({
          ...prev,
          is_subscribed: data.subscribed,
          followers_count: data.subscribers_count,
        }))
      }
    } catch { /* подписка не критична */ }
    setSubscribing(false)
  }

  async function handleDelete(post) {
    if (!window.confirm(`Вы уверены, что хотите удалить статью "${post.title}"?`)) return
    try {
      await deletePost(post.slug)
      setPosts(prev => prev.filter(p => p.id !== post.id))
      setDrafts(prev => prev.filter(p => p.id !== post.id))
      setReviews(prev => ({
        given: prev.given.filter(p => p.id !== post.id),
        requested: prev.requested.filter(p => p.id !== post.id),
      }))
    } catch {
      alert('Ошибка при удалении статьи')
    }
  }

  if (loading || authLoading) return <ProfileSkeleton />

  if (error) {
    return (
      <main className="page">
        <div className="pg-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <i className="fas fa-exclamation-circle" style={{ fontSize: '3rem', color: 'var(--muted)', marginBottom: 16 }} />
          <h3>{error}</h3>
          <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>На главную</Link>
        </div>
      </main>
    )
  }

  if (!profile) return null

  const bannerStyle = profile.banner_image
    ? { background: `url(${profile.banner_image}) center/cover no-repeat` }
    : { background: `linear-gradient(135deg, ${profile.banner_gradient_start || '#2c5d48'} 0%, ${profile.banner_gradient_end || '#7a8f63'} 100%)` }

  const tabs = [
    { key: 'published', label: 'Опубликованные', icon: 'fa-check-circle' },
    { key: 'reviews', label: 'Разборы', icon: 'fa-code' },
  ]
  if (isOwn) {
    tabs.push({ key: 'drafts', label: 'Черновики', icon: 'fa-file' })
    tabs.push({ key: 'favorites', label: 'Избранные', icon: 'fa-heart' })
  }

  const displayName = profile.first_name || profile.last_name
    ? `${profile.last_name || ''} ${profile.first_name || ''}`.trim()
    : null

  return (
    <main className="page">
      <div className="pg-container">
        <div className="author-profile-page">
          <div className="author-hero">
            <div className="author-hero-bg" style={bannerStyle} />
            <div className="author-hero-content">
              <div className="author-hero-top">
                <div>
                  <UserAvatar user={profile} size={120} />
                </div>

                <div className="author-hero-info">
                  <div className="author-hero-name-row">
                    <h1 className="author-hero-username">{profile.username}</h1>
                    {profile.current_level && (
                      <span className="user-level-badge" title={profile.current_level.name}
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: 4,
                          padding: '2px 10px', borderRadius: 20,
                          background: `${profile.current_level.color}20`,
                          color: profile.current_level.color,
                          fontSize: '0.8rem', fontWeight: 600,
                        }}>
                        <span>{profile.current_level.icon}</span>
                        <span>{profile.current_level.name}</span>
                      </span>
                    )}
                  </div>
                  {displayName && (
                    <p className="author-hero-fullname">{displayName}</p>
                  )}
                </div>

                {!isOwn && currentUser && (
                  <div className="author-hero-actions">
                    <button className="btn btn-outline-primary"
                      onClick={() => createChat(profile.id).then(chat => navigate(`/chat/${chat.id}/`))}
                      style={{ padding: '7px 18px', fontSize: '0.82rem', fontWeight: 600, borderRadius: 10, whiteSpace: 'nowrap' }}>
                      <i className="fas fa-envelope" /> Написать
                    </button>
                    <button id="subscribe-btn"
                      className={`btn ${profile.is_subscribed ? 'btn-secondary' : 'btn-primary'}`}
                      onClick={handleSubscribe}
                      disabled={subscribing}>
                      {profile.is_subscribed ? 'Отписаться' : 'Подписаться'}
                    </button>
                  </div>
                )}
                {isOwn && (
                <div className="author-actions">
                  <Link className="btn btn-secondary" to="/dashboard/" title="Дашборд автора">
                    <i className="fas fa-chart-line" />
                  </Link>
                  <Link className="btn btn-primary" to="/profile/edit/" title="Настройки профиля">
                    <i className="fas fa-cog" />
                  </Link>
                </div>
              )}
              </div>

              {profile.bio && (
                <p className="author-hero-bio">{profile.bio}</p>
              )}

              <div className="author-stats-row">
                <div className="author-stat-card">
                  <div className="author-stat-icon"><i className="fas fa-star" /></div>
                  <div className="author-stat-value">{profile.reputation || 0}</div>
                  <div className="author-stat-label">Репутация</div>
                </div>
                <div className="author-stat-card">
                  <div className="author-stat-icon"><i className="fas fa-users" /></div>
                  <div className="author-stat-value">{profile.followers_count || 0}</div>
                  <div className="author-stat-label">Подписчиков</div>
                </div>
                <div className="author-stat-card">
                  <div className="author-stat-icon"><i className="fas fa-user-plus" /></div>
                  <div className="author-stat-value">{profile.following_count || 0}</div>
                  <div className="author-stat-label">Подписок</div>
                </div>
              </div>

              {profile.achievements && profile.achievements.length > 0 && (
                <div className="author-achievements">
                  <h4 className="achievements-title">
                    <i className="fas fa-trophy" /> Достижения
                  </h4>
                  <div className="badges-grid">
                    {profile.achievements.map(a => (
                      <div key={a.id} className="badge-card" style={{ borderLeftColor: a.badge.color }}>
                        <div className="badge-icon" style={{ background: `${a.badge.color}20` }}>
                          <span>{a.badge.icon}</span>
                        </div>
                        <div className="badge-info">
                          <h4>{a.badge.name}</h4>
                          <p>{a.badge.description}</p>
                          <div className="badge-meta">
                            <span className="badge-date">
                              <i className="fas fa-calendar" /> {new Date(a.earned_at).toLocaleDateString('ru-RU')}
                            </span>
                            {a.reason && <span className="badge-reason">{a.reason}</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="profile-layout">
            <div className="profile-content">
              <div className="profile-tabs">
                <ul className="nav-tabs">
                  {tabs.map(tab => (
                    <li key={tab.key} className="nav-item">
                      <a href={`#${tab.key}`}
                        className={`nav-link tab ${activeTab === tab.key ? 'active' : ''}`}
                        onClick={e => { e.preventDefault(); setActiveTab(tab.key) }}>
                        <i className={`fas ${tab.icon}`} /> <span>{tab.label}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="tab-content">
                <div id="published" className={`content-tab ${activeTab === 'published' ? 'active' : ''}`}>
                  <div className="posts-grid">
                    {postsLoading && <div className="empty-state"><i className="fas fa-spinner fa-spin" /><p>Загрузка...</p></div>}
                    {!postsLoading && posts.length === 0 && (
                      <div className="empty-state">
                        <i className="fas fa-inbox" />
                        <p>Опубликованных статей пока нет</p>
                        {isOwn && (
                          <Link to="/add-post/"
                            style={{
                              display: 'inline-flex', alignItems: 'center', gap: 6,
                              fontSize: '0.9rem', fontWeight: 500,
                              color: 'var(--primary)', textDecoration: 'none',
                              transition: 'opacity 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.opacity = '0.7'}
                            onMouseLeave={e => e.currentTarget.style.opacity = '1'}>
                            <i className="fas fa-plus" style={{ fontSize: '0.8rem' }} /> Создать статью
                          </Link>
                        )}
                      </div>
                    )}
                    {posts.map(post => (
                      <PostCard key={post.id} post={post}
                        badge={isOwn && <div style={{ marginBottom: 8 }}><span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '1px 7px', border: '1px solid rgba(44, 107, 79, 0.4)', borderRadius: 2, background: 'transparent', color: 'var(--success)', fontFamily: 'var(--font-mono)', fontSize: '9px', fontWeight: 500 }}><i className="fas fa-check-circle" /> Опубликовано</span></div>}
                        extra={isOwn && <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                          <Link to={`/edit/${post.slug}/`} className="btn btn-sm btn-primary">
                            <i className="fas fa-edit" /> Редактировать
                          </Link>
                          <button onClick={() => handleDelete(post)} className="btn btn-sm btn-outline-danger">
                            <i className="fas fa-trash" /> Удалить
                          </button>
                        </div>}
                      />
                    ))}
                  </div>
                </div>

                {isOwn && (
                  <div id="drafts" className={`content-tab ${activeTab === 'drafts' ? 'active' : ''}`}>
                    <div className="posts-grid">
                      {drafts.length === 0 && (
                        <div className="empty-state">
                          <i className="fas fa-file" />
                          <p>Черновиков нет</p>
                        </div>
                      )}
                      {drafts.map(post => (
                        <PostCard key={post.id} post={post} noReadMore
                          badge={<div style={{ marginBottom: 8 }}><span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 10px', borderRadius: 20, background: 'rgba(245,158,11,0.1)', color: '#f59e0b', fontSize: '0.78rem', fontWeight: 600 }}><i className="fas fa-file" /> Черновик</span></div>}
                          extra={<div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                            <Link to={`/edit/${post.slug}/`} className="btn btn-sm btn-primary">
                              <i className="fas fa-edit" /> Редактировать
                            </Link>
                            <button onClick={() => handleDelete(post)} className="btn btn-sm btn-outline-danger"
                              style={{ background: 'var(--danger, #ef4444)', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: 8, fontSize: '0.8rem', cursor: 'pointer' }}>
                              <i className="fas fa-trash" /> Удалить
                            </button>
                          </div>}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {isOwn && (
                  <div id="favorites" className={`content-tab ${activeTab === 'favorites' ? 'active' : ''}`}>
                    <div className="posts-grid">
                      {favorites.length === 0 && (
                        <div className="empty-state">
                          <i className="fas fa-heart" />
                          <p>Избранных статей пока нет</p>
                          <Link to="/"
                            style={{
                              display: 'inline-flex', alignItems: 'center', gap: 6,
                              fontSize: '0.9rem', fontWeight: 500,
                              color: 'var(--primary)', textDecoration: 'none',
                              transition: 'opacity 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.opacity = '0.7'}
                            onMouseLeave={e => e.currentTarget.style.opacity = '1'}>
                            <i className="fas fa-search" style={{ fontSize: '0.8rem' }} /> Найти статьи
                          </Link>
                        </div>
                      )}
                      {favorites.map(post => (
                        <PostCard key={post.id} post={post}
                          badge={<div style={{ marginBottom: 8 }}><span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 10px', borderRadius: 20, background: 'rgba(239,68,68,0.1)', color: '#ef4444', fontSize: '0.78rem', fontWeight: 600 }}><i className="fas fa-heart" /> В избранном</span></div>}
                        />
                      ))}
                    </div>
                  </div>
                )}

                <div id="reviews" className={`content-tab ${activeTab === 'reviews' ? 'active' : ''}`}>
                  {reviewsLoading ? (
                    <div className="empty-state">
                      <i className="fas fa-spinner fa-spin" />
                      <p>Загрузка разборов...</p>
                    </div>
                  ) : (
                    <>
                      <section className="review-profile-section" aria-labelledby="reviews-given-title">
                        <h3 className="review-profile-title" id="reviews-given-title">
                          <i className="fas fa-code" /> Проведённые разборы
                          <span className="review-profile-count">{reviews.given.length}</span>
                        </h3>
                        <div className="posts-grid">
                          {reviews.given.length === 0 && (
                            <div className="empty-state">
                              <i className="fas fa-code" />
                              <p>Проведённых разборов пока нет</p>
                            </div>
                          )}
                          {reviews.given.map(post => (
                            <PostCard key={post.id} post={post} />
                          ))}
                        </div>
                      </section>

                      <section className="review-profile-section" aria-labelledby="reviews-requested-title">
                        <h3 className="review-profile-title" id="reviews-requested-title">
                          <i className="fas fa-paper-plane" /> Запрошенные разборы
                          <span className="review-profile-count">{reviews.requested.length}</span>
                        </h3>
                        <div className="posts-grid">
                          {reviews.requested.length === 0 && (
                            <div className="empty-state">
                              <i className="fas fa-code" />
                              <p>Запрошенных разборов пока нет</p>
                              {isOwn && (
                                <Link to="/add-post/"
                                  style={{
                                    display: 'inline-flex', alignItems: 'center', gap: 6,
                                    fontSize: '0.9rem', fontWeight: 500,
                                    color: 'var(--primary)', textDecoration: 'none',
                                    transition: 'opacity 0.2s',
                                  }}>
                                  <i className="fas fa-plus" style={{ fontSize: '0.8rem' }} /> Создать разбор
                                </Link>
                              )}
                            </div>
                          )}
                          {reviews.requested.map(post => (
                            <PostCard key={post.id} post={post} />
                          ))}
                        </div>
                      </section>
                    </>
                  )}
                </div>
              </div>
            </div>

            <aside className="sidebar profile-sidebar">
              <div className="modern-sidebar">
                <div className="sidebar-widget">
                  <h4 className="widget-title"><i className="fas fa-info-circle" /> О пользователе</h4>
                  <div className="profile-info-list">
                    <div className="info-item">
                      <span className="info-icon"><i className="fas fa-envelope" /></span>
                      <div className="info-content">
                        <span className="info-label">Email</span>
                        <span className="info-value">{profile.email || '—'}</span>
                      </div>
                    </div>
                    <div className="info-item">
                      <span className="info-icon"><i className="fas fa-calendar-check" /></span>
                      <div className="info-content">
                        <span className="info-label">На сайте с</span>
                        <span className="info-value">
                          {profile.date_joined
                            ? new Date(profile.date_joined).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
                            : '—'}
                        </span>
                      </div>
                    </div>
                    <div className="info-item">
                      <span className="info-icon"><i className="fas fa-shield-alt" /></span>
                      <div className="info-content">
                        <span className="info-label">Роль</span>
                        <span className="info-value">
                          {profile.is_superuser ? 'Администратор' : profile.is_staff ? 'Модератор' : 'Пользователь'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="sidebar-widget">
                  <h4 className="widget-title"><i className="fas fa-chart-bar" /> Статистика</h4>
                  <div className="stats-grid-compact">
                    <div className="stat-block">
                      <div className="stat-block-value">{userStats?.posts_count ?? profile.published_count ?? '—'}</div>
                      <div className="stat-block-label">Публикации</div>
                    </div>
                    <div className="stat-block">
                      <div className="stat-block-value">{userStats?.comments_count ?? '—'}</div>
                      <div className="stat-block-label">Комментарии</div>
                    </div>
                    <div className="stat-block">
                      <div className="stat-block-value">{userStats?.likes_received ?? '—'}</div>
                      <div className="stat-block-label">Лайков</div>
                    </div>
                  </div>
                  <div className="review-stats-row">
                    <div className="stat-block">
                      <div className="stat-block-value">{userStats?.reviews_given ?? '—'}</div>
                      <div className="stat-block-label">Разборов провёл</div>
                    </div>
                    <div className="stat-block">
                      <div className="stat-block-value">{userStats?.reviews_received ?? '—'}</div>
                      <div className="stat-block-label">Разборов получил</div>
                    </div>
                  </div>
                </div>

                {profile.current_level && (
                  <div className="sidebar-widget">
                    <h4 className="widget-title"><i className="fas fa-trophy" /> Прогресс уровня</h4>
                    <div className="level-progress-widget">
                      <div className="level-info-row">
                        <span className="level-current">
                          <span className="level-icon">{profile.current_level.icon}</span>
                          <span>{profile.current_level.name}</span>
                        </span>
                        {profile.next_level && (
                          <span className="level-next">
                            <span>{profile.next_level.icon}</span>
                            <span>{profile.next_level.name}</span>
                          </span>
                        )}
                      </div>
                      <div className="level-progress-bar-track">
                        <div className="level-progress-bar-fill"
                          style={{ width: `${profile.level_progress || 0}%`, background: profile.current_level.color }}
                        />
                      </div>
                      <div className="level-reputation-row">
                        <span>Репутация: <strong>{profile.reputation || 0}</strong></span>
                        {profile.next_level && (
                          <span className="level-next-rep">
                            до {profile.next_level.name}: <strong>{profile.next_level.min_reputation - profile.reputation}</strong>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="sidebar-widget">
                  <h4 className="widget-title"><i className="fas fa-clock" /> Недавние статьи</h4>
                  <div className="recent-posts">
                    {recentUserPosts.length === 0 && (
                      <p className="no-posts">Статей пока нет</p>
                    )}
                    {recentUserPosts.map(post => (
                      <Link key={post.id} to={`/post/${post.slug}/`} className="text-decoration-none recent-post-card">
                        {post.photo && (
                          <div className="recent-post-img">
                            <img src={post.photo} alt={post.title} />
                          </div>
                        )}
                        <div className="recent-post-content">
                          <h5 className="recent-post-title">
                            {post.title?.length > 45 ? post.title.slice(0, 45) + '...' : post.title}
                          </h5>
                          <div className="recent-post-meta">
                            <span className="post-time" title={post.time_update}>
                              <i className="fas fa-clock" /> {new Date(post.time_update).toLocaleDateString('ru-RU')}
                            </span>
                          </div>
                          <div className="recent-post-stats">
                            <span className="stat"><i className="fas fa-eye" /> {post.views}</span>
                            <span className="stat"><i className="fas fa-heart" /> {post.likes_count || 0}</span>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>

    </main>
  )
}

export default ProfilePage
