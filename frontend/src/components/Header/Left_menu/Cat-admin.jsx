import { Link } from 'react-router-dom'

const Cat_admin = () => {
    return (
        <Link to="/admin/" className="menu_link">
            <i className="fas fa-chart-line"></i> Админка
        </Link>
    )
}

export default Cat_admin