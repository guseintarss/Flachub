import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import PostCard from '../components/Feed/PostCard'

const POST_TYPES = [
  { value: '', label: 'Все типы' },
  { value: 'article', label: 'Статьи' },
  { value: 'news', label: 'Новости' },
  { value: 'idea', label: 'Идеи' },
  { value: 'post', label: 'Посты' },
]

function SearchPage() {
  const [query, setQuery] = useState('')
  const [tab, setTab] = useState('articles')
  const [results, setResults] = useState([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    cat: '',
    post_type: '',
    ordering: '-time_create',
  })
  const inputRef = useRef(null)

  useEffect(() => {
    fetch('/api/mobile/categories/', { credentials: 'same-origin' })
      .then(r => r.json())
      .then(data => setCategories(data.results || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    doSearch(1)
  }, [])

  async function doSearch(p) {
    const currentPage = p ?? page
    setLoading(true)
    try {
      let url
      if (tab === 'articles') {
        url = `/api/mobile/posts/?page=${currentPage}&page_size=20`
        if (query) url += `&search=${encodeURIComponent(query)}`
        if (filters.cat) url += `&cat=${filters.cat}`
        if (filters.post_type) url += `&post_type=${filters.post_type}`
        if (filters.ordering) url += `&ordering=${filters.ordering}`
      } else {
        url = `/api/mobile/users/?page=${currentPage}&page_size=20`
        if (query) url += `&search=${encodeURIComponent(query)}`
        if (filters.ordering) url += `&ordering=${filters.ordering}`
      }
      const res = await fetch(url, { credentials: 'same-origin' })
      const data = await res.json()
      const items = data.results || []
      setResults(items)
      setCount(data.count || 0)
      setTotalPages(Math.ceil((data.count || 0) / 20) || 1)
    } catch {
      setResults([])
      setCount(0)
    }
    setLoading(false)
  }

  function handleSubmit(e) {
    e.preventDefault()
    setPage(1)
    doSearch(1)
  }

  function switchTab(t) {
    setTab(t)
    setPage(1)
    setTimeout(() => doSearch(1), 0)
  }

  function setFilter(key, value) {
    setFilters(f => ({ ...f, [key]: value }))
    setPage(1)
    setTimeout(() => doSearch(1), 0)
  }

  function goToPage(p) {
    setPage(p)
    doSearch(p)
  }

  return (
    <div className="search-page" style={{ maxWidth: 960, margin: '0 auto', padding: '24px 16px' }}>
      <div className="search-form-wrapper" style={{ marginBottom: 24 }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 10 }}>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleSubmit(e) } }}
            placeholder="Поиск статей и авторов..."
            className="form-control"
            style={{ flex: 1, padding: '14px 18px', fontSize: '1.05rem', borderRadius: 12, border: '2px solid var(--border)', background: 'var(--card-bg)', color: 'var(--text)' }}
          />
          <button type="submit" className="btn btn-primary" style={{ padding: '14px 28px', borderRadius: 12, fontSize: '1rem' }}>
            <i className="fas fa-search" /> Поиск
          </button>
        </form>
      </div>

      <div style={{ display: 'flex', gap: 2, marginBottom: 20, borderBottom: '2px solid var(--border)' }}>
        <button
          onClick={() => switchTab('articles')}
          style={{
            flex: 1, padding: '10px 20px', border: 'none', cursor: 'pointer', fontSize: '0.95rem', fontWeight: 600,
            background: tab === 'articles' ? 'var(--primary)' : 'transparent',
            color: tab === 'articles' ? '#fff' : 'var(--text)',
            borderRadius: '10px 10px 0 0', transition: '0.2s',
          }}>
          <i className="fas fa-file-alt" /> Статьи
        </button>
        <button
          onClick={() => switchTab('authors')}
          style={{
            flex: 1, padding: '10px 20px', border: 'none', cursor: 'pointer', fontSize: '0.95rem', fontWeight: 600,
            background: tab === 'authors' ? 'var(--primary)' : 'transparent',
            color: tab === 'authors' ? '#fff' : 'var(--text)',
            borderRadius: '10px 10px 0 0', transition: '0.2s',
          }}>
          <i className="fas fa-users" /> Авторы
        </button>
      </div>

      {tab === 'articles' && (
        <div className="search-filters" style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <select
            value={filters.cat}
            onChange={e => setFilter('cat', e.target.value)}
            className="form-select"
            style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--card-bg)', color: 'var(--text)', fontSize: '0.9rem' }}>
            <option value="">Все категории</option>
            {categories.map(c => (
              <option key={c.id} value={c.slug}>{c.name}</option>
            ))}
          </select>
          <select
            value={filters.post_type}
            onChange={e => setFilter('post_type', e.target.value)}
            className="form-select"
            style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--card-bg)', color: 'var(--text)', fontSize: '0.9rem' }}>
            {POST_TYPES.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <select
            value={filters.ordering}
            onChange={e => setFilter('ordering', e.target.value)}
            className="form-select"
            style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--card-bg)', color: 'var(--text)', fontSize: '0.9rem' }}>
            <option value="-time_create">Сначала новые</option>
            <option value="time_create">Сначала старые</option>
            <option value="-views">По просмотрам</option>
            <option value="-time_update">Недавно обновлённые</option>
          </select>
        </div>
      )}

      {tab === 'authors' && (
        <div className="search-filters" style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <select
            value={filters.ordering}
            onChange={e => setFilter('ordering', e.target.value)}
            className="form-select"
            style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--card-bg)', color: 'var(--text)', fontSize: '0.9rem' }}>
            <option value="-date_joined">Новые пользователи</option>
            <option value="date_joined">Старые пользователи</option>
            <option value="posts_count">По количеству статей</option>
          </select>
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem' }} />
          <p style={{ marginTop: 12 }}>Поиск...</p>
        </div>
      )}

      {!loading && results.length === 0 && (query || filters.cat || filters.post_type) && (
        <div className="empty-state" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <i className="fas fa-search-minus" style={{ fontSize: '3rem', opacity: 0.3 }} />
          <p style={{ marginTop: 16, fontSize: '1.1rem' }}>Ничего не найдено</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.6 }}>Попробуйте изменить запрос или фильтры</p>
        </div>
      )}

      {!loading && !query && results.length === 0 && (
        <div className="empty-state" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <i className="fas fa-search" style={{ fontSize: '3rem', opacity: 0.3 }} />
          <p style={{ marginTop: 16, fontSize: '1.1rem' }}>Начните поиск</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.6 }}>Введите запрос выше или выберите фильтры</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          <p style={{ marginBottom: 16, fontSize: '0.9rem', opacity: 0.6 }}>
            Найдено: {count}
          </p>

          {tab === 'articles' && (
            <div className="posts-grid" style={{ display: 'grid', gap: 16 }}>
              {results.map(post => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}

          {tab === 'authors' && (
            <div style={{ display: 'grid', gap: 12 }}>
              {results.map(user => (
                <Link
                  key={user.id}
                  to={`/user/${user.username}/`}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 16, padding: 16,
                    background: 'var(--card-bg)', borderRadius: 12, textDecoration: 'none',
                    color: 'var(--text)', border: '1px solid var(--border)', transition: '0.2s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--primary)'}
                  onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}>
                  <img
                    src={user.avatar || '/static/images/default-avatar.svg'}
                    alt={user.username}
                    style={{ width: 56, height: 56, borderRadius: '50%', objectFit: 'cover' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '1.05rem' }}>
                      {user.first_name || user.last_name
                        ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                        : user.username}
                    </div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.6 }}>@{user.username}</div>
                    {user.bio && (
                      <div style={{ fontSize: '0.85rem', opacity: 0.7, marginTop: 4, lineHeight: 1.3 }}>
                        {user.bio.length > 100 ? user.bio.slice(0, 100) + '...' : user.bio}
                      </div>
                    )}
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '0.85rem', opacity: 0.6, whiteSpace: 'nowrap' }}>
                    {user.posts_count ?? '—'} ст.
                  </div>
                </Link>
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 24 }}>
              <button
                disabled={page <= 1}
                onClick={() => goToPage(Math.max(1, page - 1))}
                className="btn btn-outline-secondary"
                style={{ padding: '8px 16px', borderRadius: 8 }}>
                <i className="fas fa-chevron-left" /> Назад
              </button>
              <span style={{ display: 'flex', alignItems: 'center', padding: '0 12px', fontSize: '0.9rem' }}>
                {page} / {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => goToPage(Math.min(totalPages, page + 1))}
                className="btn btn-outline-secondary"
                style={{ padding: '8px 16px', borderRadius: 8 }}>
                Вперёд <i className="fas fa-chevron-right" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SearchPage