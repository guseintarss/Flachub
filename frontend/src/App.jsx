import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    const scroll = () => {
      window.scrollTo(0, 0)
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
    }
    scroll()
    setTimeout(scroll, 50)
  }, [pathname])
  return null
}
import Footer from "./components/Footer/Footer"
import Header from "./components/Header/Header"
import MainPage from "./pages/MainPage"
import PostDetail from "./pages/PostDetail"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import ProfilePage from "./pages/ProfilePage"
import EditProfilePage from "./pages/EditProfilePage"
import { TagPosts, CategoryPosts } from "./pages/PostListPage"
import AddPostPage from "./pages/AddPostPage"

const App = () => {
  return(
    <BrowserRouter>
      <AuthProvider>
        <ScrollToTop />
        <Header />
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/post/:slug/" element={<PostDetail />} />
          <Route path="/tag/:slug/" element={<TagPosts />} />
          <Route path="/category/:slug/" element={<CategoryPosts />} />
          <Route path="/login/" element={<LoginPage />} />
          <Route path="/register/" element={<RegisterPage />} />
          <Route path="/add-post/" element={<AddPostPage />} />
          <Route path="/edit/:slug/" element={<AddPostPage />} />
          <Route path="/profile/" element={<ProfilePage />} />
          <Route path="/profile/edit/" element={<EditProfilePage />} />
          <Route path="/user/:username/" element={<ProfilePage />} />
        </Routes>
        <Footer />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
