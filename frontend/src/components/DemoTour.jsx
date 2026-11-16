import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { addComment, fetchPost } from '../api'
import '../styles/demo-tour.css'

const REVIEW_SLUG = 'razbor-koda-validaciya-formy-na-react'
const TOUR_COMMENT = 'Здесь теряется ошибка валидации: форма отправляется даже с пустым email. Предлагаю проверять поле до вызова API.'
const TOUR_REPLY_WAIT = 1600

const STEPS = {
  intro: { index: 0, total: 4, title: 'Тур по ФлакХабу', text: 'Покажем главный сценарий за 90 секунд: разбор кода, построчное замечание и ответ в реальном времени.' },
  article: { index: 1, total: 4, title: 'Разбор кода', text: 'Это не обычная статья: код можно разбирать построчно. Сейчас откроем строку с ошибкой.' },
  comment: { index: 2, total: 4, title: 'Замечание к строке', text: 'Оставляем замечание к строке 7 — с важностью и привязкой к коду.' },
  waiting: { index: 3, total: 4, title: 'Ждём ответ', text: 'Ревьюер получил уведомление. Ответ придёт по WebSocket без перезагрузки страницы.' },
  reply: { index: 3, total: 4, title: 'Ответ в реальном времени', text: 'Готово: ответ появился прямо в ветке, пока вы читали. Дальше — дашборд автора.' },
  dashboard: { index: 4, total: 4, title: 'Дашборд автора', text: 'Дочитывания, источники трафика и подписчики — всё, чтобы понимать, что работает.' },
}

function wait(ms) {
  return new Promise(resolve => window.setTimeout(resolve, ms))
}

export default function DemoTour() {
  const enabled = import.meta.env.VITE_DEMO === 'true'
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(null)
  const [error, setError] = useState('')

  const close = useCallback(() => {
    window.__flachubTourActive = false
    setStep(null)
    setError('')
  }, [])

  const start = useCallback(async () => {
    window.__flachubTourActive = true
    setError('')
    setStep('intro')
  }, [])

  useEffect(() => {
    if (!enabled) return
    function onStart() { start() }
    window.addEventListener('flachub:demo-tour', onStart)
    return () => window.removeEventListener('flachub:demo-tour', onStart)
  }, [enabled, start])

  const begin = useCallback(async () => {
    setError('')
    try {
      if (user?.username !== 'demo') {
        await login('demo', 'demo1234')
      }
      navigate(`/post/${REVIEW_SLUG}/`)
      setStep('article')
    } catch {
      setError('Не удалось войти в демо-аккаунт. Попробуйте ещё раз.')
    }
  }, [user, login, navigate])

  const goToComment = useCallback(() => {
    navigate(`/post/${REVIEW_SLUG}/`)
    setStep('comment')
  }, [navigate])

  // Показываем строку и автоматически оставляем замечание — так тур
  // укладывается в 90 секунд даже если пользователь не печатает.
  useEffect(() => {
    if (step !== 'comment') return
    let cancelled = false
    async function run() {
      await wait(700)
      window.dispatchEvent(new CustomEvent('flachub:tour-line', { detail: { line: 7 } }))
      await wait(TOUR_REPLY_WAIT)
      const post = await fetchPost(REVIEW_SLUG)
      if (cancelled) return
      const comment = await addComment(post.id, TOUR_COMMENT, '', {
        line_start: 7,
        line_end: 7,
        severity: 'major',
      })
      if (cancelled) return
      window.dispatchEvent(new CustomEvent('flachub:tour-comment', { detail: comment }))
      setStep('waiting')
    }
    run().catch(() => {
      if (!cancelled) setStep('reply')
    })
    return () => { cancelled = true }
  }, [step])

  useEffect(() => {
    function onReply(event) {
      if (event.detail) setStep(current => current === 'waiting' ? 'reply' : current)
    }
    window.addEventListener('flachub:demo-reply', onReply)
    return () => window.removeEventListener('flachub:demo-reply', onReply)
  }, [])

  useEffect(() => {
    if (step !== 'article' && step !== 'comment') return
    const target = document.querySelector('.review-code')
    if (!target) return
    target.classList.add('tour-pulse')
    return () => target.classList.remove('tour-pulse')
  }, [step])

  const finish = useCallback(() => {
    close()
    window.dispatchEvent(new CustomEvent('flachub:demo-tour-finished'))
  }, [close])

  if (!enabled || !step) return null

  if (step === 'intro') {
    return (
      <div className="demo-tour-overlay" role="dialog" aria-modal="true" aria-labelledby="demo-tour-title">
        <div className="demo-tour-intro">
          <span className="demo-tour-kicker"><i className="fas fa-play" /> Тур на 90 секунд</span>
          <h2 id="demo-tour-title">ФлакХаб: от статьи до ответа ревьюера</h2>
          <p>Четыре шага, которые показывают главное отличие от обычной ленты:</p>
          <ol className="demo-tour-list">
            <li><strong>Разбор кода.</strong> Открываем статью с кодом и содержанием.</li>
            <li><strong>Замечание к строке.</strong> Оставляем точечный комментарий.</li>
            <li><strong>Ответ в realtime.</strong> Ревьюер отвечает без перезагрузки.</li>
            <li><strong>Дашборд автора.</strong> Смотрим дочитывания и источники.</li>
          </ol>
          {error && <div className="demo-tour-error" role="alert">{error}</div>}
          <div className="demo-tour-actions">
            <button type="button" className="btn btn-primary" onClick={begin}>
              Начать тур <i className="fas fa-arrow-right" />
            </button>
            <button type="button" className="btn btn-secondary" onClick={close}>Позже</button>
          </div>
        </div>
      </div>
    )
  }

  const meta = STEPS[step] || STEPS.article
  return (
    <div className={`demo-tour-panel demo-tour-step-${step}`} role="status" aria-live="polite">
      <div className="demo-tour-progress" aria-hidden="true">
        {Array.from({ length: meta.total }).map((_, index) => (
          <span key={index} className={index < meta.index ? 'is-done' : index === meta.index - 1 ? 'is-active' : ''} />
        ))}
      </div>
      <div className="demo-tour-panel-head">
        <span className="demo-tour-step-label">Шаг {meta.index} из {meta.total}</span>
        <button type="button" className="demo-tour-skip" onClick={finish}>Пропустить</button>
      </div>
      <h3>{meta.title}</h3>
      <p>{meta.text}</p>

      {step === 'article' && (
        <button type="button" className="btn btn-primary" onClick={goToComment}>
          Показать строку <i className="fas fa-arrow-right" />
        </button>
      )}
      {step === 'comment' && (
        <div className="demo-tour-wait"><i className="fas fa-spinner fa-spin" /> Оставляем замечание…</div>
      )}
      {step === 'waiting' && (
        <div className="demo-tour-wait"><i className="fas fa-satellite-dish" /> Ждём ответ по WebSocket…</div>
      )}
      {step === 'reply' && (
        <button type="button" className="btn btn-primary" onClick={() => { navigate('/dashboard/'); setStep('dashboard') }}>
          Открыть дашборд <i className="fas fa-chart-line" />
        </button>
      )}
      {step === 'dashboard' && (
        <button type="button" className="btn btn-primary" onClick={finish}>
          Завершить тур <i className="fas fa-check" />
        </button>
      )}
    </div>
  )
}
