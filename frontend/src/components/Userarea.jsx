const User_area = () => {
    return (
            <div className="user-area">
                <a className="addbutton" href="" title="Добавить пост">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"></path></svg>
                </a>
                <a id="search" className="search" href="" title="Поиск">
                    <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0,0,256,256" className="header-icon">
                        <g fill="currentColor" fillRule="nonzero" stroke="none" strokeWidth="1" strokeLinecap="butt" strokeLinejoin="miter" strokeMiterlimit="10" strokeDasharray="" strokeDashoffset="0" fontFamily="none" fontWeight="none" fontSize="none" textAnchor="none"><g transform="scale(10.66667,10.66667)"><path d="M22,20l-2,2l-6,-6v-2h2z"></path><path d="M9,16c-3.9,0 -7,-3.1 -7,-7c0,-3.9 3.1,-7 7,-7c3.9,0 7,3.1 7,7c0,3.9 -3.1,7 -7,7zM9,4c-2.8,0 -5,2.2 -5,5c0,2.8 2.2,5 5,5c2.8,0 5,-2.2 5,-5c0,-2.8 -2.2,-5 -5,-5z"></path><path transform="translate(-5.90254,14.24719) rotate(-44.992)" d="M13.7,12.5h1v3.5h-1z"></path></g></g>
                    </svg>
                </a>
                    <div className="notific-cont">
                        <div className="notification-bell" id="notification-bell">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" className="header-icon">
                                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/>
                            </svg>
                            <span className="notification-badge" id="notification-badge">0</span>
                        </div>
                        <div className="notification-dropdown" id="notification-dropdown" >
                            <div className="notification-header">
                                <span>Уведомления</span>
                                <button id="mark-all-read" className="btn btn-sm btn-link">Прочитать все</button>
                            </div>
                            <div className="notification-list" id="notification-list"></div>
                        </div>
                    </div>
                    <a className="login-pill" href="">Войти</a>
            </div>
    )
}

export default User_area