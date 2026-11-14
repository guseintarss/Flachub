function getColorFromName(name) {
  const colors = [
    ['#0c1f18', '#2f7d5a'],
    ['#1e0f0b', '#b05a3c'],
    ['#101820', '#466a80'],
    ['#1b150c', '#9a682f'],
    ['#1a1012', '#8f4a44'],
    ['#0c1210', '#3e5a4b'],
    ['#17131f', '#6a5a8a'],
    ['#080b0d', '#2d3942'],
    ['#141a10', '#5d7a3f'],
    ['#1c1116', '#8f5a6e'],
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
        style={{ width: size, height: size, borderRadius: '50%', objectFit: 'cover', border: '1px solid var(--border)', ...style }}
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