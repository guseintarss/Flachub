import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Brand from './Brand'
import BurgerMenu from './BurgerMenu'
import UserArea from './Userarea'
import { useBurgerMenu } from './useBurgerMenu'

const NAV_ITEMS = [
  { label: 'Лента', to: '/', type: null },
  { label: 'Статьи', to: '/search/?post_type=article', type: 'article' },
  { label: 'Разборы', to: '/search/?post_type=review', type: 'review' },
  { label: 'Новости', to: '/search/?post_type=news', type: 'news' },
  { label: 'Идеи', to: '/search/?post_type=idea', type: 'idea' },
]

const Header = () => {
  useBurgerMenu()
  const location = useLocation()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')

  const currentType = new URLSearchParams(location.search).get('post_type')
  const isSearchPage = location.pathname.startsWith('/search')

  function handleSearch(e) {
    e.preventDefault()
    const value = query.trim()
    navigate(value ? `/search/?q=${encodeURIComponent(value)}` : '/search/')
  }

  return (
    <header className="site-header">
      <div className="pg-container header-inner">
        <button id="burger" className="header__burger-menu" aria-label="Открыть меню">
          <span></span><span></span><span></span>
        </button>
        <Brand />

        <nav className="header-nav" aria-label="Разделы сообщества">
          {NAV_ITEMS.map((item) => {
            const active = item.type
              ? isSearchPage && currentType === item.type
              : location.pathname === '/'
            return (
              <Link key={item.label} to={item.to} className={active ? 'is-active' : ''}>
                {item.label}
              </Link>
            )
          })}
        </nav>

        <form className="header-search" onSubmit={handleSearch} role="search">
          <label htmlFor="header-search-input" className="visually-hidden">Поиск по сообществу</label>
          <input
            id="header-search-input"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск по сообществу"
            autoComplete="off"
          />
          <button type="submit" aria-label="Найти">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.2-3.2" />
            </svg>
          </button>
        </form>

        <div className="menu-overlay" id="menu-overlay"></div>
        <BurgerMenu />
        <UserArea />
      </div>
    </header>
  )
}

export default Header
