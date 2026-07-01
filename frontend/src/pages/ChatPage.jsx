import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import UserAvatar from '../components/UserAvatar'
import Sidebar from '../components/Sidebar/Sidebar'
import { useAuth } from '../context/AuthContext'
import { getChat, getChatMessages, sendMessage } from '../api'
import '../styles/chat.css'

function ChatPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [chat, setChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    setLoading(true)
    Promise.all([getChat(id), getChatMessages(id)])
      .then(([chatData, msgsData]) => {
        setChat(chatData)
        setMessages(msgsData.results || msgsData || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!text.trim() || sending) return
    setSending(true)
    try {
      const msg = await sendMessage(id, text.trim())
      setMessages(prev => [...prev, msg])
      setText('')
    } catch {}
    setSending(false)
  }

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
              </div>
            </div>

            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-empty">Напишите первое сообщение</div>
              ) : (
                messages.map(msg => {
                  const isMine = msg.sender?.id === user?.id
                  return (
                    <div key={msg.id} className={`chat-msg ${isMine ? 'chat-msg-mine' : 'chat-msg-other'}`}>
                      <div className="chat-msg-text">{msg.text}</div>
                      <div className="chat-msg-time">
                        {new Date(msg.created_at).toLocaleString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  )
                })
              )}
              <div ref={messagesEndRef} />
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
