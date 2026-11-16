// Справочники для «Разборов»: используются в карточке, на странице поста и в профиле.

export const REVIEW_STATUS_LABELS = {
  open: 'Открыт',
  in_review: 'В работе',
  completed: 'Завершён',
  cancelled: 'Отменён',
}

export const OFFER_STATUS_LABELS = {
  pending: 'Ожидает выбора',
  selected: 'Выбран',
  declined: 'Отклонён',
  withdrawn: 'Отозван',
}

export const SEVERITY_LABELS = {
  blocker: 'Блокер',
  major: 'Серьёзное',
  minor: 'Незначительное',
  nit: 'Придирка',
}

export const SEVERITY_OPTIONS = [
  { value: '', label: 'Без важности' },
  { value: 'blocker', label: 'Блокер' },
  { value: 'major', label: 'Серьёзное' },
  { value: 'minor', label: 'Незначительное' },
  { value: 'nit', label: 'Придирка' },
]

export const CODE_LANGUAGES = [
  'JavaScript',
  'TypeScript',
  'Python',
  'Go',
  'Rust',
  'Java',
  'Kotlin',
  'Swift',
  'C#',
  'C++',
  'PHP',
  'Ruby',
  'SQL',
  'HTML',
  'CSS',
  'Dart',
]

export function reviewStatusKey(status) {
  return REVIEW_STATUS_LABELS[status] ? status : 'open'
}

export function reviewStatusLabel(status) {
  return REVIEW_STATUS_LABELS[status] || REVIEW_STATUS_LABELS.open
}

export function severityLabel(severity) {
  return SEVERITY_LABELS[severity] || ''
}

export function formatCommentLine(lineStart, lineEnd) {
  if (lineStart == null) return ''
  if (lineEnd != null && lineEnd !== lineStart) {
    return `Строки ${lineStart}–${lineEnd}`
  }
  return `Строка ${lineStart}`
}

export function formatMoney(value) {
  if (value === null || value === undefined || value === '') return 'По договорённости'
  const number = Number(value)
  if (!Number.isFinite(number)) return 'По договорённости'
  return `${number.toLocaleString('ru-RU')} ₽`
}

export function formatDeadline(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

export function toDatetimeLocal(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = number => String(number).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
