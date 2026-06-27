const Brand_sotials = () => {
    return (
        <div className="footer-brand">
            <a href="{% url 'home' %}" className="footer-logo">
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


export default Brand_sotials