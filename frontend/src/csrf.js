export function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]')
  if (meta) return meta.getAttribute('content')
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : null
}

// Токен ставится ответом /me/. Если пользователь отправил форму раньше,
// чем завершился начальный запрос, запрашиваем токен ещё раз.
export async function ensureCSRFToken() {
  let token = getCSRFToken()
  if (!token) {
    try {
      await fetch('/api/mobile/me/', { credentials: 'same-origin' })
    } catch {
      // Сеть недоступна — ниже вернём null, запрос всё равно упадёт с понятной ошибкой.
    }
    token = getCSRFToken()
  }
  return token
}
