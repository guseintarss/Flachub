function getColorFromName(name) {
  const colors = [
    ['#2f5d48', '#7d9a6f'],
    ['#7a4a2f', '#c08a5e'],
    ['#3f5a66', '#7e9aa3'],
    ['#5a5340', '#a39a6f'],
    ['#6b3f4a', '#a97882'],
    ['#37504a', '#84a094'],
    ['#6d5427', '#b39a5f'],
    ['#46543a', '#8fa077'],
    ['#544a63', '#928aa8'],
    ['#5d3f35', '#9c7a68'],
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