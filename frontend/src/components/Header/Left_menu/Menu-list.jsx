import { useAuth } from '../../../context/AuthContext'
import Cat_home from "./Cat-home"
import Cat_navigations from "./Cat-navigations"
import Category from "./Category"
import Cat_profile from "./Cat-profile"
import My_profile from "./Cat-my-profile"
import Cat_bookmarks from "./Cat-bookmarks"
import Cat_subscriptions from "./Cat-subscription"
import Cat_admin from "./Cat-admin"
import Cat_login from "./Cat-login"

const Menu_list = () => {
    const { user, loading } = useAuth()

    return (
        <>
            <li className="menu-category">
                <Cat_navigations />
                <Cat_home />
            </li>

            <hr className="menu-divider" />

            <Category />

            <hr className="menu-divider" />

            <li className="menu-category">
                {!loading && !user ? (
                    <Cat_login />
                ) : (
                    <>
                        <Cat_profile />
                        <My_profile />
                        <Cat_bookmarks />
                        <Cat_subscriptions />
                        {user?.is_staff && <Cat_admin />}
                    </>
                )}
            </li>
        </>
    )
}

export default Menu_list
