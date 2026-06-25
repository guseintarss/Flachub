import BurgerButton from "./Button"
import Brand from "./Brand"
import Top_nav from "./Left_menu/Top-nav"
import User_area from "./Userarea"


const Header = () =>{
    return (
        <>
            <header className="site-header">
                <div className="pg-container header-inner">
                    <BurgerButton />
                    <Brand />
                    <div className="menu-overlay" id="menu-overlay"></div>
                    <Top_nav />
                   <User_area />
                </div>
            </header>
        </>
    )
}

export default Header