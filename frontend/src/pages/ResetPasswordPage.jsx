import { useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function ResetPasswordPage() {
  const { confirmPasswordReset } = useAuth()
  const { uidb64, token } = useParams()
  const navigate = useNavigate()
  const [newPassword1, setNewPassword1] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await confirmPasswordReset(uidb64, token, newPassword1, newPassword2)
      navigate('/login/?reset=ok')
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
            <h1 className="auth-title">Новый пароль</h1>
            <p className="auth-subtitle">Придумайте пароль, который сложно угадать.</p>
          </header>

          {error && <div className="form-message is-error" role="alert">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label className="form-label" htmlFor="reset-password1">Новый пароль</label>
              <input
                id="reset-password1"
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
              <label className="form-label" htmlFor="reset-password2">Подтвердите пароль</label>
              <input
                id="reset-password2"
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
              {loading ? 'Сохранение…' : 'Сохранить пароль'}
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

export default ResetPasswordPage
