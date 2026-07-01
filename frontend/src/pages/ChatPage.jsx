import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import UserAvatar from '../components/UserAvatar'
import Sidebar from '../components/Sidebar/Sidebar'
import { useAuth } from '../context/AuthContext'
import { getChat, getChatMessages, sendMessage, markChatRead } from '../api'
import '../styles/chat.css'

function ChatPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [chat, setChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [online, setOnline] = useState(false)
  const messagesRef = useRef(null)
  const wsRef = useRef(null)
  const isNearBottomRef = useRef(true)

  const isNearBottom = useCallback(() => {
    const el = messagesRef.current
    if (!el) return true
    return el.scrollHeight - el.scrollTop - el.clientHeight < 120
  }, [])

  const scrollToBottom = useCallback((smooth = true) => {
    const el = messagesRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: smooth ? 'smooth' : 'instant' })
  }, [])

  useEffect(() => {
    if (isNearBottomRef.current) scrollToBottom()
    isNearBottomRef.current = isNearBottom()
  }, [messages, isNearBottom, scrollToBottom])

  const handleScroll = useCallback(() => {
    isNearBottomRef.current = isNearBottom()
  }, [isNearBottom])

  useEffect(() => {
    setLoading(true)
    Promise.all([getChat(id), getChatMessages(id)])
      .then(([chatData, msgsData]) => {
        setChat(chatData)
        setMessages(msgsData.results || msgsData || [])
        markChatRead(id).catch(() => {})
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.port === '5173' ? 'localhost:8000' : window.location.host
    const wsUrl = `${protocol}//${host}/ws/chat/${id}/`
    let ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setOnline(true)
      ws.send(JSON.stringify({ type: 'mark_read' }))
    }
    ws.onclose = () => setOnline(false)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'new_message') {
          setMessages(prev => {
            if (prev.some(m => m.id === data.message.id)) return prev
            const tempIdx = prev.findIndex(m =>
              String(m.id).startsWith('temp-') &&
              m.sender?.id === data.message.sender?.id &&
              m.text === data.message.text
            )
            if (tempIdx >= 0) {
              const next = [...prev]
              next[tempIdx] = data.message
              return next
            }
            return [...prev, data.message]
          })
        } else if (data.type === 'marked_read') {
          setMessages(prev => prev.map(m => {
            if (data.by_user !== user?.id && m.sender?.id === user?.id && !m.is_read) return { ...m, is_read: true }
            if (m.sender?.id !== user?.id && !m.is_read) return { ...m, is_read: true }
            return m
          }))
        }
      } catch {}
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [id, user])

  const handleSend = useCallback(async (e) => {
    e.preventDefault()
    if (!text.trim() || sending) return
    const msgText = text.trim()
    setText('')
    setSending(true)

    const tempId = `temp-${Date.now()}`
    const optimistic = {
      id: tempId,
      sender: user ? { id: user.id, username: user.username } : null,
      text: msgText,
      created_at: new Date().toISOString(),
      is_read: false,
    }
    setMessages(prev => [...prev, optimistic])
    scrollToBottom(false)

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'send_message', text: msgText }))
    }

    try {
      const msg = await sendMessage(id, msgText)
      setMessages(prev => prev.map(m => m.id === tempId ? msg : m))
    } catch {
      setMessages(prev => prev.filter(m => m.id !== tempId))
    }
    setSending(false)
  }, [text, sending, id, user])

  const other = chat?.participants?.find(p => p.id !== user?.id) || chat?.participants?.[0]

  if (loading) {
    return (
      <main className="page">
        <div className="pg-container layout">
          <div className="content"><div className="chat-loading"><i className="fas fa-spinner fa-spin" /></div></div>
        </div>
      </main>
    )
  }

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          <div className="chat-page">
            <div className="chat-header">
              <Link to="/inbox/" className="chat-back"><i className="fas fa-arrow-left" /></Link>
              <UserAvatar user={other} size={36} />
              <div className="chat-header-info">
                <div className="chat-header-name">{other?.username || 'Пользователь'}</div>
                <div className={`chat-status ${online ? 'chat-status-online' : ''}`}>
                  {online ? 'в сети' : 'офлайн'}
                </div>
              </div>
            </div>

            <div className="chat-messages" ref={messagesRef} onScroll={handleScroll}>
              {messages.length === 0 ? (
                <div className="chat-empty">Напишите первое сообщение</div>
              ) : (
                messages.map(msg => {
                  const isMine = msg.sender?.id === user?.id
                  return (
                    <div key={msg.id} className={`chat-msg ${isMine ? 'chat-msg-mine' : 'chat-msg-other'}`}>
                      <div className="chat-msg-text">{msg.text}</div>
                      <div className="chat-msg-meta">
                        <span className="chat-msg-time">
                          {new Date(msg.created_at).toLocaleString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {isMine && (
                          <span className={`chat-msg-status ${msg.is_read ? 'chat-msg-read' : 'chat-msg-delivered'}`}>
                            {msg.is_read ? '✓✓' : '✓'}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>

            <form className="chat-input" onSubmit={handleSend}>
              <input
                type="text"
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder="Написать сообщение..."
                maxLength={2000}
              />
              <button type="submit" disabled={!text.trim() || sending}>
                <i className="fas fa-paper-plane" />
              </button>
            </form>
          </div>
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export default ChatPage
