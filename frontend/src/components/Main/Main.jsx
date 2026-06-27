import Sidebar from "./Sidebar/Sidebar"

const Main = () => {
    return (
        <main className="page">
            <div className="pg-container layout">
                <div className="content">
                </div>
                <aside className="sidebar" aria-label="Боковая панель">
                    <Sidebar />
                </aside>
            </div>
        </main>
    )
}

export default Main
