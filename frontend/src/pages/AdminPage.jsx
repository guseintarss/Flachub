import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import UserAvatar from '../components/UserAvatar'
import '../styles/admin.css'

function BarChart({ data, label, color }) {
  const max = Math.max(...data.map(d => d.count), 1)
  return (
    <div className="admin-chart">
      <h4 className="admin-chart-title">{label}</h4>
      <div className="admin-chart-bars">
        {data.map((d, i) => (
          <div key={i} className="admin-chart-col" title={`${d.date}: ${d.count}`}>
            <div className="admin-chart-track">
              <div className="admin-chart-bar" style={{ height: `${(d.count / max) * 100}%`, background: color }} />
            </div>
            <span className="admin-chart-label">{d.date.slice(5)}</span>
          </div>
        ))}
        <div className="admin-chart-zero" />
      </div>
    </div>
  )
}

function AdminCharts({ stats }) {
  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2><i className="fas fa-chart-bar"></i> Аналитика за 14 дней</h2>
      </div>
      <div className="admin-charts-grid">
        <BarChart data={stats.daily_registrations} label="Регистрации" color="#3b82f6" />
        <BarChart data={stats.daily_posts} label="Публикации" color="#10b981" />
        <BarChart data={stats.daily_comments} label="Комментарии" color="#f59e0b" />
      </div>
    </div>
  )
}

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

const ALL_COLUMNS = [
  { key: 'user', label: 'Пользователь' },
  { key: 'email', label: 'Email' },
  { key: 'role', label: 'Роль' },
  { key: 'reputation', label: 'Репутация' },
  { key: 'status', label: 'Статус' },
  { key: 'date_joined', label: 'Дата регистрации' },
  { key: 'actions', label: 'Действия' },
]

function AdminUsers({ onError, currentUser }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [role, setRole] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [updating, setUpdating] = useState(null)
  const [visibleColumns, setVisibleColumns] = useState(ALL_COLUMNS.map(c => c.key))
  const [colsOpen, setColsOpen] = useState(false)
  const colsRef = useRef()

  useEffect(() => {
    function handleClick(e) {
      if (colsRef.current && !colsRef.current.contains(e.target)) setColsOpen(false)
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

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

  async function toggleBan(userId) {
    setUpdating(userId)
    try {
      const r = await fetch(`/api/mobile/admin/users/${userId}/ban/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '' },
      })
      const d = await r.json()
      if (!d.success) throw new Error(d.error || 'Ошибка')
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: d.is_active } : u))
    } catch (e) {
      onError?.(e.message)
    }
    setUpdating(null)
  }

  function toggleColumn(key) {
    setVisibleColumns(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    )
  }

  const visible = new Set(visibleColumns)

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
        <div className="admin-cols-toggle" ref={colsRef}>
          <button type="button" className="btn btn-secondary" onClick={() => setColsOpen(o => !o)}>
            <i className="fas fa-table"></i> Колонки
          </button>
          {colsOpen && (
            <div className="admin-cols-dropdown">
              {ALL_COLUMNS.map(c => (
                <label key={c.key} className="admin-cols-option">
                  <input type="checkbox" checked={visibleColumns.includes(c.key)}
                    onChange={() => toggleColumn(c.key)} />
                  {c.label}
                </label>
              ))}
            </div>
          )}
        </div>
      </form>

      {loading ? (
        <div className="admin-loading">Загрузка...</div>
      ) : (
        <div className="admin-users-table-wrap">
          <table className="admin-users-table">
            <thead>
              <tr>
                {ALL_COLUMNS.filter(c => visible.has(c.key)).map(c => (
                  <th key={c.key}>{c.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  {visible.has('user') && (
                    <td>
                      <div className="admin-user-cell">
                        <UserAvatar user={u} size={32} />
                        <div>
                          <span className="admin-user-name">{u.first_name || u.username}</span>
                          <span className="admin-user-username">@{u.username}</span>
                        </div>
                      </div>
                    </td>
                  )}
                  {visible.has('email') && (
                    <td className="admin-cell-muted">{u.email || '—'}</td>
                  )}
                  {visible.has('role') && (
                    <td>
                      <span className={`admin-role-badge ${u.is_superuser ? 'role-admin' : u.is_staff ? 'role-moderator' : 'role-user'}`}>
                        {u.is_superuser ? 'Администратор' : u.is_staff ? 'Модератор' : 'Пользователь'}
                      </span>
                    </td>
                  )}
                  {visible.has('reputation') && (
                    <td className="admin-cell-muted">{u.reputation || 0}</td>
                  )}
                  {visible.has('status') && (
                    <td>
                      {u.is_active === false ? (
                        <span className="admin-status-badge status-banned">Заблокирован</span>
                      ) : (
                        <span className="admin-status-badge status-active">Активен</span>
                      )}
                    </td>
                  )}
                  {visible.has('date_joined') && (
                    <td className="admin-cell-muted">
                      {u.date_joined ? new Date(u.date_joined).toLocaleDateString('ru-RU') : '—'}
                    </td>
                  )}
                  {visible.has('actions') && (
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
                              {currentUser?.is_superuser && (
                                <button className={`btn btn-sm ${u.is_active === false ? 'btn-success' : 'btn-danger'}`}
                                  disabled={updating === u.id}
                                  onClick={() => toggleBan(u.id)}>
                                  {updating === u.id ? '...' : u.is_active === false ? 'Разблокировать' : 'Заблокировать'}
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      )}
                    </td>
                  )}
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
    <main className="page admin-page">
      <div className="pg-container layout">
        <div className="content">
          <div className="admin-layout">
            <div className="admin-header">
              <h2 className="admin-header-title"><i className="fas fa-chart-line"></i> Панель управления</h2>
              <nav className="admin-tabs">
                <button className={`admin-tab${tab === 'overview' ? ' active' : ''}`} onClick={() => setTab('overview')}>
                  <i className="fas fa-tachometer-alt"></i> Обзор
                </button>
                <button className={`admin-tab${tab === 'analytics' ? ' active' : ''}`} onClick={() => setTab('analytics')}>
                  <i className="fas fa-chart-bar"></i> Аналитика
                </button>
                <button className={`admin-tab${tab === 'users' ? ' active' : ''}`} onClick={() => setTab('users')}>
                  <i className="fas fa-users"></i> Пользователи
                </button>
                {user.is_superuser && (
                  <a href="/admin/" className="admin-tab" target="_blank" rel="noopener noreferrer">
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

              {tab === 'analytics' && (
                stats ? <AdminCharts stats={stats} /> : <div className="admin-loading">Загрузка аналитики...</div>
              )}

              {tab === 'users' && <AdminUsers onError={setError} currentUser={user} />}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default AdminPage
