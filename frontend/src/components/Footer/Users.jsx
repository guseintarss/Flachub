const Users = () => {
    return (
        <div className="footer-section">
            <h4><i className="fas fa-user"></i> Пользователям</h4>
            <ul className="footer-links">
                <li><a href="{% url 'users:profile' %}"><i className="fas fa-angle-right"></i> Профиль</a></li>
                <li><a href="{% url 'bookmarks' %}"><i className="fas fa-angle-right"></i> Закладки</a></li>
                <li><a href="{% url 'addpage' %}"><i className="fas fa-angle-right"></i> Создать статью</a></li>
                <li><a href="{% url 'subscription_feed' %}"><i className="fas fa-angle-right"></i> Подписки</a></li>
                <li><a href="{% url 'users:login' %}"><i className="fas fa-angle-right"></i> Войти</a></li>
                <li><a href="{% url 'users:register' %}"><i className="fas fa-angle-right"></i> Регистрация</a></li>
            </ul>
        </div>
    )
}


export default Users