import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const UserArea = () => {
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  const notifRef = useRef()
  const [notifOpen, setNotifOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    if (!user) return
    fetch('/api/mobile/notifications/unread_count/')
      .then(r => r.json())
      .then(d => setUnreadCount(d.unread_count || 0))
      .catch(() => {})
  }, [user])

  function loadNotifications() {
    fetch('/api/mobile/notifications/')
      .then(r => r.json())
      .then(data => {
        const items = data.results || data || []
        setNotifications(items)
        const unread = items.filter(n => !n.is_read).length
        setUnreadCount(unread)
      })
      .catch(() => {})
  }

  useEffect(() => {
    if (!notifOpen) return
    function handleKey(e) {
      if (e.key === 'Escape') setNotifOpen(false)
    }
    function handleClick(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false)
    }
    document.addEventListener('keydown', handleKey)
    document.addEventListener('click', handleClick)
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.removeEventListener('click', handleClick)
    }
  }, [notifOpen])

  function toggleNotif() {
    const willOpen = !notifOpen
    setNotifOpen(willOpen)
    if (willOpen) loadNotifications()
  }

  function markAllRead() {
    fetch('/api/mobile/notifications/mark_all_read/', { method: 'POST' })
      .then(() => { setUnreadCount(0); loadNotifications() })
      .catch(() => {})
  }

  return (
    <div className="user-area">
      {user && (
        <Link className="addbutton" to="/add-post/" title="Добавить пост">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" />
          </svg>
        </Link>
      )}

      <Link id="search" className="search" to="/search/" title="Поиск">
        <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0,0,256,256" className="header-icon">
          <g fill="currentColor" fillRule="nonzero" stroke="none" strokeWidth="1" strokeLinecap="butt" strokeLinejoin="miter" strokeMiterlimit="10" strokeDasharray="" strokeDashoffset="0">
            <g transform="scale(10.66667,10.66667)">
              <path d="M22,20l-2,2l-6,-6v-2h2z" />
              <path d="M9,16c-3.9,0 -7,-3.1 -7,-7c0,-3.9 3.1,-7 7,-7c3.9,0 7,3.1 7,7c0,3.9 -3.1,7 -7,7zM9,4c-2.8,0 -5,2.2 -5,5c0,2.8 2.2,5 5,5c2.8,0 5,-2.2 5,-5c0,-2.8 -2.2,-5 -5,-5z" />
              <path transform="translate(-5.90254,14.24719) rotate(-44.992)" d="M13.7,12.5h1v3.5h-1z" />
            </g>
          </g>
        </svg>
      </Link>

      {user && (
        <div className="notific-cont" ref={notifRef}>
          <div className="notification-bell" id="notification-bell" onClick={toggleNotif}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" className="header-icon">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z" />
            </svg>
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
            )}
          </div>
          {notifOpen && (
            <div className="notification-dropdown" id="notification-dropdown">
              <div className="notification-header">
                <span>Уведомления</span>
                <button id="mark-all-read" className="btn btn-sm btn-link" onClick={markAllRead}>
                  Прочитать все
                </button>
              </div>
              <div className="notification-list" id="notification-list">
                {notifications.length === 0 && (
                  <div className="notification-empty">Нет уведомлений</div>
                )}
                {notifications.map(n => (
                  <div key={n.id} className={`notification-item ${n.is_read ? '' : 'unread'}`}>
                    <div className="notification-content">
                      <span className="notification-message">{n.message}</span>
                      <span className="notification-time">{n.created_at}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!loading && !user && (
        <Link className="login-pill" to="/login/">Войти</Link>
      )}

      {user && (
        <button className="user-avatar-btn" id="avatar-toggle"
          onClick={() => navigate('/profile/')}
          aria-label="Профиль">
          {user.avatar ? (
            <img src={user.avatar} alt={user.username} className="user-avatar" />
          ) : (
            <span className="user-avatar user-avatar-placeholder"
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'var(--primary)', color: '#fff', fontWeight: 600, fontSize: 14,
                width: '100%', height: '100%', borderRadius: '10px',
              }}>
              {user.username?.[0]?.toUpperCase() || '?'}
            </span>
          )}
        </button>
      )}
    </div>
  )
}

export default UserArea
