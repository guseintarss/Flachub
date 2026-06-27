import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Footer from "./components/Footer/Footer"
import Header from "./components/Header/Header"
import Main from "./components/Main/Main"
import PostDetail from "./pages/PostDetail"

const App = () => {
  return(
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/post/:slug/" element={<PostDetail />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

export default App
