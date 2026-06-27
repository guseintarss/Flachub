import { Link } from 'react-router-dom'

const Cat_subscriptions = () => {
    return (
        <Link to="/subscriptions/" className="menu_link">
            <i className="fas fa-pen-fancy"></i> Подписки
        </Link>
    )
}

export default Cat_subscriptions