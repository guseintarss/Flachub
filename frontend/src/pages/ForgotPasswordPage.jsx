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
            <h2 style={{ margin: '0 0 8px', textAlign: 'center', fontSize: '1.5rem' }}>Сброс пароля</h2>
            <p style={{ margin: '0 0 24px', textAlign: 'center', fontSize: '0.9rem', color: 'var(--muted)' }}>
              Введите ваш email, и мы отправим ссылку для сброса пароля
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
              <div style={{ marginBottom: 20 }}>
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  placeholder="your@email.com"
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    border: '2px solid var(--border)',
                    borderRadius: 10,
                    fontSize: '1rem',
                    background: 'var(--bg)',
                    color: 'var(--text)',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', justifyContent: 'center', padding: '12px 20px' }}
              >
                {loading ? 'Отправка...' : 'Отправить'}
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: 20, fontSize: '0.9rem', color: 'var(--muted)' }}>
              <Link to="/login/" style={{ color: 'var(--primary)' }}>Вернуться к входу</Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default ForgotPasswordPage
