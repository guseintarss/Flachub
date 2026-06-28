function SkeletonBox({ width, height, borderRadius = 4, className = '' }) {
  return <div className={`skeleton-line ${className}`} style={{ width, height, borderRadius }} />
}

function SkeletonCircle({ size }) {
  return <div className="skeleton-circle" style={{ width: size, height: size }} />
}

function SidebarSkeleton() {
  return (
    <aside className="sidebar" aria-label="Боковая панель">
      <div className="skeleton-sidebar">
        <SkeletonBox width="100%" height={200} borderRadius={12} />
        <div style={{ height: 16 }} />
        <SkeletonBox width="100%" height={150} borderRadius={12} />
        <div style={{ height: 16 }} />
        <SkeletonBox width="100%" height={180} borderRadius={12} />
      </div>
    </aside>
  )
}

export function PostDetailSkeleton() {
  return (
    <div className="page">
      <div className="reading-progress-bar skeleton-progress" />
      <div className="pg-container layout">
        <div className="content">
          <div className="article-container">
            <div className="article-wrapper">
              <div className="skeleton-header">
                <div className="skeleton-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                  <div className="skeleton-author">
                    <SkeletonCircle size={44} />
                    <div>
                      <SkeletonBox width={120} height={14} />
                      <div style={{ height: 6 }} />
                      <SkeletonBox width={80} height={12} />
                    </div>
                  </div>
                  <SkeletonBox width={100} height={32} borderRadius={8} />
                </div>
                <SkeletonBox width="70%" height={28} />
                <div style={{ height: 12 }} />
                <div className="skeleton-meta" style={{ display: 'flex', gap: 8 }}>
                  <SkeletonBox width={80} height={20} borderRadius={12} />
                  <SkeletonBox width={60} height={20} borderRadius={12} />
                  <SkeletonBox width={50} height={20} borderRadius={12} />
                </div>
              </div>

              <SkeletonBox width="100%" height={300} borderRadius={12} />
              <div style={{ height: 20 }} />

              <div className="skeleton-body">
                {[100, 90, 95, 80, 100, 60, 85, 45, 100, 70].map((w, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <SkeletonBox width={`${w}%`} height={14} />
                  </div>
                ))}
              </div>

              <div className="skeleton-tags" style={{ display: 'flex', gap: 8, margin: '24px 0' }}>
                <SkeletonBox width={60} height={24} borderRadius={12} />
                <SkeletonBox width={80} height={24} borderRadius={12} />
                <SkeletonBox width={70} height={24} borderRadius={12} />
              </div>

              <div className="skeleton-actions" style={{ display: 'flex', gap: 10 }}>
                <SkeletonBox width={80} height={34} borderRadius={8} />
                <SkeletonBox width={80} height={34} borderRadius={8} />
                <SkeletonBox width={80} height={34} borderRadius={8} />
              </div>

              <div style={{ marginTop: 40 }}>
                <SkeletonBox width={200} height={22} />
                <div style={{ height: 20 }} />
                <SkeletonBox width="100%" height={80} borderRadius={8} />
                <div style={{ height: 20 }} />
                {[1, 2, 3].map(i => (
                  <div key={i} className="skeleton-comment" style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
                    <SkeletonCircle size={32} />
                    <div style={{ flex: 1 }}>
                      <SkeletonBox width={100} height={12} />
                      <div style={{ height: 6 }} />
                      <SkeletonBox width="70%" height={12} />
                      <div style={{ height: 4 }} />
                      <SkeletonBox width="50%" height={12} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <SidebarSkeleton />
      </div>
    </div>
  )
}

export function PostListSkeleton() {
  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          {[1, 2, 3, 4].map(card => (
            <div key={card} className="post" style={{ marginBottom: 20, padding: 20, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
              <div className="skeleton-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <div className="skeleton-author" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <SkeletonCircle size={36} />
                  <div>
                    <SkeletonBox width={100} height={13} />
                    <div style={{ height: 4 }} />
                    <SkeletonBox width={70} height={11} />
                  </div>
                </div>
                <div className="skeleton-author" style={{ display: 'flex', gap: 8 }}>
                  <SkeletonBox width={50} height={18} borderRadius={12} />
                  <SkeletonBox width={60} height={18} borderRadius={12} />
                </div>
              </div>
              <SkeletonBox width="60%" height={20} />
              <div style={{ height: 10 }} />
              {card % 2 === 0 && <SkeletonBox width="100%" height={180} borderRadius={8} />}
              {card % 2 === 0 && <div style={{ height: 10 }} />}
              <SkeletonBox width="100%" height={13} />
              <div style={{ height: 4 }} />
              <SkeletonBox width="85%" height={13} />
              <div style={{ height: 16 }} />
              <div className="skeleton-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 12, borderTop: '1px solid var(--border)' }}>
                <div className="skeleton-author" style={{ display: 'flex', gap: 16 }}>
                  <SkeletonBox width={40} height={14} />
                  <SkeletonBox width={40} height={14} />
                  <SkeletonBox width={40} height={14} />
                  <SkeletonBox width={40} height={14} />
                </div>
                <SkeletonBox width={90} height={14} />
              </div>
            </div>
          ))}
        </div>
        <SidebarSkeleton />
      </div>
    </main>
  )
}

export function AddPostSkeleton() {
  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content">
          <div className="step-indicator" style={{ display: 'flex', justifyContent: 'center', gap: 12, marginBottom: 24 }}>
            {[1, 2, 3].map(s => (
              <div key={s} className="skeleton-author" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <SkeletonCircle size={28} />
                <SkeletonBox width={60} height={12} />
              </div>
            ))}
          </div>
          <div className="editor-wrapper" style={{ padding: 24, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <SkeletonBox width={120} height={18} />
            <div style={{ height: 16 }} />
            <SkeletonBox width="100%" height={40} borderRadius={8} />
            <div style={{ height: 16 }} />
            <SkeletonBox width="100%" height={300} borderRadius={8} />
            <div style={{ height: 16 }} />
            <div className="skeleton-row" style={{ display: 'flex', gap: 10 }}>
              <SkeletonBox width={100} height={34} borderRadius={8} />
              <SkeletonBox width={100} height={34} borderRadius={8} />
            </div>
          </div>
        </div>
        <SidebarSkeleton />
      </div>
    </main>
  )
}

export function ProfileSkeleton() {
  return (
    <main className="page">
      <div className="pg-container">
        <div className="author-hero-bg skeleton-line" style={{ height: 200 }} />
        <div className="author-hero-content" style={{ padding: '0 32px 32px', background: 'var(--surface)' }}>
          <div className="skeleton-row" style={{ display: 'flex', alignItems: 'flex-end', gap: 24, marginTop: -55, marginBottom: 18 }}>
            <SkeletonCircle size={120} />
            <div style={{ flex: 1, paddingBottom: 6 }}>
              <SkeletonBox width={200} height={28} />
              <div style={{ height: 6 }} />
              <SkeletonBox width={140} height={16} />
            </div>
            <SkeletonBox width={100} height={34} borderRadius={8} />
          </div>
          <SkeletonBox width="60%" height={14} />
          <div style={{ height: 24 }} />
          <div className="skeleton-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
            {[1, 2, 3].map(s => (
              <div key={s} className="skeleton-stat" style={{ padding: 18, borderRadius: 16, border: '1px solid var(--border)' }}>
                <SkeletonCircle size={40} />
                <div style={{ height: 10 }} />
                <SkeletonBox width={40} height={24} />
                <div style={{ height: 4 }} />
                <SkeletonBox width={80} height={12} />
              </div>
            ))}
          </div>
          <div style={{ height: 24 }} />
          <div className="profile-layout" style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24 }}>
            <div>
              <div className="skeleton-tabs" style={{ display: 'flex', gap: 4, marginBottom: 20 }}>
                {[1, 2, 3].map(t => <SkeletonBox key={t} width={100} height={36} borderRadius={8} />)}
              </div>
              {[1, 2].map(c => (
                <div key={c} className="post" style={{ marginBottom: 16, padding: 20, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
                  <SkeletonBox width="60%" height={18} />
                  <div style={{ height: 8 }} />
                  <SkeletonBox width="100%" height={12} />
                  <div style={{ height: 4 }} />
                  <SkeletonBox width="80%" height={12} />
                </div>
              ))}
            </div>
            <aside className="sidebar profile-sidebar" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="sidebar-widget" style={{ padding: 20, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--surface)' }}>
                <SkeletonBox width={120} height={16} />
                <div style={{ height: 12 }} />
                <SkeletonBox width="100%" height={12} />
                <div style={{ height: 4 }} />
                <SkeletonBox width="60%" height={12} />
              </div>
              <div className="sidebar-widget" style={{ padding: 20, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--surface)' }}>
                <SkeletonBox width={100} height={16} />
                <div style={{ height: 12 }} />
                <SkeletonBox width="100%" height={12} />
                <div style={{ height: 4 }} />
                <SkeletonBox width="100%" height={12} />
                <div style={{ height: 4 }} />
                <SkeletonBox width="70%" height={12} />
              </div>
            </aside>
          </div>
        </div>
      </div>
    </main>
  )
}

export function FormSkeleton() {
  return (
    <main className="page">
      <div className="pg-container">
        <div className="post edit-profile-page" style={{ maxWidth: 800, margin: '0 auto' }}>
          <SkeletonBox width={250} height={26} />
          <div style={{ height: 24 }} />
          <div className="skeleton-section" style={{ padding: 24, background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <SkeletonBox width={140} height={18} />
            <div style={{ height: 16 }} />
            <div className="skeleton-row" style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
              <SkeletonCircle size={80} />
              <div style={{ flex: 1 }}>
                <SkeletonBox width="100%" height={36} borderRadius={8} />
                <div style={{ height: 8 }} />
                <SkeletonBox width="100%" height={36} borderRadius={8} />
              </div>
            </div>
            <SkeletonBox width="100%" height={36} borderRadius={8} />
            <div style={{ height: 10 }} />
            <SkeletonBox width="100%" height={36} borderRadius={8} />
            <div style={{ height: 10 }} />
            <SkeletonBox width="100%" height={80} borderRadius={8} />
            <div style={{ height: 10 }} />
            <div className="skeleton-row" style={{ display: 'flex', gap: 10 }}>
              <SkeletonBox width={120} height={36} borderRadius={8} />
              <SkeletonBox width={120} height={36} borderRadius={8} />
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
