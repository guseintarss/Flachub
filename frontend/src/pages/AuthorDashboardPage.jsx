import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { fetchAuthorDashboard } from '../api'
import '../styles/dashboard.css'

const PERIODS = [
  { days: 7, label: '7 дней' },
  { days: 30, label: '30 дней' },
  { days: 90, label: '90 дней' },
]

function formatSeconds(value) {
  const seconds = Number(value) || 0
  if (seconds < 60) return `${seconds} сек`
  const minutes = Math.floor(seconds / 60)
  const rest = seconds % 60
  return rest ? `${minutes} мин ${rest} сек` : `${minutes} мин`
}

function KpiCard({ icon, label, value, hint, tone = 'blue' }) {
  return (
    <div className={`dashboard-kpi tone-${tone}`}>
      <div className="dashboard-kpi-icon"><i className={`fas ${icon}`} /></div>
      <div>
        <div className="dashboard-kpi-value">{value}</div>
        <div className="dashboard-kpi-label">{label}</div>
        {hint && <div className="dashboard-kpi-hint">{hint}</div>}
      </div>
    </div>
  )
}

function ViewsChart({ daily }) {
  const max = Math.max(1, ...daily.map(day => day.views))
  return (
    <div className="dashboard-chart" role="img" aria-label="Просмотры по дням">
      {daily.map((day, i) => (
        <div
          key={day.date}
          className="dashboard-chart-column"
          title={`${day.label}: ${day.views} просмотров, ${day.completed} дочитываний`}
        >
          <div className="dashboard-chart-bars">
            <span className="dashboard-chart-bar views" style={{ height: `${Math.max(3, day.views / max * 100)}%` }} />
            <span className="dashboard-chart-bar completed" style={{ height: `${Math.max(day.completed ? 3 : 0, day.completed / max * 100)}%` }} />
          </div>
          {i % 3 === 1 && <span className="dashboard-chart-label">{day.label}</span>}
        </div>
      ))}
    </div>
  )
}

export default function AuthorDashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [days, setDays] = useState(30)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (authLoading) return
    if (!user) { navigate('/login/'); return }
    let cancelled = false
    fetchAuthorDashboard(days)
      .then(result => { if (!cancelled) setData(result) })
      .catch(() => { if (!cancelled) setError('Не удалось загрузить статистику. Попробуйте обновить страницу.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [days, user, authLoading, navigate])

  function changePeriod(nextDays) {
    if (nextDays === days) return
    setDays(nextDays)
    setLoading(true)
    setError('')
  }

  const kpi = data?.kpi
  const maxSource = useMemo(
    () => Math.max(1, ...(data?.sources || []).map(item => item.count)),
    [data],
  )

  return (
    <main className="page dashboard-page">
      <div className="pg-container">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-eyebrow"><i className="fas fa-chart-line" /> Кабинет автора</p>
            <h1>Дашборд</h1>
            <p className="dashboard-subtitle">
              Как читают ваши статьи: дочитывания, источники трафика и подписчики.
            </p>
          </div>
          <div className="dashboard-periods" role="group" aria-label="Период статистики">
            {PERIODS.map(period => (
              <button
                key={period.days}
                type="button"
                className={days === period.days ? 'is-active' : ''}
                onClick={() => changePeriod(period.days)}
              >
                {period.label}
              </button>
            ))}
          </div>
        </header>

        {loading && (
          <div className="dashboard-loading">
            <i className="fas fa-spinner fa-spin" /> Считаем статистику…
          </div>
        )}

        {error && <div className="dashboard-error" role="alert">{error}</div>}

        {!loading && data && (
          <>
            <section className="dashboard-kpis" aria-label="Ключевые показатели">
              <KpiCard
                icon="fa-eye"
                label="Просмотры"
                value={kpi.views.toLocaleString('ru-RU')}
                hint={`${kpi.readers.toLocaleString('ru-RU')} уникальных читателей`}
              />
              <KpiCard
                icon="fa-book-open-reader"
                label="Дочитывания"
                value={`${kpi.completion_rate}%`}
                hint={`${kpi.completed} из ${kpi.views} просмотров`}
                tone="green"
              />
              <KpiCard
                icon="fa-hourglass-half"
                label="Среднее время чтения"
                value={formatSeconds(kpi.avg_read_seconds)}
                hint="по всем статьям за период"
                tone="violet"
              />
              <KpiCard
                icon="fa-user-plus"
                label="Подписчики"
                value={kpi.subscribers_total.toLocaleString('ru-RU')}
                hint={`+${kpi.subscribers_new} за период`}
                tone="orange"
              />
            </section>

            <div className="dashboard-grid">
              <section className="dashboard-card dashboard-card-chart">
                <div className="dashboard-card-head">
                  <h2>Просмотры и дочитывания</h2>
                  <div className="dashboard-legend">
                    <span><i className="legend-dot views" /> Просмотры</span>
                    <span><i className="legend-dot completed" /> Дочитывания</span>
                  </div>
                </div>
                {data.daily.length ? <ViewsChart daily={data.daily} /> : <p className="dashboard-empty">Пока нет данных.</p>}
              </section>

              <section className="dashboard-card">
                <div className="dashboard-card-head">
                  <h2>Источники трафика</h2>
                </div>
                {data.sources.length === 0 && <p className="dashboard-empty">Пока нет переходов.</p>}
                <div className="dashboard-sources">
                  {data.sources.map(source => (
                    <div key={source.source} className="dashboard-source">
                      <div className="dashboard-source-row">
                        <span>{source.label}</span>
                        <strong>{source.count}</strong>
                      </div>
                      <div className="dashboard-source-track">
                        <span style={{ width: `${Math.max(2, source.count / maxSource * 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <section className="dashboard-card">
              <div className="dashboard-card-head">
                <h2>Статьи за период</h2>
                <Link to="/add-post/" className="btn btn-sm btn-primary">
                  <i className="fas fa-plus" /> Новая статья
                </Link>
              </div>
              {data.top_posts.length === 0 ? (
                <div className="dashboard-empty">
                  <p>Здесь появятся ваши статьи и их статистика.</p>
                  <Link to="/add-post/" className="btn btn-primary">Написать первую статью</Link>
                </div>
              ) : (
                <div className="dashboard-table-wrap">
                  <table className="dashboard-table">
                    <thead>
                      <tr>
                        <th>Статья</th>
                        <th>Просмотры</th>
                        <th>Дочитывания</th>
                        <th>Среднее время</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {data.top_posts.map(post => (
                        <tr key={post.id}>
                          <td>
                            <Link to={`/post/${post.slug}/`} className="dashboard-post-title">
                              {post.title}
                            </Link>
                            {!post.is_published && <span className="dashboard-draft">черновик</span>}
                          </td>
                          <td>{post.views}</td>
                          <td>{post.completion_rate}%</td>
                          <td>{formatSeconds(post.avg_read_seconds)}</td>
                          <td>
                            <Link to={`/edit/${post.slug}/`} className="dashboard-edit" title="Редактировать">
                              <i className="fas fa-pen" />
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  )
}
