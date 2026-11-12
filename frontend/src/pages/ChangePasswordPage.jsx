import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function ChangePasswordPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword1, setNewPassword1] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (newPassword1 !== newPassword2) {
      setError('Новые пароли не совпадают')
      return
    }

    if (newPassword1.length < 8) {
      setError('Новый пароль должен содержать минимум 8 символов')
      return
    }

    setLoading(true)
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
        || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
      const res = await fetch('/api/mobile/password/change/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrf ? { 'X-CSRFToken': csrf } : {}),
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          old_password: oldPassword,
          new_password1: newPassword1,
          new_password2: newPassword2,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Ошибка при смене пароля')
        return
      }
      setSuccess('Пароль успешно изменён')
      setOldPassword('')
      setNewPassword1('')
      setNewPassword2('')
    } catch {
      setError('Ошибка соединения с сервером')
    }
    setLoading(false)
  }

  if (!user) {
    return (
      <main className="page auth-page">
        <div className="pg-container">
          <div className="auth-card auth-card--center">
            <h1 className="auth-title">Нужен вход</h1>
            <p className="auth-subtitle">Чтобы сменить пароль, войдите в аккаунт.</p>
            <Link to="/login/" className="btn btn-primary">Войти</Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="page auth-page">
      <div className="pg-container">
        <div className="auth-card">
          <header className="auth-card-head">
            <span className="auth-kicker">ФлакХаб · безопасность</span>
            <h1 className="auth-title">Смена пароля</h1>
            <p className="auth-subtitle">Вы вошли как {user.username}.</p>
          </header>

          {error && <div className="form-message is-error" role="alert">{error}</div>}
          {success && <div className="form-message is-success" role="status">{success}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label className="form-label" htmlFor="change-old-password">Старый пароль</label>
              <input
                id="change-old-password"
                type="password"
                className="form-control"
                value={oldPassword}
                onChange={e => setOldPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="change-new-password1">Новый пароль</label>
              <input
                id="change-new-password1"
                type="password"
                className="form-control"
                value={newPassword1}
                onChange={e => setNewPassword1(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="change-new-password2">Повторите новый пароль</label>
              <input
                id="change-new-password2"
                type="password"
                className="form-control"
                value={newPassword2}
                onChange={e => setNewPassword2(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
              {loading ? 'Смена…' : 'Сменить пароль'}
            </button>
          </form>

          <p className="auth-footer">
            <Link to="/profile/edit/">Вернуться к редактированию профиля</Link>
          </p>
        </div>
      </div>
    </main>
  )
}

export default ChangePasswordPage
