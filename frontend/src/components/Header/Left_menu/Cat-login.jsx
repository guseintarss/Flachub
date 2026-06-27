import { Link } from 'react-router-dom'

const Cat_login = () => {
    return (
        <Link to="/login/" className="menu_link">
            <i className="fas fa-sign-in-alt"></i> Войти
        </Link>
    )
}

export default Cat_login