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
            <h2 style={{ margin: '0 0 24px', textAlign: 'center', fontSize: '1.5rem' }}>Вход</h2>

            {resetOk && (
              <div style={{
                padding: '12px 16px',
                background: '#dcfce7',
                color: '#16a34a',
                borderRadius: 8,
                marginBottom: 16,
                fontSize: '0.9rem',
              }}>
                Пароль успешно изменён. Войдите с новым паролем.
              </div>
            )}

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

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Логин</label>
                <input
                  type="text"
                  className="form-control"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
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
                <label className="form-label">Пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
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
                {loading ? 'Вход...' : 'Войти'}
              </button>

              <div style={{ textAlign: 'right', marginTop: 8 }}>
                <Link to="/forgot-password/" style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
                  Забыли пароль?
                </Link>
              </div>
            </form>

            {isDemo && (
              <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px dashed var(--border)' }}>
                <div style={{
                  textAlign: 'center',
                  fontSize: '0.85rem',
                  color: 'var(--muted)',
                  marginBottom: 12,
                }}>
                  Демо-стенд: данные хранятся только в вашем браузере
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ flex: 1, justifyContent: 'center' }}
                    onClick={() => handleDemoLogin('user')}
                    disabled={!!demoLoading}
                  >
                    {demoLoading === 'user' ? 'Вход...' : 'Войти как читатель'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ flex: 1, justifyContent: 'center' }}
                    onClick={() => handleDemoLogin('admin')}
                    disabled={!!demoLoading}
                  >
                    {demoLoading === 'admin' ? 'Вход...' : 'Войти как админ'}
                  </button>
                </div>
                <div style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--muted)', marginTop: 10 }}>
                  demo / demo1234 · admin / admin1234
                </div>
              </div>
            )}

            <div style={{ textAlign: 'center', marginTop: 20, fontSize: '0.9rem', color: 'var(--muted)' }}>
              Нет аккаунта?{' '}
              <Link to="/register/" style={{ color: 'var(--primary)' }}>Зарегистрироваться</Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default LoginPage
