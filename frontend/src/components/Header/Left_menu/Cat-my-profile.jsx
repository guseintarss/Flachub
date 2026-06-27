import { Link } from 'react-router-dom'

const My_profile = () => {
    return (
        <Link to="/profile/" className="menu_link">
            <i className="fas fa-user-circle"></i> Мой профиль
        </Link>
    )
}

export default My_profile