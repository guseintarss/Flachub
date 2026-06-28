import Brand from "./Brand"
import BurgerMenu from "./BurgerMenu"
import UserArea from "./Userarea"
import { useBurgerMenu } from "./useBurgerMenu"

const Header = () => {
  useBurgerMenu()

  return (
    <header className="site-header">
      <div className="pg-container header-inner">
        <button id="burger" className="header__burger-menu">
          <span></span><span></span><span></span>
        </button>
        <Brand />
        <div className="menu-overlay" id="menu-overlay"></div>
        <BurgerMenu />
        <UserArea />
      </div>
    </header>
  )
}

export default Header
