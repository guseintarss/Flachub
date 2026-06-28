export function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]')
  if (meta) return meta.getAttribute('content')
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : null
}
