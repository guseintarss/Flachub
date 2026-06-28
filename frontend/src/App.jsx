import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Footer from "./components/Footer/Footer"
import Header from "./components/Header/Header"
import Main from "./components/Main/Main"
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
        <Header />
        <Routes>
          <Route path="/" element={<Main />} />
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
