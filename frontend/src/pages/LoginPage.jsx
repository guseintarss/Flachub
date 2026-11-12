import { useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { DEMO_CREDENTIALS } from '../demo/credentials'

const isDemo = import.meta.env.VITE_DEMO === 'true'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const resetOk = searchParams.get('reset') === 'ok'
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  async function handleDemoLogin(account) {
    const credentials = DEMO_CREDENTIALS[account]
    setError('')
    setDemoLoading(account)
    setUsername(credentials.username)
    setPassword(credentials.password)
    try {
      await login(credentials.username, credentials.password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
    setDemoLoading('')
  }

  return (
    <main className="page auth-page">
      <div className="pg-container">
        <div className="auth-card">
          <header className="auth-card-head">
            <span className="auth-kicker">ФлакХаб · сообщество</span>
            <h1 className="auth-title">Вход</h1>
            <p className="auth-subtitle">Продолжайте читать, обсуждать и публиковать.</p>
          </header>

          {resetOk && (
            <div className="form-message is-success" role="status">
              Пароль изменён. Войдите с новым паролем.
            </div>
          )}

          {error && (
            <div className="form-message is-error" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label className="form-label" htmlFor="login-username">Логин</label>
              <input
                id="login-username"
                type="text"
                className="form-control"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="form-field">
              <label className="form-label" htmlFor="login-password">Пароль</label>
              <input
                id="login-password"
                type="password"
                className="form-control"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            <div className="auth-form-row">
              <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
                {loading ? 'Вход…' : 'Войти'}
              </button>
              <Link to="/forgot-password/" className="auth-link-muted">Забыли пароль?</Link>
            </div>
          </form>

          {isDemo && (
            <div className="auth-demo">
              <p className="auth-demo-note">Демо-стенд: данные хранятся только в вашем браузере</p>
              <div className="auth-demo-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleDemoLogin('user')}
                  disabled={!!demoLoading}
                >
                  {demoLoading === 'user' ? 'Вход…' : 'Войти как читатель'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleDemoLogin('admin')}
                  disabled={!!demoLoading}
                >
                  {demoLoading === 'admin' ? 'Вход…' : 'Войти как админ'}
                </button>
              </div>
              <p className="auth-demo-hint">demo / demo1234, admin / admin1234</p>
            </div>
          )}

          <p className="auth-footer">
            Нет аккаунта? <Link to="/register/">Зарегистрироваться</Link>
          </p>
        </div>
      </div>
    </main>
  )
}

export default LoginPage
