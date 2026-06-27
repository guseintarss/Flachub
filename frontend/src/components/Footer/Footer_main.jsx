import Brand_sotials from "./Brand-sotials"
import Contacts from "./Contact/Contact"
import Navigations from "./Navigations"
import Users from "./Users"

const Footer_main = () => {
    return (
        <div className="footer-main">
            <Brand_sotials />
            <Navigations />                
            <Users />
            <Contacts />
        </div>
    )
}

export default Footer_main