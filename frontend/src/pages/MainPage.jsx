import Feed from "../components/Feed/Feed"
import Sidebar from "../components/Sidebar/Sidebar"

const Main = () => {
    return (
        <main className="page">
            <div className="pg-container layout">
                <Feed />
                <aside className="sidebar" aria-label="Боковая панель">
                    <Sidebar />
                </aside>
            </div>
        </main>
    )
}

export default Main
