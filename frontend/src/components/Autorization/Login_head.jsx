const Login_head = () => {
    return (
        <header className="site-header">
            <div className="pg-container header-inner">
                <a className="brand" href="{% url 'home' %}">ФлакХаб</a>
            </div>
        </header>
    )
}

export default Login_head