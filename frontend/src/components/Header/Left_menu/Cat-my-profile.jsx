const My_profile = () => {
    return (
        <a href="{% url 'users:profile' %}" className="menu_link">
            <i className="fas fa-user-circle"></i> Мой профиль
        </a>
    )
}

export default My_profile