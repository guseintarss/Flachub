function getColorFromName(name) {
  const colors = [
    ['#667eea', '#764ba2'],
    ['#f093fb', '#f5576c'],
    ['#4facfe', '#00f2fe'],
    ['#43e97b', '#38f9d7'],
    ['#fa709a', '#fee140'],
    ['#a18cd1', '#fbc2eb'],
    ['#fccb90', '#d57eeb'],
    ['#e0c3fc', '#8ec5fc'],
    ['#f5576c', '#ff6f91'],
    ['#00b4db', '#0083b0'],
    ['#11998e', '#38ef7d'],
    ['#fc5c7d', '#6a82fb'],
    ['#c471f5', '#fa71cd'],
    ['#48c6ef', '#6f86d6'],
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

function UserAvatar({ user, size = 36, style }) {
  if (user?.avatar) {
    return (
      <img
        src={user.avatar}
        alt={user.username || 'avatar'}
        style={{ width: size, height: size, borderRadius: '50%', objectFit: 'cover', ...style }}
      />
    )
  }

  const letter = (user?.first_name?.[0] || user?.username?.[0] || '?').toUpperCase()
  const [c1, c2] = getColorFromName(user?.username || user?.first_name || 'user')

  return (
    <div
      style={{
        width: size, height: size, borderRadius: '50%',
        background: `linear-gradient(135deg, ${c1}, ${c2})`,
        color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: size * 0.4, fontWeight: 700, letterSpacing: 1,
        flexShrink: 0, userSelect: 'none',
        ...style,
      }}>
      {letter}
    </div>
  )
}

export default UserAvatar