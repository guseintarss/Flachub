import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { ensureCSRFToken } from '../csrf'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/mobile/me/', { credentials: 'same-origin' })
      .then(res => {
        if (res.status === 403) return null
        if (!res.ok) throw new Error('auth err')
        return res.json()
      })
      .then(data => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (username, password) => {
    const headers = { 'Content-Type': 'application/json' }
    const csrf = await ensureCSRFToken()
    if (csrf) headers['X-CSRFToken'] = csrf
    const res = await fetch('/api/mobile/auth/login/', {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: JSON.stringify({ username, password }),
    })
    const text = await res.text()
    let data
    try {
      data = JSON.parse(text)
    } catch {
      throw new Error(`Ответ сервера (${res.status}): ${text.slice(0, 200)}`)
    }
    if (!res.ok) throw new Error(data.error || 'Ошибка входа')
    setUser(data)
    return data
  }, [])

  const logout = useCallback(async () => {
    const headers = {}
    const csrf = await ensureCSRFToken()
    if (csrf) headers['X-CSRFToken'] = csrf
    await fetch('/api/mobile/auth/logout/', {
      method: 'POST',
      headers,
      credentials: 'same-origin',
    })
    setUser(null)
  }, [])

  const resetPassword = useCallback(async (email) => {
    const headers = { 'Content-Type': 'application/json' }
    const csrf = await ensureCSRFToken()
    if (csrf) headers['X-CSRFToken'] = csrf
    const res = await fetch('/api/mobile/auth/password-reset/', {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: JSON.stringify({ email }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Ошибка отправки')
    return data
  }, [])

  const confirmPasswordReset = useCallback(async (uidb64, token, new_password1, new_password2) => {
    const headers = { 'Content-Type': 'application/json' }
    const csrf = await ensureCSRFToken()
    if (csrf) headers['X-CSRFToken'] = csrf
    const res = await fetch('/api/mobile/auth/password-reset/confirm/', {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: JSON.stringify({ uidb64, token, new_password1, new_password2 }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Ошибка сброса пароля')
    return data
  }, [])

  const register = useCallback(async (formData) => {
    const headers = { 'Content-Type': 'application/json' }
    const csrf = await ensureCSRFToken()
    if (csrf) headers['X-CSRFToken'] = csrf
    const res = await fetch('/api/mobile/auth/register/', {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: JSON.stringify(formData),
    })
    const text = await res.text()
    let data
    try {
      data = JSON.parse(text)
    } catch {
      throw new Error(`Ответ сервера (${res.status}): ${text.slice(0, 200)}`)
    }
    if (!res.ok) throw new Error(data.errors ? Object.values(data.errors).flat().join(', ') : 'Ошибка регистрации')
    setUser(data)
    return data
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, setUser, resetPassword, confirmPasswordReset }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
