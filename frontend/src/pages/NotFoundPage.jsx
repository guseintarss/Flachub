import { Link } from 'react-router-dom'

const NotFoundPage = () => (
  <main className="page">
    <div className="pg-container">
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ fontSize: '4rem', fontWeight: 800, color: 'var(--primary, #667eea)', lineHeight: 1 }}>
          404
        </div>
        <h1 style={{ margin: '16px 0 8px' }}>Страница не найдена</h1>
        <p style={{ color: 'var(--muted)', marginBottom: 24 }}>
          Возможно, ссылка устарела или страница была удалена.
        </p>
        <Link to="/" className="btn btn-primary">
          <i className="fas fa-home"></i> На главную
        </Link>
      </div>
    </div>
  </main>
)

export default NotFoundPage
