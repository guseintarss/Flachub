import { useEffect, useRef, useState } from 'react'
import { saveReadingSettings } from './readingSettings'

export default function ReadingSettings({ settings, onChange }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const toggleRef = useRef(null)

  useEffect(() => {
    if (!open) return
    function onClick(event) {
      if (ref.current && !ref.current.contains(event.target)) setOpen(false)
    }
    function onKeyDown(event) {
      if (event.key !== 'Escape') return
      setOpen(false)
      toggleRef.current?.focus()
    }
    document.addEventListener('click', onClick)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('click', onClick)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  function update(patch) {
    const next = { ...settings, ...patch }
    onChange(next)
    saveReadingSettings(next)
  }

  return (
    <div className="reading-settings" ref={ref}>
      <button
        type="button"
        ref={toggleRef}
        className={`action-btn reading-settings-toggle${open ? ' is-open' : ''}`}
        onClick={() => setOpen(value => !value)}
        title="Настройки чтения"
        aria-label="Настройки чтения"
        aria-expanded={open}
        aria-controls="reading-settings-popover"
      >
        <span className="reading-settings-aa">Aa</span>
      </button>
      {open && (
        <div
          id="reading-settings-popover"
          className="reading-settings-popover"
          role="dialog"
          aria-label="Настройки чтения"
        >
          <div className="reading-settings-row">
            <span>Размер текста</span>
            <div className="reading-stepper">
              <button
                type="button"
                onClick={() => update({ fontSize: Math.max(16, settings.fontSize - 1) })}
                aria-label="Уменьшить шрифт"
              >A−</button>
              <output aria-live="polite">{settings.fontSize}px</output>
              <button
                type="button"
                onClick={() => update({ fontSize: Math.min(24, settings.fontSize + 1) })}
                aria-label="Увеличить шрифт"
              >A+</button>
            </div>
          </div>
          <div className="reading-settings-row">
            <span>Шрифт</span>
            <div className="reading-segmented">
              <button
                type="button"
                className={settings.font === 'serif' ? 'is-active' : ''}
                aria-pressed={settings.font === 'serif'}
                onClick={() => update({ font: 'serif' })}
              >С засечками</button>
              <button
                type="button"
                className={settings.font === 'sans' ? 'is-active' : ''}
                aria-pressed={settings.font === 'sans'}
                onClick={() => update({ font: 'sans' })}
              >Без засечек</button>
            </div>
          </div>
          <div className="reading-settings-row">
            <span>Ширина</span>
            <div className="reading-segmented">
              <button
                type="button"
                className={settings.width === 'normal' ? 'is-active' : ''}
                aria-pressed={settings.width === 'normal'}
                onClick={() => update({ width: 'normal' })}
              >Удобная</button>
              <button
                type="button"
                className={settings.width === 'wide' ? 'is-active' : ''}
                aria-pressed={settings.width === 'wide'}
                onClick={() => update({ width: 'wide' })}
              >Широкая</button>
            </div>
          </div>
          <p className="reading-settings-hint">Настройки сохраняются в браузере.</p>
        </div>
      )}
    </div>
  )
}
