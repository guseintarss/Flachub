import { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { toggleSubscribe } from '../api'
import PostCard from '../components/Feed/PostCard'
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
      } catch {}
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
      } catch {}
    }

    async function loadFavorites() {
      if (!isOwn) return
      try {
        const res = await fetch(`/api/mobile/users/${profile.id}/favorites/`)
        if (res.ok) {
          const data = await res.json()
          setFavorites(data.results || data || [])
        }
      } catch {}
    }

    async function loadStats() {
      try {
        const res = await fetch(`/api/mobile/users/${profile.id}/stats/`)
        if (res.ok) setUserStats(await res.json())
      } catch {}
    }

    async function loadRecentPosts() {
      try {
        const res = await fetch(`/api/mobile/posts/?author=${profile.id}&page_size=5`)
        if (res.ok) {
          const data = await res.json()
          setRecentUserPosts(data.results || [])
        }
      } catch {}
    }

    loadPosts()
    loadDrafts()
    loadFavorites()
    loadStats()
    loadRecentPosts()
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
    } catch {}
    setSubscribing(false)
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
    : { background: `linear-gradient(135deg, ${profile.banner_gradient_start || '#0c6acf'} 0%, ${profile.banner_gradient_end || '#764ba2'} 100%)` }

  const tabs = [
    { key: 'published', label: 'Опубликованные', icon: 'fa-check-circle' },
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
                  {profile.avatar ? (
                    <img className="author-avatar-lg" src={profile.avatar} alt={profile.username} />
                  ) : (
                    <div className="author-avatar-lg author-avatar-placeholder"
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'var(--primary)', color: '#fff', fontWeight: 700, fontSize: 36,
                      }}>
                      {profile.username?.[0]?.toUpperCase() || '?'}
                    </div>
                  )}
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
                  <div className="author-hero-subscribe">
                    <button id="subscribe-btn"
                      className={`btn ${profile.is_subscribed ? 'btn-secondary' : 'btn-primary'}`}
                      onClick={handleSubscribe}
                      disabled={subscribing}>
                      {profile.is_subscribed ? 'Отписаться' : 'Подписаться'}
                    </button>
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

              {isOwn && (
                <div className="author-actions">
                  <Link className="btn btn-primary" to="/profile/edit/">
                    <i className="fas fa-cog" />
                  </Link>
                  <Link className="btn btn-outline-primary" to="/reputation/history/">
                    <i className="fas fa-history" />
                  </Link>
                </div>
              )}

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
                          <Link to="/add-post/" className="btn btn-primary">
                            <i className="fas fa-plus" /> Создать статью
                          </Link>
                        )}
                      </div>
                    )}
                    {posts.map(post => (
                      <PostCard key={post.id} post={post}
                        badge={isOwn && <div style={{ marginBottom: 8 }}><span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 10px', borderRadius: 20, background: 'rgba(16,185,129,0.1)', color: '#10b981', fontSize: '0.78rem', fontWeight: 600 }}><i className="fas fa-check-circle" /> Опубликовано</span></div>}
                        extra={isOwn && <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                          <Link to={`/edit/${post.slug}/`} className="btn btn-sm btn-primary">
                            <i className="fas fa-edit" /> Редактировать
                          </Link>
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
                          <Link to="/" className="btn btn-outline-secondary">
                            <i className="fas fa-search" /> Найти статьи
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

      <style>{`
        .author-profile-page { max-width: 100%; margin: 0 auto; }

        .profile-layout {
          display: flex; gap: 28px; align-items: flex-start;
        }
        .profile-content {
          flex: 1; min-width: 0;
        }
        .profile-sidebar {
          width: 320px; flex-shrink: 0;
        }
        .profile-sidebar .modern-sidebar { position: sticky; top: 20px; }

        .profile-info-list { display: flex; flex-direction: column; gap: 14px; }
        .info-item { display: flex; gap: 12px; align-items: flex-start; }
        .info-icon {
          width: 36px; height: 36px; border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          background: linear-gradient(135deg, rgba(12,106,207,0.1), rgba(118,75,162,0.08));
          color: var(--primary); flex-shrink: 0; font-size: 0.85rem;
        }
        .info-content { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
        .info-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; }
        .info-value { font-size: 0.9rem; color: var(--text); font-weight: 500; word-break: break-word; }

        .stats-grid-compact { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .stat-block {
          text-align: center; padding: 12px 6px;
          background: linear-gradient(135deg, rgba(12,106,207,0.05), rgba(118,75,162,0.03));
          border: 1px solid var(--border); border-radius: 12px;
        }
        .stat-block-value { font-size: 1.3rem; font-weight: 800; color: var(--text); }
        .stat-block-label { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; margin-top: 2px; }

        .level-progress-widget { display: flex; flex-direction: column; gap: 10px; }
        .level-info-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
        .level-current, .level-next { display: flex; align-items: center; gap: 4px; font-weight: 600; color: var(--text); }
        .level-next { color: var(--muted); font-size: 0.8rem; }
        .level-icon { font-size: 1.1rem; }
        .level-progress-bar-track {
          height: 8px; background: var(--border); border-radius: 10px; overflow: hidden;
        }
        .level-progress-bar-fill {
          height: 100%; border-radius: 10px; transition: width 0.5s ease;
        }
        .level-reputation-row {
          display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--muted); flex-wrap: wrap; gap: 4px;
        }
        .level-next-rep { color: var(--primary); }

        html.dark-mode .info-icon { background: linear-gradient(135deg, rgba(41,156,245,0.15), rgba(118,75,162,0.1)); }
        html.dark-mode .stat-block { background: var(--dark-bg); border-color: var(--dark-border); }
        html.dark-mode .level-progress-bar-track { background: var(--dark-border); }

        @media (max-width: 1024px) {
          .profile-layout { flex-direction: column; }
          .profile-sidebar { width: 100%; }
        }

        .author-profile-page { max-width: 960px; margin: 0 auto; }

        .author-hero {
          position: relative; border-radius: 20px; overflow: hidden;
          margin-bottom: 24px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        }
        .author-hero-bg { height: 200px; position: relative; }
        .author-hero-bg::after {
          content: ''; position: absolute; inset: 0;
          background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
          opacity: 0.5;
        }
        .author-hero-content {
          position: relative; padding: 0 32px 32px; background: var(--surface);
        }
        .author-hero-top {
          display: flex; align-items: flex-end; gap: 24px;
          margin-top: -55px; margin-bottom: 18px;
        }
        .author-avatar-lg {
          width: 120px; height: 120px; border-radius: 50%; object-fit: cover;
          border: 4px solid var(--surface); background: var(--bg);
          box-shadow: 0 4px 20px rgba(0,0,0,0.15); flex-shrink: 0;
        }
        .author-avatar-placeholder { border-radius: 50%; }
        .author-hero-info { flex: 1; min-width: 0; padding-bottom: 6px; margin-top: 10px; }
        .author-hero-name-row {
          display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px;
        }
        .author-hero-username {
          font-size: 1.75rem; font-weight: 800; color: var(--text); margin: 0;
        }
        .author-hero-fullname { color: var(--muted); font-size: 1rem; margin: 0; }
        .author-hero-bio {
          color: var(--text); font-size: 0.95rem; line-height: 1.65;
          margin: 0 0 24px 0; max-width: 600px;
        }
        .author-hero-subscribe { flex-shrink: 0; padding-bottom: 6px; }
        #subscribe-btn {
          padding: 10px 24px; font-size: 0.9rem; font-weight: 600;
          border-radius: 12px; transition: all 0.25s ease; white-space: nowrap;
        }

        .author-stats-row {
          display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 24px;
        }
        .author-stat-card {
          display: flex; flex-direction: column; align-items: center; gap: 6px;
          padding: 18px 12px; background: linear-gradient(135deg, rgba(12,106,207,0.08) 0%, rgba(118,75,162,0.06) 100%);
          border: 1px solid var(--border); border-radius: 16px; transition: all 0.25s ease;
        }
        .author-stat-card:hover {
          transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); border-color: var(--primary);
        }
        .author-stat-icon {
          width: 40px; height: 40px; border-radius: 12px;
          display: flex; align-items: center; justify-content: center;
          font-size: 1rem; color: #fff;
        }
        .author-stat-card:nth-child(1) .author-stat-icon { background: linear-gradient(135deg, #0c6acf, #667eea); }
        .author-stat-card:nth-child(2) .author-stat-icon { background: linear-gradient(135deg, #10b981, #34d399); }
        .author-stat-card:nth-child(3) .author-stat-icon { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
        .author-stat-value { font-size: 1.6rem; font-weight: 800; color: var(--text); }
        .author-stat-label { font-size: 0.75rem; color: var(--muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }

        .author-actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .author-actions .btn {
          padding: 10px 20px; font-size: 0.85rem; font-weight: 600; border-radius: 10px;
          transition: all 0.25s ease; display: inline-flex; align-items: center; gap: 8px; text-decoration: none;
        }
        .author-actions .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(12,106,207,0.25); }

        .author-achievements { margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--border); }
        .achievements-title {
          font-size: 1.15rem; font-weight: 700; color: var(--text);
          margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
        }
        .achievements-title i { color: #f59e0b; font-size: 1.3rem; }
        .badges-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
        .badge-card {
          display: flex; gap: 14px; padding: 14px; background: var(--bg);
          border-radius: 12px; border-left: 3px solid var(--primary);
        }
        .badge-icon {
          width: 46px; height: 46px; display: flex; align-items: center; justify-content: center;
          border-radius: 12px; font-size: 1.6rem; flex-shrink: 0;
        }
        .badge-info h4 { font-size: 0.95rem; font-weight: 600; color: var(--text); margin: 0 0 4px 0; }
        .badge-info p { font-size: 0.8rem; color: var(--muted); margin: 0 0 6px 0; }
        .badge-meta { display: flex; gap: 10px; font-size: 0.75rem; color: var(--muted); flex-wrap: wrap; }

        .profile-tabs {
          background: var(--surface); border-radius: var(--radius);
          padding: 0; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);
          overflow: hidden; position: relative;
        }
        .nav-tabs {
          display: flex; gap: 5px; list-style: none; padding: 0 20px; margin: 0;
          border-bottom: 2px solid var(--border); overflow-x: auto; overflow-y: hidden;
          -webkit-overflow-scrolling: touch; scrollbar-width: thin;
        }
        .nav-item { margin: 0; flex-shrink: 0; }
        .nav-link {
          display: flex; align-items: center; gap: 8px; padding: 15px 20px;
          color: var(--text); text-decoration: none; font-weight: 500;
          border-bottom: 3px solid transparent; transition: all 0.3s;
          margin-bottom: -2px; white-space: nowrap; cursor: pointer;
        }
        .nav-link:hover { color: var(--primary); }
        .nav-link.active { color: var(--primary); border-bottom-color: var(--primary); }

        .tab-content { display: block; }
        .content-tab { display: none; }
        .content-tab.active { display: block; }

        .posts-grid { display: grid; gap: 25px; }
        .badge {
          padding: 4px 12px; background: var(--primary); color: white;
          border-radius: 20px; font-size: 0.8rem; font-weight: 500;
        }
        .post-time { color: var(--muted); font-size: 0.85rem; display: flex; align-items: center; gap: 5px; }

        .empty-state {
          grid-column: 1 / -1; text-align: center;
          padding: 60px 20px; background: var(--surface); border-radius: var(--radius);
        }
        .empty-state i { font-size: 4rem; color: var(--muted); margin-bottom: 20px; }
        .empty-state p { color: var(--muted); margin-bottom: 20px; font-size: 1.1rem; }
        .empty-state .btn { padding: 10px 24px; font-size: 0.95rem; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; }

        html.dark-mode .author-hero-content { background: var(--dark-surface); }
        html.dark-mode .author-avatar-lg { border-color: var(--dark-surface); background: var(--dark-bg); }
        html.dark-mode .author-stat-card { background: var(--dark-bg); border-color: var(--dark-border); }
        html.dark-mode .badge-card { background: var(--dark-bg); }

        @media (max-width: 768px) {
          .author-hero { border-radius: 0; margin-bottom: 0; }
          .author-hero-bg { height: 140px; }
          .author-hero-content { padding: 0 16px 20px; }
          .author-hero-top { margin-top: -44px; gap: 14px; }
          .author-avatar-lg { width: 80px; height: 80px; }
          .author-hero-username { font-size: 1.3rem; }
          .author-stats-row { gap: 8px; }
          .author-stat-card { padding: 12px 6px; }
          .author-stat-icon { width: 30px; height: 30px; }
          .author-stat-value { font-size: 1.2rem; }
          .author-stat-label { font-size: 0.65rem; }
          .badges-grid { grid-template-columns: 1fr; }
          .posts-grid { grid-template-columns: 1fr; }
          .empty-state { padding: 40px 16px; }
          .empty-state i { font-size: 3rem; }
          .nav-link { padding: 12px 15px; font-size: 0.85rem; border-radius: 8px; margin-bottom: 0; border-bottom: none; }
          .nav-link.active { background: var(--primary); color: white; border-bottom: none; }
        }
      `}</style>
    </main>
  )
}

export default ProfilePage
