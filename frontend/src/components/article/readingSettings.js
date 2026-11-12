export const DEFAULT_READING_SETTINGS = {
  fontSize: 19,
  font: 'serif',
  width: 'normal',
}

export function loadReadingSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem('flachub-reading-settings') || 'null')
    if (!saved) return DEFAULT_READING_SETTINGS
    return {
      fontSize: Math.min(24, Math.max(16, Number(saved.fontSize) || 19)),
      font: saved.font === 'sans' ? 'sans' : 'serif',
      width: saved.width === 'wide' ? 'wide' : 'normal',
    }
  } catch {
    return DEFAULT_READING_SETTINGS
  }
}

export function saveReadingSettings(settings) {
  try {
    localStorage.setItem('flachub-reading-settings', JSON.stringify(settings))
  } catch {
    // localStorage может быть недоступен в приватном режиме.
  }
}
