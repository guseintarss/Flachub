function BrandSocials() {
  return (
    <div className="footer-brand">
      <a href="/" className="footer-logo">
        <span>ФлакХаб</span>
      </a>
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
        <li><a href="/"><i className="fas fa-angle-right"></i> Главная</a></li>
        <li><a href="/search/"><i className="fas fa-angle-right"></i> Поиск</a></li>
      </ul>
    </div>
  )
}

function Users() {
  return (
    <div className="footer-section">
      <h4><i className="fas fa-user"></i> Пользователям</h4>
      <ul className="footer-links">
        <li><a href="/profile/"><i className="fas fa-angle-right"></i> Профиль</a></li>
        <li><a href="/add-post/"><i className="fas fa-angle-right"></i> Создать статью</a></li>
        <li><a href="/subscriptions/"><i className="fas fa-angle-right"></i> Подписки</a></li>
        <li><a href="/login/"><i className="fas fa-angle-right"></i> Войти</a></li>
        <li><a href="/register/"><i className="fas fa-angle-right"></i> Регистрация</a></li>
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
