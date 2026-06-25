const Brand = () => {
    return (
        <a className="brand" href="{% url 'home' %}">
            <span className="brand-text">ФлакХаб</span>
        </a>
    )
}

export default Brand