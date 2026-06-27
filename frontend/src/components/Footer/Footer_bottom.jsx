const Footer_bottom = () => {
    return (
        <div className="footer-bottom">
            <div className="footer-bottom-content">
                <p className="copyright">
                    &copy; 2026-<span id="currentYear"></span> ФлакХаб. Все права защищены.
                </p>
                <div className="footer-bottom-links">
                    <a href="{% url 'privacy_policy' %}">Конфиденциальность</a>
                    <a href="{% url 'terms_of_use' %}">Соглашение</a>
                </div>
            </div>
        </div>
    )
}


export default Footer_bottom