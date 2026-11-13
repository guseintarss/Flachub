import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import './styles/auth.css'
import './styles/bookmarks.css'
import './styles/footer.css'
import './styles/add-article.css'
import './styles/review.css'
import './styles/mobile.css'
import App from './App.jsx'

async function bootstrap() {
  // Статический демо-стенд: подменяем серверный API до первого запроса приложения.
  // В обычной сборке флаг не выставлен, поэтому демо-код не загружается вовсе.
  if (import.meta.env.VITE_DEMO === 'true') {
    const { installDemo } = await import('./demo/installDemo')
    installDemo()
  } else if (import.meta.env.PROD && 'serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => {})
    })
  }

  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}

bootstrap()
