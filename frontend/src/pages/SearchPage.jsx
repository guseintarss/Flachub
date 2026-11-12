import { useState, useEffect, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import PostCard from '../components/Feed/PostCard'
import UserAvatar from '../components/UserAvatar'
import Sidebar from '../components/Sidebar/Sidebar'

const POST_TYPES = [
  { value: '', label: 'Все типы' },
  { value: 'article', label: 'Статьи' },
  { value: 'news', label: 'Новости' },
  { value: 'idea', label: 'Идеи' },
  { value: 'post', label: 'Посты' },
  { value: 'review', label: 'Разборы' },
]

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [tab, setTab] = useState('articles')
  const [results, setResults] = useState([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    cat: '',
    post_type: searchParams.get('post_type') || '',
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
    const q = searchParams.get('q') || ''
    const type = searchParams.get('post_type') || ''
    setQuery(q)
    setFilters(prev => ({ ...prev, post_type: type }))
    doSearch(1, 'articles', q, { ...filters, post_type: type })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  async function doSearch(p = 1, overrideTab = tab, overrideQuery = query, overrideFilters = filters) {
    const currentPage = p
    const currentTab = overrideTab
    setLoading(true)
    try {
      let url
      if (currentTab === 'articles') {
        url = `/api/mobile/posts/?page=${currentPage}&page_size=20`
        if (overrideQuery) url += `&search=${encodeURIComponent(overrideQuery)}`
        if (overrideFilters.cat) url += `&cat=${overrideFilters.cat}`
        if (overrideFilters.post_type) url += `&post_type=${overrideFilters.post_type}`
        if (overrideFilters.ordering) url += `&ordering=${overrideFilters.ordering}`
      } else {
        url = `/api/mobile/users/?page=${currentPage}&page_size=20`
        if (overrideQuery) url += `&search=${encodeURIComponent(overrideQuery)}`
        if (overrideFilters.ordering) url += `&ordering=${overrideFilters.ordering}`
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
      setTotalPages(1)
    }
    setLoading(false)
  }

  function handleSubmit(e) {
    e.preventDefault()
    setPage(1)
    const params = new URLSearchParams()
    if (query.trim()) params.set('q', query.trim())
    if (filters.post_type) params.set('post_type', filters.post_type)
    setSearchParams(params)
  }

  function switchTab(nextTab) {
    setTab(nextTab)
    setPage(1)
    doSearch(1, nextTab, query, filters)
  }

  function setFilter(key, value) {
    const nextFilters = { ...filters, [key]: value }
    setFilters(nextFilters)
    setPage(1)
    if (key === 'post_type') {
      const params = new URLSearchParams(searchParams)
      if (value) params.set('post_type', value)
      else params.delete('post_type')
      if (query.trim()) params.set('q', query.trim())
      else params.delete('q')
      setSearchParams(params)
    } else {
      doSearch(1, tab, query, nextFilters)
    }
  }

  function goToPage(nextPage) {
    setPage(nextPage)
    doSearch(nextPage, tab, query, filters)
  }

  const hasQuery = query.trim() || filters.cat || filters.post_type

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content search-page">
          <header className="search-header">
            <p className="feed-kicker">Поиск</p>
            <h1 className="search-title">Найдите материал или автора</h1>
            <p className="search-subtitle">Ищите по заголовкам, текстам, категориям и людям.</p>
          </header>

          <form onSubmit={handleSubmit} className="search-bar" role="search">
            <label htmlFor="search-query" className="visually-hidden">Поисковый запрос</label>
            <input
              ref={inputRef}
              id="search-query"
              type="search"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Например: React, Django, PostgreSQL"
              className="form-control"
              autoComplete="off"
            />
            <button type="submit" className="btn btn-primary">Найти</button>
          </form>

          <div className="search-tabs" role="tablist" aria-label="Тип результатов">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'articles'}
              className={tab === 'articles' ? 'is-active' : ''}
              onClick={() => switchTab('articles')}
            >
              Публикации
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'authors'}
              className={tab === 'authors' ? 'is-active' : ''}
              onClick={() => switchTab('authors')}
            >
              Авторы
            </button>
          </div>

          {tab === 'articles' && (
            <div className="search-filters">
              <label className="visually-hidden" htmlFor="search-category">Категория</label>
              <select
                id="search-category"
                value={filters.cat}
                onChange={e => setFilter('cat', e.target.value)}
                className="form-select"
              >
                <option value="">Все категории</option>
                {categories.map(c => (
                  <option key={c.id} value={c.slug}>{c.name}</option>
                ))}
              </select>
              <label className="visually-hidden" htmlFor="search-type">Тип публикации</label>
              <select
                id="search-type"
                value={filters.post_type}
                onChange={e => setFilter('post_type', e.target.value)}
                className="form-select"
              >
                {POST_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
              <label className="visually-hidden" htmlFor="search-order">Сортировка</label>
              <select
                id="search-order"
                value={filters.ordering}
                onChange={e => setFilter('ordering', e.target.value)}
                className="form-select"
              >
                <option value="-time_create">Сначала новые</option>
                <option value="time_create">Сначала старые</option>
                <option value="-views">По просмотрам</option>
                <option value="-time_update">Недавно обновлённые</option>
              </select>
            </div>
          )}

          {tab === 'authors' && (
            <div className="search-filters">
              <label className="visually-hidden" htmlFor="search-authors-order">Сортировка авторов</label>
              <select
                id="search-authors-order"
                value={filters.ordering}
                onChange={e => setFilter('ordering', e.target.value)}
                className="form-select"
              >
                <option value="-date_joined">Новые пользователи</option>
                <option value="date_joined">Старые пользователи</option>
                <option value="posts_count">По количеству статей</option>
              </select>
            </div>
          )}

          {loading && (
            <div className="search-loading" role="status">
              <span className="search-spinner" aria-hidden="true" />
              <p>Ищем подходящее…</p>
            </div>
          )}

          {!loading && results.length === 0 && hasQuery && (
            <div className="search-empty">
              <h2>Ничего не нашлось</h2>
              <p>Попробуйте изменить запрос или снять фильтры.</p>
            </div>
          )}

          {!loading && !hasQuery && results.length === 0 && (
            <div className="search-empty">
              <h2>С чего начать</h2>
              <p>Введите запрос выше или выберите категорию и тип публикации.</p>
            </div>
          )}

          {!loading && results.length > 0 && (
            <>
              <p className="search-results-meta">
                Найдено: <strong>{count}</strong>
              </p>

              {tab === 'articles' && (
                <div className="feed-container">
                  {results.map(post => (
                    <PostCard key={post.id} post={post} />
                  ))}
                </div>
              )}

              {tab === 'authors' && (
                <div className="search-authors">
                  {results.map(user => (
                    <Link key={user.id} to={`/user/${user.username}/`} className="search-author-card">
                      <UserAvatar user={user} size={52} />
                      <div className="search-author-info">
                        <div className="search-author-name">
                          {user.first_name || user.last_name
                            ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                            : user.username}
                        </div>
                        <div className="search-author-handle">@{user.username}</div>
                        {user.bio && <p className="search-author-bio">{user.bio}</p>}
                      </div>
                      <div className="search-author-count">
                        {user.posts_count ?? '—'} <span>публикаций</span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}

              {totalPages > 1 && (
                <nav className="pagination" aria-label="Страницы поиска">
                  <button
                    className="pagination-btn"
                    disabled={page <= 1}
                    onClick={() => goToPage(Math.max(1, page - 1))}
                  >
                    ← Назад
                  </button>
                  <span className="pagination-status">{page} / {totalPages}</span>
                  <button
                    className="pagination-btn"
                    disabled={page >= totalPages}
                    onClick={() => goToPage(Math.min(totalPages, page + 1))}
                  >
                    Далее →
                  </button>
                </nav>
              )}
            </>
          )}
        </div>

        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar />
        </aside>
      </div>
    </main>
  )
}

export default SearchPage
