import { Link } from 'react-router-dom'

const Cat_bookmarks = () => {
    return (
        <Link to="/bookmarks/" className="menu_link">
            <i className="fas fa-bookmark"></i> Закладки
        </Link>
    )
}

export default Cat_bookmarks