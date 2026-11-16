import { useEffect, useState } from 'react'

function slugifyHeading(text, index) {
  const base = text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
    .trim()
    .replace(/\s+/g, '-')
    .slice(0, 60)
  return `${base || 'section'}-${index + 1}`
}

/**
 * Содержание статьи. Собирается из уже отрендеренного HTML,
 * поэтому работает и для статей, импортированных с Хабра.
 */
export default function ArticleToc({ containerRef, contentKey }) {
  const [items, setItems] = useState([])
  const [activeId, setActiveId] = useState('')
  const [open, setOpen] = useState(() => (
    typeof window === 'undefined' ? true : window.innerWidth >= 900
  ))

  useEffect(() => {
    const root = containerRef.current
    if (!root) return

    const headings = Array.from(root.querySelectorAll('h2, h3'))
      .filter(el => (el.textContent || '').trim().length > 1)
      .map((el, index) => {
        if (!el.id) el.id = slugifyHeading(el.textContent, index)
        return {
          id: el.id,
          text: el.textContent.trim(),
          level: el.tagName === 'H3' ? 3 : 2,
        }
      })

    setItems(headings)
    setActiveId(headings[0]?.id || '')
    if (!headings.length) return

    const observer = new IntersectionObserver(
      entries => {
        const visible = entries
          .filter(entry => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActiveId(visible[0].target.id)
      },
      { rootMargin: '-90px 0px -65% 0px', threshold: [0, 1] },
    )
    headings.forEach(item => {
      const el = document.getElementById(item.id)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [containerRef, contentKey])

  if (items.length < 2) return null

  return (
    <nav className={`article-toc${open ? ' is-open' : ''}`} aria-label="Содержание статьи">
      <button
        type="button"
        className="article-toc-toggle"
        onClick={() => setOpen(value => !value)}
        aria-expanded={open}
        aria-controls="article-toc-list"
      >
        <span><i className="fas fa-list-ul" aria-hidden="true" /> Содержание</span>
        <span className="article-toc-count">{items.length}</span>
        <i className={`fas fa-chevron-${open ? 'up' : 'down'}`} aria-hidden="true" />
      </button>
      {open && (
        <ol className="article-toc-list" id="article-toc-list">
          {items.map(item => (
            <li key={item.id} className={`article-toc-item level-${item.level}`}>
              <a
                href={`#${item.id}`}
                className={activeId === item.id ? 'is-active' : ''}
                aria-current={activeId === item.id ? 'location' : undefined}
                onClick={event => {
                  event.preventDefault()
                  const el = document.getElementById(item.id)
                  if (!el) return
                  const top = el.getBoundingClientRect().top + window.scrollY - 88
                  window.scrollTo({ top, behavior: 'smooth' })
                  history.replaceState(null, '', `#${item.id}`)
                  setActiveId(item.id)
                }}
              >
                {item.text}
              </a>
            </li>
          ))}
        </ol>
      )}
    </nav>
  )
}
