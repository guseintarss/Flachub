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

  return (
    <main className="page auth-page">
      <div className="pg-container">
        <div className="auth-card auth-card--wide">
          <header className="auth-card-head">
            <span className="auth-kicker">ФлакХаб · сообщество</span>
            <h1 className="auth-title">Создать аккаунт</h1>
            <p className="auth-subtitle">Присоединяйтесь к практикам, которые делятся опытом.</p>
          </header>

          {error && (
            <div className="form-message is-error" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label className="form-label" htmlFor="register-username">Логин</label>
              <input id="register-username" type="text" className="form-control" value={form.username} onChange={set('username')} autoComplete="username" required />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="register-email">E-mail</label>
              <input id="register-email" type="email" className="form-control" value={form.email} onChange={set('email')} autoComplete="email" required />
            </div>
            <div className="form-row">
              <div className="form-field">
                <label className="form-label" htmlFor="register-first-name">Имя</label>
                <input id="register-first-name" type="text" className="form-control" value={form.first_name} onChange={set('first_name')} autoComplete="given-name" />
              </div>
              <div className="form-field">
                <label className="form-label" htmlFor="register-last-name">Фамилия</label>
                <input id="register-last-name" type="text" className="form-control" value={form.last_name} onChange={set('last_name')} autoComplete="family-name" />
              </div>
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="register-password1">Пароль</label>
              <input id="register-password1" type="password" className="form-control" value={form.password1} onChange={set('password1')} autoComplete="new-password" required />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="register-password2">Повторите пароль</label>
              <input id="register-password2" type="password" className="form-control" value={form.password2} onChange={set('password2')} autoComplete="new-password" required />
            </div>

            <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
              {loading ? 'Регистрация…' : 'Зарегистрироваться'}
            </button>
          </form>

          <p className="auth-footer">
            Уже есть аккаунт? <Link to="/login/">Войти</Link>
          </p>
        </div>
      </div>
    </main>
  )
}

export default RegisterPage
