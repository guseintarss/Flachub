import { createContext, useContext, useState, useEffect, useCallback } from 'react'

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

  function csrfToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/)
    return m ? m[1] : ''
  }

  const login = useCallback(async (username, password) => {
    const res = await fetch('/api/mobile/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
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
    await fetch('/api/mobile/auth/logout/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      credentials: 'same-origin',
    })
    setUser(null)
  }, [])

  const register = useCallback(async (formData) => {
    const res = await fetch('/api/mobile/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
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
    <AuthContext.Provider value={{ user, loading, login, logout, register, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
