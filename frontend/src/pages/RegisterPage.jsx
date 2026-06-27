import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password1: '',
    password2: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (form.password1 !== form.password2) {
      setError('Пароли не совпадают')
      return
    }
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const inputStyle = {
    width: '100%',
    padding: '12px 14px',
    border: '2px solid var(--border)',
    borderRadius: 10,
    fontSize: '1rem',
    background: 'var(--bg)',
    color: 'var(--text)',
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
            <h2 style={{ margin: '0 0 24px', textAlign: 'center', fontSize: '1.5rem' }}>Регистрация</h2>

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
              <div style={{ marginBottom: 14 }}>
                <label className="form-label">Логин</label>
                <input type="text" value={form.username} onChange={set('username')} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: 14 }}>
                <label className="form-label">E-mail</label>
                <input type="email" value={form.email} onChange={set('email')} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: 14 }}>
                <label className="form-label">Имя</label>
                <input type="text" value={form.first_name} onChange={set('first_name')} style={inputStyle} />
              </div>
              <div style={{ marginBottom: 14 }}>
                <label className="form-label">Фамилия</label>
                <input type="text" value={form.last_name} onChange={set('last_name')} style={inputStyle} />
              </div>
              <div style={{ marginBottom: 14 }}>
                <label className="form-label">Пароль</label>
                <input type="password" value={form.password1} onChange={set('password1')} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: 20 }}>
                <label className="form-label">Повторите пароль</label>
                <input type="password" value={form.password2} onChange={set('password2')} required style={inputStyle} />
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}
                style={{ width: '100%', justifyContent: 'center', padding: '12px 20px' }}>
                {loading ? 'Регистрация...' : 'Зарегистрироваться'}
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: 20, fontSize: '0.9rem', color: 'var(--muted)' }}>
              Уже есть аккаунт?{' '}
              <Link to="/login/" style={{ color: 'var(--primary)' }}>Войти</Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default RegisterPage
