import { lazy, Suspense, useEffect } from 'react'
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
import SearchPage from "./pages/SearchPage"
import { PostListSkeleton } from './components/Skeleton'
import ChangePasswordPage from "./pages/ChangePasswordPage"
import ForgotPasswordPage from "./pages/ForgotPasswordPage"
import ResetPasswordPage from "./pages/ResetPasswordPage"
import SubscriptionsPage from "./pages/SubscriptionsPage"
import InboxPage from "./pages/InboxPage"
import NotFoundPage from "./pages/NotFoundPage"

const AddPostPage = lazy(() => import('./pages/AddPostPage'))
const ChatPage = lazy(() => import('./pages/ChatPage'))
const AdminPage = lazy(() => import('./pages/AdminPage'))
const AuthorDashboardPage = lazy(() => import('./pages/AuthorDashboardPage'))
const ReviewMarketplacePage = lazy(() => import('./pages/ReviewMarketplacePage'))
import DemoTour from "./components/DemoTour"
import "./styles/redesign.css"

const App = () => {
  return(
    <BrowserRouter>
      <AuthProvider>
        <ScrollToTop />
        <Header />
        <Suspense fallback={<PostListSkeleton />}>
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
            <Route path="/dashboard/" element={<AuthorDashboardPage />} />
            <Route path="/reviews/" element={<ReviewMarketplacePage />} />
            <Route path="/profile/edit/" element={<EditProfilePage />} />
            <Route path="/search/" element={<SearchPage />} />
            <Route path="/user/:username/" element={<ProfilePage />} />
            <Route path="/password/change/" element={<ChangePasswordPage />} />
            <Route path="/forgot-password/" element={<ForgotPasswordPage />} />
            <Route path="/reset-password/:uidb64/:token/" element={<ResetPasswordPage />} />
            <Route path="/subscriptions/" element={<SubscriptionsPage />} />
            <Route path="/inbox/" element={<InboxPage />} />
            <Route path="/chat/:id/" element={<ChatPage />} />
            <Route path="/admin-panel/" element={<AdminPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
        <DemoTour />
        <Footer />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
