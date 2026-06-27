const Navigations = () => {
    return (
        <div className="footer-section">
            <h4><i className="fas fa-compass"></i> Навигация</h4>
            <ul className="footer-links">
                <li><a href="{% url 'home' %}"><i className="fas fa-angle-right"></i> Главная</a></li>
                <li><a href="{% url 'search' %}"><i className="fas fa-angle-right"></i> Поиск</a></li>
                <li><a href="{% url 'popular' %}"><i className="fas fa-angle-right"></i> Популярное</a></li>
                <li><a href="{% url 'about' %}"><i className="fas fa-angle-right"></i> О платформе</a></li>
            </ul>
        </div>
    )
}


export default Navigations