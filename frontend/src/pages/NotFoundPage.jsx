import { Link } from 'react-router-dom'

const NotFoundPage = () => (
  <main className="page">
    <div className="pg-container">
      <div className="not-found">
        <p className="not-found-code">404</p>
        <h1 className="not-found-title">Страница не найдена</h1>
        <p className="not-found-text">Возможно, ссылка устарела или страница была удалена.</p>
        <Link to="/" className="btn btn-primary">
          <i className="fas fa-home" /> На главную
        </Link>
      </div>
    </div>
  </main>
)

export default NotFoundPage
