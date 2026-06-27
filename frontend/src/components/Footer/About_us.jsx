const About_us = () => {
    return (
        <div className="container py-5">
            <div className="row">
                <div className="col-lg-8 mx-auto">
                    <h1>О PageGlow</h1>
                    
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Что такое PageGlow?</h5>
                            <p>PageGlow - это интегрированная платформа для создания и обмена контентом, а также для взаимодействия между фрилансерами и клиентами.</p>
                        </div>
                    </div>

                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Наши возможности</h5>
                            <ul>
                                <li><strong>Сообщество:</strong> Делитесь статьями, идеями и опытом</li>
                                <li><strong>Маркетплейс:</strong> Находите работу или нанимайте специалистов</li>
                                <li><strong>Профили:</strong> Создавайте профессиональный профиль</li>
                                <li><strong>Рейтинги:</strong> Получайте отзывы и строите репутацию</li>
                                <li><strong>Безопасность:</strong> Защищённые платежи и система эскроу</li>
                            </ul>
                        </div>
                    </div>

                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Для кого PageGlow?</h5>
                            <p>PageGlow подходит для:</p>
                            <ul>
                                <li>👨‍💻 Веб-разработчиков</li>
                                <li>🎨 Дизайнеров</li>
                                <li>✍️ Копирайтеров</li>
                                <li>📊 Аналитиков</li>
                                <li>🚀 Предпринимателей</li>
                                <li>🏢 Компаний</li>
                                <li>📱 Мобильных разработчиков</li>
                                <li>🎯 И многих других специалистов</li>
                            </ul>
                        </div>
                    </div>

                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title">Начните прямо сейчас</h5>
                            <p>
                                <a href="{% url 'users:register' %}" className="btn btn-primary">Создать аккаунт</a>
                                <a href="{% url 'marketplace:home' %}" className="btn btn-outline-primary">Перейти на маркетплейс</a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default About_us