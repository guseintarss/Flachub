import Menu_list from "./Menu-list"

const Top_nav = () => {
    return (
        <nav className="top-nav" aria-label="Основное меню">
            <ul className="menu-list">
                <Menu_list />
            </ul>
        </nav>
    )
}


export default Top_nav