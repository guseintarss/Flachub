import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function CategoryList() {
  const [categories, setCategories] = useState([])

  useEffect(() => {
    fetch("/api/mobile/categories/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        const list = data.results || data
        if (Array.isArray(list)) setCategories(list)
      })
      .catch(() => {})
  }, [])

  return (
    <li className="menu-category">
      <div className="menu-category-title">
        <i className="fas fa-folder"></i> Категории
      </div>
      {categories.map((cat) => (
        <Link key={cat.id} to={`/category/${cat.slug}/`} className="menu_link">
          <i className="fas fa-angle-right"></i> {cat.name}
        </Link>
      ))}
    </li>
  )
}

function BurgerMenu() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className="top-nav" aria-label="Основное меню">
      <ul className="menu-list">
        <li className="menu-category">
          <div className="menu-category-title">
            <i className="fas fa-compass"></i> Навигация
          </div>
          <Link to="/" className="menu_link">
            <i className="fas fa-home"></i> Главная
          </Link>
        </li>

        <hr className="menu-divider" />

        <CategoryList />

        <hr className="menu-divider" />

        <li className="menu-category">
          {!loading && !user ? (
            <Link to="/login/" className="menu_link">
              <i className="fas fa-sign-in-alt"></i> Войти
            </Link>
          ) : (
            <>
              <div className="menu-category-title">
                <i className="fas fa-user"></i> Профиль
              </div>
              <Link to="/profile/" className="menu_link">
                <i className="fas fa-user-circle"></i> Мой профиль
              </Link>
              <Link to="/bookmarks/" className="menu_link">
                <i className="fas fa-bookmark"></i> Закладки
              </Link>
              <Link to="/subscriptions/" className="menu_link">
                <i className="fas fa-pen-fancy"></i> Подписки
              </Link>
              {user?.is_staff && (
                <Link to="/admin/" className="menu_link">
                  <i className="fas fa-chart-line"></i> Админка
                </Link>
              )}
              <hr className="menu-divider" />
              <button onClick={handleLogout} className="menu_link logout-link">
                <i className="fas fa-sign-out-alt"></i> Выйти
              </button>
            </>
          )}
        </li>
      </ul>
    </nav>
  )
}

export default BurgerMenu
