import { Link } from 'react-router-dom'
import BrandMark from '../BrandMark'

function BrandSocials() {
  return (
    <div className="footer-brand">
      <Link to="/" className="footer-logo">
        <BrandMark />
        <span>ФлакХаб</span>
      </Link>
      <p className="footer-description">
        Платформа для IT-специалистов: делитесь знаниями,
        находите возможности и развивайтесь вместе с нами.
      </p>
      <div className="footer-social">
        <a href="https://t.me/+2-lThKE3m5c5YmQ6" className="text-decoration-none social-link" title="Telegram">
          <i className="fab fa-telegram"></i>
        </a>
        <a href="https://github.com/guseintarss/Flachub" className="text-decoration-none social-link" title="GitHub">
          <i className="fab fa-github"></i>
        </a>
        <a href="https://vk.com/club237403434" className="text-decoration-none social-link" title="VK">
          <i className="fab fa-vk"></i>
        </a>
      </div>
    </div>
  )
}

function Navigations() {
  return (
    <div className="footer-section">
      <h4><i className="fas fa-compass"></i> Навигация</h4>
      <ul className="footer-links">
        <li><Link to="/"><i className="fas fa-angle-right"></i> Главная</Link></li>
        <li><Link to="/search/"><i className="fas fa-angle-right"></i> Поиск</Link></li>
      </ul>
    </div>
  )
}

function Users() {
  return (
    <div className="footer-section">
      <h4><i className="fas fa-user"></i> Пользователям</h4>
      <ul className="footer-links">
        <li><Link to="/profile/"><i className="fas fa-angle-right"></i> Профиль</Link></li>
        <li><Link to="/add-post/"><i className="fas fa-angle-right"></i> Создать статью</Link></li>
        <li><Link to="/subscriptions/"><i className="fas fa-angle-right"></i> Подписки</Link></li>
        <li><Link to="/login/"><i className="fas fa-angle-right"></i> Войти</Link></li>
        <li><Link to="/register/"><i className="fas fa-angle-right"></i> Регистрация</Link></li>
      </ul>
    </div>
  )
}

function Contacts() {
  return (
    <div className="footer-section">
      <h4><i className="fas fa-envelope"></i> Связь</h4>
      <div className="footer-contact-item">
        <i className="fas fa-envelope"></i>
        <a href="mailto:support@flakhub.com">support@flakhub.com</a>
      </div>
      <div className="footer-contact-item">
        <i className="fas fa-map-marker-alt"></i>
        <span>Черкесск, Россия</span>
      </div>
    </div>
  )
}

function FooterBottom() {
  return (
    <div className="footer-bottom">
      <div className="footer-bottom-content">
        <p className="copyright">
          &copy; {new Date().getFullYear()} ФлакХаб. Все права защищены.
        </p>
      </div>
    </div>
  )
}

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-main">
        <BrandSocials />
        <Navigations />
        <Users />
        <Contacts />
      </div>
      <FooterBottom />
    </footer>
  )
}

export default Footer
