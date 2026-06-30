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
            <h2 style={{ margin: '0 0 24px', textAlign: 'center', fontSize: '1.5rem' }}>Новый пароль</h2>

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
                <label className="form-label">Новый пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={newPassword1}
                  onChange={e => setNewPassword1(e.target.value)}
                  required
                  minLength={8}
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

              <div style={{ marginBottom: 20 }}>
                <label className="form-label">Подтвердите пароль</label>
                <input
                  type="password"
                  className="form-control"
                  value={newPassword2}
                  onChange={e => setNewPassword2(e.target.value)}
                  required
                  minLength={8}
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
                {loading ? 'Сохранение...' : 'Сохранить пароль'}
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

export default ResetPasswordPage
