import { Link } from 'react-router-dom'

const Cat_home = () => {
    return (
        <Link to="/" className="menu_link">
            <i className="fas fa-home"></i> Главная
        </Link>
    )
}

export default Cat_home