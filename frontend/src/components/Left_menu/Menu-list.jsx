import Cat_admin from "./Cat-admin"
import Cat_bookmarks from "./Cat-bookmarks"
import Cat_profile from "./Cat-profile"
import Cat_subscriptions from "./Cat-subscription"
import Category from "./Category"
import My_profile from "./Cat-my-profile"

const Menu_list = () => {
    return (
        <>
            <Category />
            <li className="menu-category">
                <Cat_profile />
                <My_profile />
                <Cat_bookmarks />
                <Cat_subscriptions />
                <Cat_admin />
            </li>
        </>
    )
}

export default Menu_list