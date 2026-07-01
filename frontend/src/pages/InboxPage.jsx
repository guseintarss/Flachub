import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import UserAvatar from '../components/UserAvatar'
import Sidebar from '../components/Sidebar/Sidebar'
import { useAuth } from '../context/AuthContext'
import '../styles/chat.css'

function InboxPage() {
  const { user } = useAuth()
  const [chats, setChats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/mobile/chats/')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(data => setChats(data.results || data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          <div className="inbox-page">
            <h1 className="inbox-title"><i className="fas fa-envelope" /> Сообщения</h1>
            {loading ? (
              <div className="inbox-loading"><i className="fas fa-spinner fa-spin" /> Загрузка...</div>
            ) : chats.length === 0 ? (
              <div className="inbox-empty">
                <i className="fas fa-inbox" />
                <h3>Нет сообщений</h3>
                <p>Напишите автору статьи, чтобы начать диалог</p>
              </div>
            ) : (
              <div className="inbox-list">
                {chats.map(chat => {
                  const other = chat.participants?.find(p => p.id !== user?.id) || chat.participants?.[0]
                  const last = chat.last_message
                  return (
                    <Link key={chat.id} to={`/chat/${chat.id}/`} className="inbox-item">
                      <UserAvatar user={other} size={48} />
                      <div className="inbox-item-body">
                        <div className="inbox-item-name">{other?.username || 'Пользователь'}</div>
                        {last && (
                          <div className="inbox-item-preview">{last.text}</div>
                        )}
                        <div className="inbox-item-time">
                          {last?.time ? new Date(last.time).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                        </div>
                      </div>
                      {chat.unread_count > 0 && (
                        <span className="inbox-badge">{chat.unread_count}</span>
                      )}
                    </Link>
                  )
                })}
              </div>
            )}
          </div>
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export default InboxPage
