// Справочники для «Разборов»: используются в карточке, на странице поста и в профиле.

export const REVIEW_STATUS_LABELS = {
  open: 'Открыт',
  in_review: 'В работе',
  completed: 'Завершён',
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
