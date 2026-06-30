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
      <main className="page">
        <div className="pg-container">
          <div className="con">
            <div style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              boxShadow: 'var(--shadow)',
              padding: 40,
              maxWidth: 400,
              margin: '0 auto',
              textAlign: 'center',
            }}>
              <p>Необходимо войти в систему</p>
              <Link to="/login/" className="btn btn-primary" style={{ marginTop: 16, display: 'inline-block' }}>
                Войти
              </Link>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="page">
      <div className="pg-container">
        <div className="con">
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow)',
            padding: 40,
            maxWidth: 400,
            margin: '0 auto',
          }}>
            <h2 style={{ margin: '0 0 8px', textAlign: 'center', fontSize: '1.5rem' }}>Смена пароля</h2>
            <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 24 }}>
              {user.username}
            </p>

            {error && (
              <div style={{
                padding: '12px 16px',
                background: '#fee2e2',
                color: '#dc2626',
                borderRadius: 8,
                marginBottom: 16,
                fontSize: '0.9rem',
              }}>
                {error}
              </div>
            )}

            {success && (
              <div style={{
                padding: '12px 16px',
                background: '#dcfce7',
                color: '#16a34a',
                borderRadius: 8,
                marginBottom: 16,
                fontSize: '0.9rem',
              }}>
                {success}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Старый пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={oldPassword}
                  onChange={e => setOldPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    border: '2px solid var(--border)',
                    borderRadius: 10,
                    fontSize: '1rem',
                    background: 'var(--bg)',
                    color: 'var(--text)',
                  }}
                />
              </div>

              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Новый пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={newPassword1}
                  onChange={e => setNewPassword1(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    border: '2px solid var(--border)',
                    borderRadius: 10,
                    fontSize: '1rem',
                    background: 'var(--bg)',
                    color: 'var(--text)',
                  }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label className="form-label">Повторите новый пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={newPassword2}
                  onChange={e => setNewPassword2(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    border: '2px solid var(--border)',
                    borderRadius: 10,
                    fontSize: '1rem',
                    background: 'var(--bg)',
                    color: 'var(--text)',
                  }}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', justifyContent: 'center', padding: '12px 20px' }}
              >
                {loading ? 'Смена...' : 'Сменить пароль'}
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: 20 }}>
              <Link to="/profile/edit/" style={{ color: 'var(--primary)', fontSize: '0.9rem' }}>
                ← Назад к редактированию профиля
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default ChangePasswordPage
