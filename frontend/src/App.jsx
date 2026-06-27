import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Footer from "./components/Footer/Footer"
import Header from "./components/Header/Header"
import Main from "./components/Main/Main"
import PostDetail from "./pages/PostDetail"
import { TagPosts, CategoryPosts } from "./pages/PostListPage"

const App = () => {
  return(
    <BrowserRouter>
      <AuthProvider>
        <Header />
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/post/:slug/" element={<PostDetail />} />
          <Route path="/tag/:slug/" element={<TagPosts />} />
          <Route path="/category/:slug/" element={<CategoryPosts />} />
        </Routes>
        <Footer />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
