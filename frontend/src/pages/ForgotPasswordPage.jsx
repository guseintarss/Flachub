import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function ForgotPasswordPage() {
  const { resetPassword } = useAuth()
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      await resetPassword(email)
      setSuccess('Письмо для сброса пароля отправлено на ваш email')
      setEmail('')
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <main className="page auth-page">
      <div className="pg-container">
        <div className="auth-card">
          <header className="auth-card-head">
            <span className="auth-kicker">ФлакХаб · доступ</span>
            <h1 className="auth-title">Сброс пароля</h1>
            <p className="auth-subtitle">Введите email, и мы отправим ссылку для восстановления доступа.</p>
          </header>

          {error && <div className="form-message is-error" role="alert">{error}</div>}
          {success && <div className="form-message is-success" role="status">{success}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label className="form-label" htmlFor="forgot-email">Email</label>
              <input
                id="forgot-email"
                type="email"
                className="form-control"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
              {loading ? 'Отправка…' : 'Отправить ссылку'}
            </button>
          </form>

          <p className="auth-footer">
            <Link to="/login/">Вернуться к входу</Link>
          </p>
        </div>
      </div>
    </main>
  )
}

export default ForgotPasswordPage
