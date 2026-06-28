import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import './styles/auth.css'
import './styles/feed.css'
import './styles/bookmarks.css'
import './styles/footer.css'
import './styles/add-article.css'
import './styles/mobile.css'
import 'ckeditor5/ckeditor5.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
