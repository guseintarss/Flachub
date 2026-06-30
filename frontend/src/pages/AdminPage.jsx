import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar/Sidebar'
import UserAvatar from '../components/UserAvatar'
import '../styles/admin.css'

function AdminStats({ stats }) {
  const cards = [
    { label: 'Пользователей', value: stats.total_users, icon: 'fa-users', color: '#3b82f6' },
    { label: 'Публикаций', value: stats.total_posts, icon: 'fa-file-alt', color: '#10b981' },
    { label: 'Опубликовано', value: stats.published_posts, icon: 'fa-check-circle', color: '#22c55e' },
    { label: 'Комментариев', value: stats.total_comments, icon: 'fa-comments', color: '#f59e0b' },
    { label: 'Администраторов', value: stats.total_admins, icon: 'fa-crown', color: '#ef4444' },
    { label: 'Модераторов', value: stats.total_moderators, icon: 'fa-shield-alt', color: '#8b5cf6' },
  ]

  return (
    <div className="admin-stats-grid">
      {cards.map(c => (
        <div key={c.label} className="admin-stat-card">
          <div className="admin-stat-icon" style={{ background: `${c.color}15`, color: c.color }}>
            <i className={`fas ${c.icon}`}></i>
          </div>
          <div className="admin-stat-info">
            <span className="admin-stat-value">{c.value}</span>
            <span className="admin-stat-label">{c.label}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

function AdminUsers({ onError }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [role, setRole] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [updating, setUpdating] = useState(null)

  function fetchUsers() {
    setLoading(true)
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (role) params.set('role', role)
    params.set('page', page)

    fetch(`/api/mobile/admin/users/?${params}`)
      .then(r => {
        if (!r.ok) throw new Error('Ошибка загрузки')
        return r.json()
      })
      .then(d => {
        setUsers(d.users || [])
        setTotalPages(d.total_pages || 0)
      })
      .catch(e => onError?.(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchUsers() }, [page, role])

  function handleSearch(e) {
    e.preventDefault()
    setPage(1)
    fetchUsers()
  }

  async function changeRole(userId, newRole) {
    setUpdating(userId)
    try {
      const r = await fetch(`/api/mobile/admin/users/${userId}/role/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '' },
        body: JSON.stringify({ role: newRole }),
      })
      const d = await r.json()
      if (!d.success) throw new Error(d.error || 'Ошибка')
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_staff: newRole !== 'user', is_superuser: newRole === 'admin' } : u))
    } catch (e) {
      onError?.(e.message)
    }
    setUpdating(null)
  }

  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2><i className="fas fa-user-cog"></i> Управление пользователями</h2>
      </div>

      <form className="admin-users-filters" onSubmit={handleSearch}>
        <div className="admin-search">
          <i className="fas fa-search"></i>
          <input type="text" placeholder="Поиск по имени, email, нику..." value={search}
            onChange={e => setSearch(e.target.value)} />
        </div>
        <select value={role} onChange={e => { setRole(e.target.value); setPage(1) }}>
          <option value="">Все роли</option>
          <option value="admin">Администраторы</option>
          <option value="moderator">Модераторы</option>
          <option value="user">Пользователи</option>
        </select>
        <button type="submit" className="btn btn-primary">Найти</button>
      </form>

      {loading ? (
        <div className="admin-loading">Загрузка...</div>
      ) : (
        <div className="admin-users-table-wrap">
          <table className="admin-users-table">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Репутация</th>
                <th>Дата регистрации</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>
                    <div className="admin-user-cell">
                      <UserAvatar user={u} size={32} />
                      <div>
                        <span className="admin-user-name">{u.first_name || u.username}</span>
                        <span className="admin-user-username">@{u.username}</span>
                      </div>
                    </div>
                  </td>
                  <td className="admin-cell-muted">{u.email || '—'}</td>
                  <td>
                    <span className={`admin-role-badge ${u.is_superuser ? 'role-admin' : u.is_staff ? 'role-moderator' : 'role-user'}`}>
                      {u.is_superuser ? 'Администратор' : u.is_staff ? 'Модератор' : 'Пользователь'}
                    </span>
                  </td>
                  <td className="admin-cell-muted">{u.reputation || 0}</td>
                  <td className="admin-cell-muted">
                    {u.date_joined ? new Date(u.date_joined).toLocaleDateString('ru-RU') : '—'}
                  </td>
                  <td>
                    {u.id !== undefined && (
                      <div className="admin-role-actions">
                        {u.is_superuser ? (
                          <span className="admin-role-current">Высшая роль</span>
                        ) : (
                          <>
                            {u.is_staff ? (
                              <button className="btn btn-sm btn-secondary" disabled={updating === u.id}
                                onClick={() => changeRole(u.id, 'user')}>
                                {updating === u.id ? '...' : 'Снять модератора'}
                              </button>
                            ) : (
                              <button className="btn btn-sm btn-primary" disabled={updating === u.id}
                                onClick={() => changeRole(u.id, 'moderator')}>
                                {updating === u.id ? '...' : 'Назначить модератором'}
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 20 }}>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
            <button key={p} className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setPage(p)} disabled={p === page}>{p}</button>
          ))}
        </div>
      )}
    </div>
  )
}

function AdminPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    if (!user.is_staff) { navigate('/', { replace: true }); return }
  }, [user, navigate])

  useEffect(() => {
    if (!user?.is_staff) return
    fetch('/api/mobile/admin/stats/')
      .then(r => r.json())
      .then(d => setStats(d))
      .catch(() => setError('Не удалось загрузить статистику'))
  }, [user])

  if (!user || !user.is_staff) return null

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          <div className="admin-layout">
            <div className="admin-sidebar">
              <h2 className="admin-sidebar-title"><i className="fas fa-chart-line"></i> Панель управления</h2>
              <nav className="admin-nav">
                <button className={`admin-nav-link${tab === 'overview' ? ' active' : ''}`} onClick={() => setTab('overview')}>
                  <i className="fas fa-tachometer-alt"></i> Обзор
                </button>
                <button className={`admin-nav-link${tab === 'users' ? ' active' : ''}`} onClick={() => setTab('users')}>
                  <i className="fas fa-users"></i> Пользователи
                </button>
                {user.is_superuser && (
                  <a href="/admin/" className="admin-nav-link" target="_blank" rel="noopener noreferrer">
                    <i className="fas fa-database"></i> Django Admin
                  </a>
                )}
              </nav>
            </div>

            <div className="admin-main">
              {error && (
                <div className="admin-error">{error}</div>
              )}

              {tab === 'overview' && (
                <div className="admin-section">
                  <div className="admin-section-header">
                    <h2><i className="fas fa-tachometer-alt"></i> Обзор сайта</h2>
                  </div>
                  {stats ? <AdminStats stats={stats} /> : <div className="admin-loading">Загрузка статистики...</div>}
                </div>
              )}

              {tab === 'users' && <AdminUsers onError={setError} />}
            </div>
          </div>
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export default AdminPage