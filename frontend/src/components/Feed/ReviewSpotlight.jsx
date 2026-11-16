import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchReviewSpotlight } from '../../api'
import { formatDeadline, formatMoney } from '../../reviewMeta'

function SpotlightCard({ kicker, icon, post, extra, action }) {
  if (!post) return null
  return (
    <article className={`spotlight-card spotlight-${action}`}>
      <p className="spotlight-kicker"><i className={`fas ${icon}`} /> {kicker}</p>
      <Link to={`/post/${post.slug}/`} className="spotlight-title">{post.title}</Link>
      <p className="spotlight-author">
        <i className="fas fa-user" /> {post.author?.username || 'Автор'}
        {post.code_language && <span className="spotlight-language">{post.code_language}</span>}
      </p>
      {post.review_focus && <p className="spotlight-focus">{post.review_focus}</p>}
      <div className="spotlight-foot">
        <span className="spotlight-extra">{extra}</span>
        <Link to={`/post/${post.slug}/`} className="spotlight-link">
          {action === 'request' ? 'Откликнуться' : 'Читать разбор'} <i className="fas fa-arrow-right" />
        </Link>
      </div>
    </article>
  )
}

function ReviewSpotlight() {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    fetchReviewSpotlight()
      .then(payload => { if (!cancelled) setData(payload) })
      .catch(() => { if (!cancelled) setFailed(true) })
    return () => { cancelled = true }
  }, [])

  if (failed || !data) return null
  const { review_of_day: review, request_of_week: request } = data
  if (!review && !request) return null

  return (
    <section className="review-spotlight" aria-label="Разбор дня и запрос недели">
      <SpotlightCard
        kicker="Разбор дня"
        icon="fa-award"
        post={review}
        action="review"
        extra={review?.review_status === 'completed' ? 'Завершён' : 'Разбор кода'}
      />
      <SpotlightCard
        kicker="Запрос недели"
        icon="fa-bullhorn"
        post={request}
        action="request"
        extra={[
          request?.review_budget != null ? formatMoney(request.review_budget) : null,
          request?.review_deadline ? `до ${formatDeadline(request.review_deadline)}` : null,
          request?.review_offers_count
            ? `${request.review_offers_count} откл.`
            : 'Ждёт ревьюера',
        ].filter(Boolean).join(' · ')}
      />
    </section>
  )
}

export default ReviewSpotlight
