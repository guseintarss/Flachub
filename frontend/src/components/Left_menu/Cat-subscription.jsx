const Cat_subscriptions = () => {
    return (
        <a href="{% url 'subscription_feed' %}" className="menu_link">
            <i className="fas fa-pen-fancy"></i> Подписки
        </a>
    )
}


export default Cat_subscriptions