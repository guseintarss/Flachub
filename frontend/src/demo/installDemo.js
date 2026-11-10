// Браузерный мок Django-API для статического демо-стенда.
//
// Подменяет только запросы демо-контура (/api/mobile/*, /upload/ и
// /ajax/subscribe/). Состояние целиком лежит в localStorage, поэтому стенд
// работает на GitHub Pages без сервера. Все ответы повторяют контракты
// PageGlow/mobile_api: те же поля, пагинация и коды ошибок.
import { createDemoState, DEMO_SEED_VERSION, DEMO_STORAGE_KEY } from './seed'

const LEVELS = [
  { name: 'Новичок', slug: 'novice', min_reputation: 0, icon: '🌱', color: '#10b981' },
  { name: 'Любитель', slug: 'amateur', min_reputation: 100, icon: '🔥', color: '#f59e0b' },
  { name: 'Эксперт', slug: 'expert', min_reputation: 500, icon: '🌳', color: '#2196f3' },
  { name: 'Мастер', slug: 'master', min_reputation: 1500, icon: '⚡', color: '#8b5cf6' },
  { name: 'Гуру', slug: 'guru', min_reputation: 5000, icon: '👑', color: '#ef4444' },
]

const TRANSLIT = {
  а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'e', ж: 'zh',
  з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o',
  п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'kh', ц: 'ts',
  ч: 'ch', ш: 'sh', щ: 'sch', ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu',
  я: 'ya',
}

const liveSockets = new Set()
let state = loadState()
let toastTimer = 0
let quotaWarned = false

// ===== Состояние =====

function loadState() {
  try {
    const raw = window.localStorage.getItem(DEMO_STORAGE_KEY)
    if (raw) {
      const saved = JSON.parse(raw)
      if (saved && saved.version === DEMO_SEED_VERSION) {
        normalizeState(saved)
        return saved
      }
    }
  } catch (error) {
    console.warn('[demo] Не удалось прочитать сохранённое состояние:', error)
  }

  const fresh = JSON.parse(JSON.stringify(createDemoState()))
  normalizeState(fresh)
  try {
    window.localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(fresh))
  } catch {
    // Приватный режим или переполненное хранилище — стенд продолжит работать
    // в памяти до перезагрузки страницы.
  }
  return fresh
}

function normalizeState(data) {
  data.counters = data.counters || {}
  const collections = ['users', 'categories', 'tags', 'posts', 'comments', 'chats', 'messages', 'badges', 'userAchievements', 'notifications']
  for (const key of collections) {
    if (!Array.isArray(data[key])) data[key] = []
  }
  if (!Array.isArray(data.subscriptions)) data.subscriptions = []

  const maxId = list => list.reduce((max, item) => Math.max(max, Number(item.id) || 0), 0)
  const counterKeys = {
    user: 'users', post: 'posts', comment: 'comments', chat: 'chats',
    message: 'messages', notification: 'notifications', badge: 'badges',
    achievement: 'userAchievements',
  }
  for (const [counter, collection] of Object.entries(counterKeys)) {
    data.counters[counter] = Math.max(Number(data.counters[counter]) || 0, maxId(data[collection]))
  }

  for (const user of data.users) {
    user.likes = user.likes || []
    user.show_email = user.show_email ?? true
    user.show_phone = user.show_phone ?? false
    user.show_birth_date = user.show_birth_date ?? false
    user.reputation = Number(user.reputation) || 0
    user.is_active = user.is_active !== false
  }
  for (const post of data.posts) {
    post.likes = post.likes || []
    post.favorites = post.favorites || []
    post.tagIds = post.tagIds || []
    post.views = Number(post.views) || 0
    post.review_status = post.review_status || 'open'
    post.code_snippet = post.code_snippet || ''
    post.code_language = post.code_language || ''
    post.review_focus = post.review_focus || ''
    if (post.reputationAwarded === undefined) post.reputationAwarded = !!post.is_published
  }
  for (const comment of data.comments) {
    comment.likes = comment.likes || []
    comment.severity = comment.severity || ''
    comment.is_active = comment.is_active !== false
    comment.is_resolved = !!comment.is_resolved
    comment.is_accepted = !!comment.is_accepted
  }
  for (const notification of data.notifications) {
    notification.is_read = !!notification.is_read
  }
}

function persist() {
  try {
    window.localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(state))
    return true
  } catch (error) {
    console.warn('[demo] Не удалось сохранить состояние:', error)
    if (!quotaWarned) {
      quotaWarned = true
      showToast('Хранилище браузера заполнено. Сбросьте демо-данные кнопкой слева внизу.')
    }
    return false
  }
}

function nextId(key) {
  const next = (Number(state.counters[key]) || 0) + 1
  state.counters[key] = next
  return next
}

// ===== Общие помощники =====

function httpError(status, payload) {
  const error = new Error(payload?.detail || payload?.error || `HTTP ${status}`)
  error.status = status
  error.payload = payload
  return error
}

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function emptyResponse() {
  return new Response(null, { status: 204 })
}

function parseBool(value, fallback = false) {
  if (value === undefined || value === null || value === '') return fallback
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value !== 0
  return ['1', 'true', 'on', 'yes'].includes(String(value).toLowerCase())
}

function asInt(value, fallback = null) {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) ? parsed : fallback
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function currentUser() {
  if (!state.currentUserId) return null
  const user = state.users.find(item => item.id === Number(state.currentUserId))
  if (!user || !user.is_active) return null
  return user
}

function requireUser() {
  const user = currentUser()
  if (!user) throw httpError(401, { detail: 'Требуется авторизация' })
  return user
}

function requireStaff() {
  const user = requireUser()
  if (!user.is_staff) throw httpError(403, { error: 'Доступ запрещён' })
  return user
}

function requireSuperuser() {
  const user = requireUser()
  if (!user.is_superuser) throw httpError(403, { error: 'Только администратор может выполнить действие' })
  return user
}

function userById(id) {
  return state.users.find(user => user.id === Number(id)) || null
}

function postBySlug(slug) {
  return state.posts.find(post => post.slug === slug) || null
}

function formatRelative(iso) {
  const time = new Date(iso).getTime()
  if (!Number.isFinite(time)) return ''
  const diff = Date.now() - time
  if (diff < 60_000) return 'только что'
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 60) return `${minutes} мин назад`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} ч назад`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} дн назад`
  return new Date(iso).toLocaleDateString('ru-RU')
}

function stripHtml(html) {
  return String(html || '')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ')
    .trim()
}

function readingTime(html) {
  const words = stripHtml(html).split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.round(words / 200))
}

function excerpt(html) {
  const words = stripHtml(html).split(/\s+/).filter(Boolean)
  if (words.length > 40) return `${words.slice(0, 40).join(' ')}...`
  return words.join(' ')
}

function transliterate(value) {
  return Array.from(String(value).toLowerCase())
    .map(char => TRANSLIT[char] ?? char)
    .join('')
}

function uniqueSlug(title) {
  const base = transliterate(title)
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 240) || 'post'
  let slug = base
  let counter = 2
  while (state.posts.some(post => post.slug === slug)) {
    slug = `${base}-${counter}`
    counter += 1
  }
  return slug
}

function lineCount(code) {
  const normalized = String(code || '').replace(/\r\n?/g, '\n')
  if (!normalized) return 0
  const lines = normalized.split('\n')
  if (lines.length > 1 && lines[lines.length - 1] === '') lines.pop()
  return lines.length
}

function localDateKey(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function isPublishedPost(post) {
  return !!post.is_published
}

function publishedPosts() {
  return state.posts.filter(isPublishedPost)
}

function postsByAuthor(authorId, includeDrafts = false) {
  return state.posts.filter(post => post.authorId === Number(authorId) && (includeDrafts || post.is_published))
}

function activeComments(postId) {
  return state.comments.filter(comment => comment.postId === Number(postId) && comment.is_active !== false)
}

function publishedPostCount(userId) {
  return postsByAuthor(userId).length
}

// ===== Парсинг запроса =====

function requestMethod(input, init) {
  return String(init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase()
}

function formToObject(form) {
  const result = {}
  for (const [key, value] of form.entries()) {
    if (key === 'tags' || key === 'tag_ids') {
      if (!Array.isArray(result.tags)) result.tags = []
      result.tags.push(value)
    } else if (key in result) {
      if (!Array.isArray(result[key])) result[key] = [result[key]]
      result[key].push(value)
    } else {
      result[key] = value
    }
  }
  return result
}

async function readBody(init) {
  const body = init?.body
  if (!body) return { data: {}, form: null }

  if (typeof FormData !== 'undefined' && body instanceof FormData) {
    return { data: formToObject(body), form: body }
  }
  if (typeof body === 'string') {
    const text = body.trim()
    if (!text) return { data: {}, form: null }
    try {
      return { data: JSON.parse(text), form: null }
    } catch {
      const params = new URLSearchParams(text)
      const data = {}
      for (const [key, value] of params.entries()) data[key] = value
      return { data, form: null }
    }
  }
  if (typeof URLSearchParams !== 'undefined' && body instanceof URLSearchParams) {
    const data = {}
    for (const [key, value] of body.entries()) data[key] = value
    return { data, form: null }
  }
  return { data: {}, form: null }
}

function tagIdsFrom(value) {
  const source = Array.isArray(value) ? value : value === undefined || value === null || value === '' ? [] : [value]
  return [...new Set(source.map(item => asInt(item)).filter(id => id && state.tags.some(tag => tag.id === id)))]
}

// ===== Изображения =====

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error || new Error('Не удалось прочитать файл'))
    reader.readAsDataURL(file)
  })
}

async function imageFileToDataUrl(file, { maxSize = 1400, quality = 0.8 } = {}) {
  if (!file || typeof file === 'string') return null
  if (!file.type || !file.type.startsWith('image/')) {
    throw httpError(400, { error: 'Поддерживаются только изображения' })
  }
  if (file.type === 'image/svg+xml') {
    throw httpError(400, { error: 'SVG не поддерживается: используйте JPEG, PNG, GIF или WebP' })
  }
  if (file.size > 12 * 1024 * 1024) {
    throw httpError(400, { error: 'Размер файла не должен превышать 12 МБ' })
  }

  let bitmap
  try {
    bitmap = await createImageBitmap(file)
  } catch {
    return readFileAsDataUrl(file)
  }

  const scale = Math.min(1, maxSize / Math.max(bitmap.width, bitmap.height))
  const width = Math.max(1, Math.round(bitmap.width * scale))
  const height = Math.max(1, Math.round(bitmap.height * scale))
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d')
  if (!context) {
    bitmap.close?.()
    return readFileAsDataUrl(file)
  }
  context.drawImage(bitmap, 0, 0, width, height)
  bitmap.close?.()
  return canvas.toDataURL('image/webp', quality)
}

// ===== Сериализация пользователей =====

function levelFor(reputation) {
  const value = Number(reputation) || 0
  let current = null
  for (const level of LEVELS) {
    if (level.min_reputation <= value) current = level
    else break
  }
  return current
}

function nextLevelFor(reputation) {
  const value = Number(reputation) || 0
  return LEVELS.find(level => level.min_reputation > value) || null
}

function levelProgress(reputation) {
  const value = Number(reputation) || 0
  const current = levelFor(value)
  const next = nextLevelFor(value)
  if (!current || !next) return 100
  const range = next.min_reputation - current.min_reputation
  if (range <= 0) return 100
  return clamp(Math.floor(((value - current.min_reputation) / range) * 100), 0, 100)
}

function publicUser(user) {
  if (!user) return null
  const current = currentUser()
  void current
  return {
    id: user.id,
    username: user.username,
    email: user.show_email ? user.email : null,
    first_name: user.first_name,
    last_name: user.last_name,
    avatar: user.avatar || null,
    bio: user.about_me || '',
    is_staff: !!user.is_staff,
    is_superuser: !!user.is_superuser,
    is_active: user.is_active !== false,
    date_joined: user.date_joined,
    banner_gradient_start: user.banner_gradient_start || '#0c6acf',
    banner_gradient_end: user.banner_gradient_end || '#764ba2',
    banner_image: user.banner_image || null,
    phone: user.show_phone && user.phone_namber ? user.phone_namber : null,
    birth_date: user.show_birth_date && user.data_birth ? user.data_birth : null,
    posts_count: publishedPostCount(user.id),
    reputation: Number(user.reputation) || 0,
  }
}

function profileUser(user) {
  const current = currentUser()
  const isOwn = !!current && current.id === user.id
  const isSubscribed = !!current && !isOwn && state.subscriptions.some(
    item => item.subscriberId === current.id && item.authorId === user.id,
  )
  const currentLevel = levelFor(user.reputation)
  const nextLevel = nextLevelFor(user.reputation)

  return {
    id: user.id,
    username: user.username,
    email: user.show_email ? user.email : null,
    first_name: user.first_name,
    last_name: user.last_name,
    avatar: user.avatar || null,
    bio: user.about_me || '',
    is_staff: !!user.is_staff,
    is_superuser: !!user.is_superuser,
    date_joined: user.date_joined,
    banner_gradient_start: user.banner_gradient_start || '#0c6acf',
    banner_gradient_end: user.banner_gradient_end || '#764ba2',
    banner_image: user.banner_image || null,
    followers_count: state.subscriptions.filter(item => item.authorId === user.id).length,
    following_count: state.subscriptions.filter(item => item.subscriberId === user.id).length,
    reputation: Number(user.reputation) || 0,
    current_level: currentLevel ? { ...currentLevel } : null,
    next_level: nextLevel ? { ...nextLevel } : null,
    level_progress: levelProgress(user.reputation),
    show_email: !!user.show_email,
    show_phone: !!user.show_phone,
    show_birth_date: !!user.show_birth_date,
    phone_namber: user.show_phone && user.phone_namber ? user.phone_namber : null,
    data_birth: user.show_birth_date && user.data_birth ? user.data_birth : null,
    is_own_profile: isOwn,
    is_subscribed: isSubscribed,
    published_count: publishedPostCount(user.id),
  }
}

function achievementsFor(userId) {
  return state.userAchievements
    .filter(item => item.userId === Number(userId))
    .map(item => {
      const badge = state.badges.find(candidate => candidate.id === item.badgeId)
      return badge ? {
        id: item.id,
        badge: { ...badge },
        earned_at: item.earned_at,
        reason: item.reason || '',
      } : null
    })
    .filter(Boolean)
}

// ===== Сериализация постов и комментариев =====

function categoryPayload(category) {
  if (!category) return null
  return {
    id: category.id,
    name: category.name,
    slug: category.slug,
    posts_count: state.posts.filter(post => post.categoryId === category.id && post.is_published).length,
  }
}

function tagPayload(tag) {
  return { id: tag.id, tag: tag.tag, slug: tag.slug }
}

function tagWithCountPayload(tag) {
  const postsCount = state.posts.filter(post => post.is_published && post.tagIds.includes(tag.id)).length
  return {
    ...tagPayload(tag),
    name: tag.tag,
    posts_count: postsCount,
    is_popular: postsCount >= 2,
  }
}

function serializePostList(post) {
  const user = currentUser()
  const author = userById(post.authorId)
  const category = state.categories.find(item => item.id === post.categoryId)
  return {
    id: post.id,
    title: post.title,
    slug: post.slug,
    photo: post.photo || null,
    post_type: post.post_type,
    time_create: post.time_create,
    time_update: post.time_update,
    author: publicUser(author),
    category: categoryPayload(category),
    likes_count: post.likes.length,
    favorites_count: post.favorites.length,
    comments_count: activeComments(post.id).length,
    is_liked: !!user && post.likes.includes(user.id),
    is_favorited: !!user && post.favorites.includes(user.id),
    reading_time_minutes: readingTime(post.content),
    views: post.views,
    excerpt: excerpt(post.content),
    code_language: post.code_language || '',
    review_status: post.review_status || 'open',
  }
}

function serializeCommentBase(comment, post) {
  const user = currentUser()
  return {
    id: comment.id,
    author: publicUser(userById(comment.authorId)),
    parent: comment.parentId ?? null,
    content: comment.content,
    created_at: comment.created_at,
    likes_count: comment.likes.length,
    is_liked: !!user && comment.likes.includes(user.id),
    line_start: comment.line_start ?? null,
    line_end: comment.line_end ?? null,
    severity: comment.severity || '',
    is_resolved: !!comment.is_resolved,
    is_accepted: !!comment.is_accepted,
    can_accept: Boolean(
      user
      && post
      && post.post_type === 'review'
      && post.review_status !== 'completed'
      && post.authorId === user.id
      && comment.authorId !== user.id
      && !comment.is_accepted
    ),
    can_resolve: Boolean(
      user
      && comment.line_start != null
      && (comment.authorId === user.id || (post && post.authorId === user.id))
    ),
  }
}

function serializeCommentTree(comment, allComments, post) {
  const replies = allComments
    .filter(item => item.parentId === comment.id)
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
  return {
    ...serializeCommentBase(comment, post),
    replies: replies.map(reply => serializeCommentTree(reply, allComments, post)),
  }
}

function serializeCommentFull(comment) {
  const post = state.posts.find(item => item.id === comment.postId)
  return {
    ...serializeCommentBase(comment, post),
    post: comment.postId,
    updated_at: comment.updated_at || comment.created_at,
    is_edited: !!comment.is_edited,
    replies_count: activeComments(comment.postId).filter(item => item.parentId === comment.id).length,
  }
}

function serializePostDetail(post, { bumpViews = false } = {}) {
  const user = currentUser()
  const author = userById(post.authorId)
  const reviewer = userById(post.reviewerId)
  const comments = activeComments(post.id)
    .filter(comment => !comment.parentId)
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
  const isLiked = !!user && post.likes.includes(user.id)
  const isFavorited = !!user && post.favorites.includes(user.id)
  const isSubscribed = !!user && !!author && state.subscriptions.some(
    item => item.subscriberId === user.id && item.authorId === author.id,
  )
  const isReviewAuthor = !!user && post.authorId === user.id
  const canClaim = !!user
    && post.post_type === 'review'
    && post.is_published
    && (post.review_status || 'open') === 'open'
    && post.authorId !== user.id
  const canRelease = !!user
    && (post.review_status || 'open') === 'in_review'
    && (post.reviewerId === user.id || user.is_staff)

  if (bumpViews && post.is_published && post.authorId !== user?.id) {
    post.views += 1
    persist()
  }

  const similar = publishedPosts()
    .filter(item => item.id !== post.id && (
      item.categoryId === post.categoryId
      || item.tagIds.some(tagId => post.tagIds.includes(tagId))
    ))
    .sort((a, b) => (b.views - a.views) || b.time_create.localeCompare(a.time_create))
    .slice(0, 4)

  return {
    ...serializePostList(post),
    content: post.content || '',
    is_published: !!post.is_published,
    tags: post.tagIds
      .map(tagId => state.tags.find(tag => tag.id === tagId))
      .filter(Boolean)
      .map(tagPayload),
    comments: comments.map(comment => serializeCommentTree(comment, comments, post)),
    is_subscribed: isSubscribed,
    current_user: user ? user.username : null,
    similar_posts: similar.map(serializePostList),
    code_snippet: post.code_snippet || '',
    code_language: post.code_language || '',
    review_focus: post.review_focus || '',
    review_status: post.review_status || 'open',
    reviewer: publicUser(reviewer),
    review_accepted_at: post.review_accepted_at || null,
    is_review_author: isReviewAuthor,
    can_claim_review: canClaim,
    can_release_review: canRelease,
    is_liked: isLiked,
    is_favorited: isFavorited,
  }
}

function serializePostWrite(post) {
  return {
    id: post.id,
    slug: post.slug,
    title: post.title,
    content: post.content || '',
    photo: post.photo || null,
    post_type: post.post_type,
    is_published: !!post.is_published,
    cat: post.categoryId,
    tags: [...post.tagIds],
    code_snippet: post.code_snippet || '',
    code_language: post.code_language || '',
    review_focus: post.review_focus || '',
  }
}

// ===== Списки и пагинация =====

function paginate(items, searchParams, defaultPageSize = 20) {
  const page = Math.max(1, asInt(searchParams.get('page'), 1))
  const pageSize = clamp(asInt(searchParams.get('page_size'), defaultPageSize) || defaultPageSize, 1, 100)
  const count = items.length
  const totalPages = Math.max(1, Math.ceil(count / pageSize))
  const currentPage = Math.min(page, totalPages)
  const start = (currentPage - 1) * pageSize
  const base = `${window.location.pathname}${window.location.search}`
  return {
    count,
    next: currentPage < totalPages ? `${base}?page=${currentPage + 1}` : null,
    previous: currentPage > 1 ? `${base}?page=${currentPage - 1}` : null,
    results: items.slice(start, start + pageSize),
  }
}

function filterPosts(searchParams) {
  const user = currentUser()
  const isPublishedParam = searchParams.get('is_published')
  const authorId = asInt(searchParams.get('author'))
  const tagSlug = searchParams.get('tag')
  const categorySlug = searchParams.get('cat')
  const postType = searchParams.get('post_type')
  const reviewStatus = searchParams.get('review_status')
  const search = (searchParams.get('search') || '').trim().toLowerCase()

  let posts
  if (isPublishedParam === '0' && authorId && user && authorId === user.id) {
    posts = state.posts.filter(post => post.authorId === authorId && !post.is_published)
  } else if (isPublishedParam === '0' && authorId) {
    return []
  } else {
    posts = publishedPosts()
  }

  if (isPublishedParam === '1') posts = posts.filter(post => post.is_published)
  if (authorId) posts = posts.filter(post => post.authorId === authorId)
  if (postType) posts = posts.filter(post => post.post_type === postType)
  if (reviewStatus) posts = posts.filter(post => (post.review_status || 'open') === reviewStatus)
  if (tagSlug) {
    const tag = state.tags.find(item => item.slug === tagSlug)
    posts = tag ? posts.filter(post => post.tagIds.includes(tag.id)) : []
  }
  if (categorySlug) {
    const category = state.categories.find(item => item.slug === categorySlug)
    posts = category ? posts.filter(post => post.categoryId === category.id) : []
  }
  if (search) {
    posts = posts.filter(post => {
      const author = userById(post.authorId)
      return [
        post.title,
        stripHtml(post.content),
        author?.username,
        author?.first_name,
        author?.last_name,
      ].some(value => String(value || '').toLowerCase().includes(search))
    })
  }

  const ordering = searchParams.get('ordering') || '-time_create'
  const direction = ordering.startsWith('-') ? -1 : 1
  const field = ordering.replace(/^-/, '')
  const compare = (a, b) => {
    if (field === 'views') return (a.views - b.views) * direction
    if (field === 'time_update') return a.time_update.localeCompare(b.time_update) * direction
    if (field === 'title') return a.title.localeCompare(b.title, 'ru') * direction
    return a.time_create.localeCompare(b.time_create) * direction
  }
  return posts.slice().sort(compare)
}

function filterUsers(searchParams) {
  const search = (searchParams.get('search') || '').trim().toLowerCase()
  let users = state.users.filter(user => user.is_active !== false)
  if (search) {
    users = users.filter(user => [
      user.username,
      user.first_name,
      user.last_name,
      user.about_me,
    ].some(value => String(value || '').toLowerCase().includes(search)))
  }
  const ordering = searchParams.get('ordering') || '-date_joined'
  const direction = ordering.startsWith('-') ? -1 : 1
  const field = ordering.replace(/^-/, '')
  return users.slice().sort((a, b) => {
    if (field === 'posts_count') return (publishedPostCount(a.id) - publishedPostCount(b.id)) * direction
    if (field === 'username') return a.username.localeCompare(b.username) * direction
    return a.date_joined.localeCompare(b.date_joined) * direction
  })
}

// ===== Уведомления и чаты =====

function unreadNotifications() {
  const user = currentUser()
  if (!user) return 0
  return state.notifications.filter(item => item.recipientId === user.id && !item.is_read).length
}

function broadcastNotificationCount() {
  for (const socket of liveSockets) {
    if (socket.url.includes('/ws/notifications/') && socket.readyState === 1) {
      socket.emit({ type: 'count', count: unreadNotifications() })
    }
  }
}

function createNotification(recipientId, senderId, type, message, { postId = null, chatId = null } = {}) {
  if (!recipientId || recipientId === senderId) return null
  const recipient = userById(recipientId)
  if (!recipient) return null
  const notification = {
    id: nextId('notification'),
    recipientId,
    senderId: senderId || null,
    notification_type: type,
    postId,
    chatId,
    message,
    is_read: false,
    created_at: new Date().toISOString(),
  }
  state.notifications.unshift(notification)
  if (recipientId === currentUser()?.id) broadcastNotificationCount()
  return notification
}

function serializeNotification(notification) {
  const post = state.posts.find(item => item.id === notification.postId)
  return {
    id: notification.id,
    sender: publicUser(userById(notification.senderId)),
    notification_type: notification.notification_type,
    post: notification.postId,
    post_title: post ? post.title : null,
    chat: notification.chatId,
    message: notification.message,
    is_read: !!notification.is_read,
    created_at: formatRelative(notification.created_at),
  }
}

function chatMessages(chatId) {
  return state.messages
    .filter(message => message.chatId === Number(chatId))
    .slice()
    .sort((a, b) => a.created_at.localeCompare(b.created_at))
}

function serializeChat(chat, { detail = false } = {}) {
  const messages = chatMessages(chat.id)
  const last = messages[messages.length - 1] || null
  const user = currentUser()
  const payload = {
    id: chat.id,
    participants: chat.participantIds.map(id => publicUser(userById(id))).filter(Boolean),
    created_at: chat.created_at,
    updated_at: chat.updated_at,
  }
  if (detail) return payload
  return {
    ...payload,
    last_message: {
      text: last ? last.text : null,
      time: last ? last.created_at : null,
      sender_id: last ? last.senderId : null,
    },
    unread_count: user
      ? messages.filter(message => message.senderId !== user.id && !message.is_read).length
      : 0,
  }
}

function serializeMessage(message) {
  return {
    id: message.id,
    sender: publicUser(userById(message.senderId)),
    text: message.text,
    created_at: message.created_at,
    is_read: !!message.is_read,
  }
}

function chatById(id) {
  return state.chats.find(chat => chat.id === Number(id)) || null
}

function ensureChatParticipant(chat, user) {
  if (!chat || !chat.participantIds.includes(user.id)) {
    throw httpError(404, { detail: 'Чат не найден' })
  }
}

// ===== Действия с постами =====

async function createPost(init) {
  const user = requireUser()
  const { data, form } = await readBody(init)
  const title = String(data.title || '').trim()
  if (!title) throw httpError(400, { title: ['Обязательное поле.'] })

  const postType = String(data.post_type || 'post')
  const codeSnippet = String(data.code_snippet || '')
  const codeLanguage = String(data.code_language || '').trim()
  if (postType === 'review') {
    const errors = {}
    if (!codeSnippet.trim()) errors.code_snippet = ['Для разбора нужен код']
    if (!codeLanguage) errors.code_language = ['Укажите язык кода']
    if (Object.keys(errors).length) throw httpError(400, errors)
  }

  const isPublished = parseBool(data.is_published, false)
  const photoFile = form?.get('photo')
  const photo = photoFile && typeof photoFile !== 'string'
    ? await imageFileToDataUrl(photoFile, { maxSize: 1600, quality: 0.8 })
    : null
  const now = new Date().toISOString()
  const post = {
    id: nextId('post'),
    title,
    slug: uniqueSlug(title),
    photo,
    post_type: postType,
    is_published: isPublished,
    authorId: user.id,
    categoryId: asInt(data.cat),
    tagIds: tagIdsFrom(data.tags),
    time_create: now,
    time_update: now,
    views: 0,
    likes: [],
    favorites: [],
    content: String(data.content || ''),
    code_snippet: postType === 'review' ? codeSnippet : '',
    code_language: postType === 'review' ? codeLanguage : '',
    review_focus: postType === 'review' ? String(data.review_focus || '').trim() : '',
    review_status: 'open',
    reviewerId: null,
    review_accepted_at: null,
    reputationAwarded: false,
  }
  if (isPublished) {
    post.reputationAwarded = true
    user.reputation = (Number(user.reputation) || 0) + 10
  }
  state.posts.push(post)
  persist()
  return jsonResponse(serializePostWrite(post), 201)
}

async function updatePost(slug, init) {
  const user = requireUser()
  const post = postBySlug(slug)
  if (!post) throw httpError(404, { detail: 'Не найдено' })
  if (post.authorId !== user.id) throw httpError(403, { detail: 'У вас нет прав для изменения этого поста' })

  const { data, form } = await readBody(init)
  const nextType = data.post_type !== undefined ? String(data.post_type) : post.post_type
  const nextSnippet = data.code_snippet !== undefined ? String(data.code_snippet) : post.code_snippet
  const nextLanguage = data.code_language !== undefined ? String(data.code_language).trim() : post.code_language
  if (nextType === 'review') {
    const errors = {}
    if (!nextSnippet.trim()) errors.code_snippet = ['Для разбора нужен код']
    if (!nextLanguage) errors.code_language = ['Укажите язык кода']
    if (Object.keys(errors).length) throw httpError(400, errors)
  }

  if (data.title !== undefined) post.title = String(data.title).trim()
  if (data.content !== undefined) post.content = String(data.content)
  if (data.post_type !== undefined) post.post_type = nextType
  if (data.cat !== undefined) post.categoryId = asInt(data.cat)
  if (data.tags !== undefined) post.tagIds = tagIdsFrom(data.tags)
  if (data.code_snippet !== undefined) post.code_snippet = nextSnippet
  if (data.code_language !== undefined) post.code_language = nextLanguage
  if (data.review_focus !== undefined) post.review_focus = String(data.review_focus || '').trim()

  if (nextType === 'review') {
    post.code_snippet = nextSnippet
    post.code_language = nextLanguage
  } else if (post.post_type === 'review') {
    post.code_snippet = ''
    post.code_language = ''
    post.review_focus = ''
    post.reviewerId = null
    post.review_status = 'open'
    post.review_accepted_at = null
  }

  const photoFile = form?.get('photo')
  if (photoFile && typeof photoFile !== 'string') {
    post.photo = await imageFileToDataUrl(photoFile, { maxSize: 1600, quality: 0.8 })
  } else if (parseBool(data.photo_clear, false)) {
    post.photo = null
  }

  if (data.is_published !== undefined) {
    const shouldPublish = parseBool(data.is_published, post.is_published)
    if (shouldPublish && !post.is_published && !post.reputationAwarded) {
      post.reputationAwarded = true
      user.reputation = (Number(user.reputation) || 0) + 10
    }
    post.is_published = shouldPublish
  }
  post.time_update = new Date().toISOString()
  persist()
  return jsonResponse(serializePostWrite(post))
}

function deletePost(slug) {
  const user = requireUser()
  const post = postBySlug(slug)
  if (!post) throw httpError(404, { detail: 'Не найдено' })
  if (post.authorId !== user.id && !user.is_staff) {
    throw httpError(403, { detail: 'У вас нет прав для удаления этого поста' })
  }
  const author = userById(post.authorId)
  if (author && post.reputationAwarded) {
    author.reputation = Math.max(0, (Number(author.reputation) || 0) - 10)
  }
  state.posts = state.posts.filter(item => item.id !== post.id)
  state.comments = state.comments.filter(item => item.postId !== post.id)
  state.notifications = state.notifications.filter(item => item.postId !== post.id)
  persist()
  return emptyResponse()
}

function claimReview(slug) {
  const user = requireUser()
  const post = postBySlug(slug)
  if (!post || post.post_type !== 'review' || !post.is_published) {
    throw httpError(404, { detail: 'Разбор не найден' })
  }
  if (post.authorId === user.id) throw httpError(403, { detail: 'Автор не может взять свой разбор' })
  if ((post.review_status || 'open') !== 'open') {
    throw httpError(400, { detail: 'Разбор уже взят или завершён' })
  }
  post.reviewerId = user.id
  post.review_status = 'in_review'
  createNotification(
    post.authorId,
    user.id,
    'review_claimed',
    `${user.username} взял ваш разбор «${post.title.slice(0, 100)}»`,
    { postId: post.id },
  )
  persist()
  return jsonResponse(serializePostDetail(post))
}

function releaseReview(slug) {
  const user = requireUser()
  const post = postBySlug(slug)
  if (!post) throw httpError(404, { detail: 'Не найдено' })
  if (post.reviewerId !== user.id && !user.is_staff) {
    throw httpError(403, { detail: 'Освободить разбор может ревьюер или модератор' })
  }
  if ((post.review_status || 'open') !== 'in_review') {
    throw httpError(400, { detail: 'Разбор не в работе' })
  }
  post.reviewerId = null
  post.review_status = 'open'
  persist()
  return jsonResponse(serializePostDetail(post))
}

// ===== Действия с комментариями =====

function createComment(init) {
  const user = requireUser()
  return readBody(init).then(({ data }) => {
    const postId = asInt(data.post_id)
    const post = state.posts.find(item => item.id === postId)
    if (!post) throw httpError(404, { detail: 'Пост не найден' })
    if (!post.is_published && post.authorId !== user.id) {
      throw httpError(403, { detail: 'Нельзя комментировать чужой черновик' })
    }

    const content = String(data.content || '').trim()
    if (!content) throw httpError(400, { content: ['Комментарий не может быть пустым'] })

    let parentId = data.parent ? asInt(data.parent) : null
    if (parentId) {
      const parent = state.comments.find(item => item.id === parentId && item.is_active !== false)
      if (!parent || parent.postId !== post.id) {
        throw httpError(400, { parent: ['Родительский комментарий относится к другому посту'] })
      }
    } else {
      parentId = null
    }

    let lineStart = data.line_start !== undefined && data.line_start !== '' ? asInt(data.line_start) : null
    let lineEnd = data.line_end !== undefined && data.line_end !== '' ? asInt(data.line_end) : null
    if (lineStart !== null) {
      if (post.post_type !== 'review') {
        throw httpError(400, { line_start: ['Строчные замечания доступны только для разборов'] })
      }
      const total = lineCount(post.code_snippet)
      const errors = {}
      if (lineStart < 1 || lineStart > total) {
        errors.line_start = [`Строка должна быть в диапазоне 1–${total}`]
      }
      if (lineEnd === null) {
        lineEnd = lineStart
      } else if (lineEnd < lineStart) {
        errors.line_end = ['Конец строки не может быть раньше начала']
      } else if (lineEnd > total) {
        errors.line_end = [`Строка должна быть в диапазоне 1–${total}`]
      }
      if (Object.keys(errors).length) throw httpError(400, errors)
    } else if (lineEnd !== null) {
      throw httpError(400, { line_end: ['Нельзя указать конец строки без начала'] })
    }

    const severity = ['blocker', 'major', 'minor', 'nit'].includes(data.severity)
      ? data.severity
      : ''
    const now = new Date().toISOString()
    const comment = {
      id: nextId('comment'),
      postId: post.id,
      authorId: user.id,
      parentId,
      content,
      created_at: now,
      updated_at: now,
      is_edited: false,
      is_active: true,
      likes: [],
      line_start: lineStart,
      line_end: lineStart === null ? null : lineEnd,
      severity,
      is_resolved: false,
      is_accepted: false,
    }
    state.comments.push(comment)
    createNotification(
      post.authorId,
      user.id,
      'comment',
      `${user.username} оставил комментарий к «${post.title.slice(0, 100)}»`,
      { postId: post.id },
    )
    persist()
    return jsonResponse(serializeCommentFull(comment), 201)
  })
}

function updateComment(commentId, init) {
  const user = requireUser()
  const comment = state.comments.find(item => item.id === Number(commentId) && item.is_active !== false)
  if (!comment) throw httpError(404, { detail: 'Не найдено' })
  if (comment.authorId !== user.id) throw httpError(403, { detail: 'У вас нет прав для изменения комментария' })
  return readBody(init).then(({ data }) => {
    if (data.content !== undefined) {
      const content = String(data.content).trim()
      if (!content) throw httpError(400, { content: ['Комментарий не может быть пустым'] })
      comment.content = content
    }
    comment.is_edited = true
    comment.updated_at = new Date().toISOString()
    persist()
    return jsonResponse(serializeCommentFull(comment))
  })
}

function deleteComment(commentId) {
  const user = requireUser()
  const comment = state.comments.find(item => item.id === Number(commentId) && item.is_active !== false)
  if (!comment) throw httpError(404, { detail: 'Не найдено' })
  if (comment.authorId !== user.id && !user.is_staff) {
    throw httpError(403, { detail: 'У вас нет прав для удаления этого комментария' })
  }
  comment.is_active = false
  persist()
  return emptyResponse()
}

function acceptComment(commentId) {
  const user = requireUser()
  const comment = state.comments.find(item => item.id === Number(commentId) && item.is_active !== false)
  if (!comment) throw httpError(404, { detail: 'Не найдено' })
  const post = state.posts.find(item => item.id === comment.postId)
  if (!post || post.post_type !== 'review') {
    throw httpError(400, { detail: 'Принять можно только комментарий к разбору' })
  }
  if (post.authorId !== user.id) throw httpError(403, { detail: 'Принять разбор может только автор публикации' })
  if (comment.authorId === user.id) throw httpError(400, { detail: 'Нельзя принять собственный комментарий' })
  if (comment.is_accepted) throw httpError(400, { detail: 'Комментарий уже принят' })
  if (post.review_status === 'completed') throw httpError(400, { detail: 'Разбор уже завершён' })

  comment.is_accepted = true
  post.review_status = 'completed'
  post.review_accepted_at = new Date().toISOString()
  if (post.reviewerId == null) post.reviewerId = comment.authorId

  const author = userById(comment.authorId)
  if (author) author.reputation = (Number(author.reputation) || 0) + 15

  createNotification(
    comment.authorId,
    user.id,
    'review_accepted',
    `Ваш разбор принят: «${post.title.slice(0, 100)}»`,
    { postId: post.id },
  )
  persist()
  return jsonResponse(serializeCommentFull(comment))
}

function resolveComment(commentId) {
  const user = requireUser()
  const comment = state.comments.find(item => item.id === Number(commentId) && item.is_active !== false)
  if (!comment) throw httpError(404, { detail: 'Не найдено' })
  if (comment.line_start == null) {
    throw httpError(400, { detail: 'Решить можно только строчное замечание' })
  }
  const post = state.posts.find(item => item.id === comment.postId)
  const canResolve = comment.authorId === user.id
    || (post && post.authorId === user.id)
    || user.is_staff
  if (!canResolve) {
    throw httpError(403, { detail: 'Решить замечание может автор комментария, автор разбора или модератор' })
  }
  comment.is_resolved = !comment.is_resolved
  persist()
  return jsonResponse(serializeCommentFull(comment))
}

// ===== Роутер демо-API =====

async function handleRequest(pathname, searchParams, init, input) {
  const method = requestMethod(input, init)
  const user = currentUser()

  // Auth и текущий пользователь
  if (pathname === '/api/mobile/me/' && method === 'GET') {
    if (!user) return jsonResponse(null)
    return jsonResponse({ ...profileUser(user), achievements: achievementsFor(user.id) })
  }
  if (pathname === '/api/mobile/me/' && method === 'PATCH') {
    return updateCurrentUser(init)
  }
  if (pathname === '/api/mobile/auth/login/' && method === 'POST') {
    return login(init)
  }
  if (pathname === '/api/mobile/auth/logout/' && method === 'POST') {
    state.currentUserId = null
    persist()
    return jsonResponse({ status: 'ok' })
  }
  if (pathname === '/api/mobile/auth/register/' && method === 'POST') {
    return register(init)
  }
  if (pathname === '/api/mobile/auth/password-reset/' && method === 'POST') {
    return requestPasswordReset(init)
  }
  if (pathname === '/api/mobile/auth/password-reset/confirm/' && method === 'POST') {
    return confirmPasswordReset(init)
  }
  if (pathname === '/api/mobile/password/change/' && method === 'POST') {
    return changePassword(init)
  }

  // Посты
  if (pathname === '/api/mobile/posts/' && method === 'GET') {
    return jsonResponse(paginate(filterPosts(searchParams).map(serializePostList), searchParams))
  }
  if (pathname === '/api/mobile/posts/' && method === 'POST') {
    return createPost(init)
  }

  let match = pathname.match(/^\/api\/mobile\/posts\/([^/]+)\/(claim_review|release_review)\/$/)
  if (match) {
    if (method !== 'POST') throw httpError(405, { detail: 'Метод не поддерживается' })
    const slug = decodeURIComponent(match[1])
    return match[2] === 'claim_review' ? claimReview(slug) : releaseReview(slug)
  }

  match = pathname.match(/^\/api\/mobile\/posts\/([^/]+)\/$/)
  if (match) {
    const slug = decodeURIComponent(match[1])
    if (method === 'GET') {
      const post = postBySlug(slug)
      if (!post || (!post.is_published && post.authorId !== user?.id)) {
        throw httpError(404, { detail: 'Не найдено' })
      }
      return jsonResponse(serializePostDetail(post, { bumpViews: true }))
    }
    if (method === 'PATCH' || method === 'PUT') return updatePost(slug, init)
    if (method === 'DELETE') return deletePost(slug)
  }

  // Комментарии
  if (pathname === '/api/mobile/comments/' && method === 'GET') {
    const postId = asInt(searchParams.get('post_id'))
    let comments = state.comments.filter(comment => comment.is_active !== false)
    if (postId) comments = comments.filter(comment => comment.postId === postId)
    comments = comments.slice().sort((a, b) => b.created_at.localeCompare(a.created_at))
    return jsonResponse(paginate(comments.map(serializeCommentFull), searchParams))
  }
  if (pathname === '/api/mobile/comments/' && method === 'POST') {
    return createComment(init)
  }

  match = pathname.match(/^\/api\/mobile\/comments\/(\d+)\/(accept|resolve)\/$/)
  if (match) {
    if (method !== 'POST') throw httpError(405, { detail: 'Метод не поддерживается' })
    return match[2] === 'accept' ? acceptComment(match[1]) : resolveComment(match[1])
  }

  match = pathname.match(/^\/api\/mobile\/comments\/(\d+)\/$/)
  if (match) {
    if (method === 'PATCH' || method === 'PUT') return updateComment(match[1], init)
    if (method === 'DELETE') return deleteComment(match[1])
  }

  match = pathname.match(/^\/api\/mobile\/comment-actions\/(\d+)\/toggle_like\/$/)
  if (match && method === 'POST') {
    const comment = state.comments.find(item => item.id === Number(match[1]) && item.is_active !== false)
    if (!comment) throw httpError(404, { detail: 'Не найдено' })
    const actor = requireUser()
    if (comment.likes.includes(actor.id)) {
      comment.likes = comment.likes.filter(id => id !== actor.id)
    } else {
      comment.likes.push(actor.id)
    }
    persist()
    return jsonResponse({ liked: comment.likes.includes(actor.id), likes_count: comment.likes.length })
  }

  // Лайки и избранное постов
  match = pathname.match(/^\/api\/mobile\/post-actions\/(\d+)\/(toggle_like|toggle_favorite)\/$/)
  if (match && method === 'POST') {
    const actor = requireUser()
    const post = state.posts.find(item => item.id === Number(match[1]) && item.is_published)
    if (!post) throw httpError(404, { detail: 'Не найдено' })
    if (match[2] === 'toggle_like') {
      if (post.likes.includes(actor.id)) post.likes = post.likes.filter(id => id !== actor.id)
      else post.likes.push(actor.id)
      persist()
      return jsonResponse({ liked: post.likes.includes(actor.id), likes_count: post.likes.length })
    }
    if (post.favorites.includes(actor.id)) post.favorites = post.favorites.filter(id => id !== actor.id)
    else post.favorites.push(actor.id)
    persist()
    return jsonResponse({ favorited: post.favorites.includes(actor.id), favorites_count: post.favorites.length })
  }

  // Справочники
  if (pathname === '/api/mobile/categories/' && method === 'GET') {
    const categories = state.categories.map(categoryPayload)
    return jsonResponse(paginate(categories, searchParams))
  }
  if (pathname === '/api/mobile/tags/' && method === 'GET') {
    const tags = state.tags.map(tagWithCountPayload)
    return jsonResponse(paginate(tags, searchParams))
  }
  if (pathname === '/api/mobile/sidebar/' && method === 'GET') {
    const recent = publishedPosts()
      .slice()
      .sort((a, b) => b.time_create.localeCompare(a.time_create))
      .slice(0, 5)
      .map(post => ({
        id: post.id,
        title: post.title,
        slug: post.slug,
        photo: post.photo || null,
        author: userById(post.authorId)?.username || 'Аноним',
        time_create: post.time_create,
        views: post.views,
        likes_count: post.likes.length,
      }))
    const categories = state.categories
      .map(categoryPayload)
      .filter(category => category.posts_count > 0)
      .sort((a, b) => b.posts_count - a.posts_count)
      .slice(0, 10)
    const tags = state.tags
      .map(tagWithCountPayload)
      .filter(tag => tag.posts_count > 0)
      .sort((a, b) => b.posts_count - a.posts_count)
      .slice(0, 15)
    return jsonResponse({
      recent_posts: recent,
      categories,
      tags: tags.map(tag => ({ id: tag.id, name: tag.name, slug: tag.slug, posts_count: tag.posts_count })),
      stats: {
        total_posts: state.posts.length,
        total_users: state.users.filter(item => item.is_active !== false).length,
        total_comments: state.comments.length,
      },
    })
  }

  // Подписки
  if (pathname === '/ajax/subscribe/' && method === 'POST') {
    const actor = requireUser()
    const { data } = await readBody(init)
    const authorId = asInt(data.author_id)
    if (!authorId) throw httpError(400, { error: 'author_id is required' })
    const target = userById(authorId)
    if (!target) throw httpError(404, { error: 'User not found' })
    if (target.id === actor.id) throw httpError(400, { error: 'Cannot subscribe to yourself' })
    const index = state.subscriptions.findIndex(
      item => item.subscriberId === actor.id && item.authorId === target.id,
    )
    let subscribed
    if (index >= 0) {
      state.subscriptions.splice(index, 1)
      subscribed = false
    } else {
      state.subscriptions.push({ subscriberId: actor.id, authorId: target.id })
      subscribed = true
      createNotification(
        target.id,
        actor.id,
        'follow',
        `${actor.username} подписался на ваши обновления`,
      )
    }
    persist()
    return jsonResponse({
      success: true,
      subscribed,
      subscribers_count: state.subscriptions.filter(item => item.authorId === target.id).length,
    })
  }
  if (pathname === '/api/mobile/subscriptions/feed/' && method === 'GET') {
    const actor = requireUser()
    const authors = state.users.filter(candidate => (
      candidate.is_active !== false
      && state.subscriptions.some(item => item.subscriberId === actor.id && item.authorId === candidate.id)
    ))
    const authorsData = authors.map(author => {
      const latest = postsByAuthor(author.id)
        .slice()
        .sort((a, b) => b.time_create.localeCompare(a.time_create))[0]
      return {
        id: author.id,
        username: author.username,
        first_name: author.first_name,
        last_name: author.last_name,
        avatar: author.avatar || null,
        bio: author.about_me || '',
        posts_count: publishedPostCount(author.id),
        last_post: latest ? serializePostList(latest) : null,
      }
    })
    const authorIds = authors.map(author => author.id)
    const posts = publishedPosts()
      .filter(post => authorIds.includes(post.authorId))
      .sort((a, b) => b.time_create.localeCompare(a.time_create))
    const page = Math.max(1, asInt(searchParams.get('page'), 1))
    const pageSize = 20
    const totalPages = Math.max(1, Math.ceil(posts.length / pageSize))
    const currentPage = Math.min(page, totalPages)
    const pagePosts = posts.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    return jsonResponse({
      authors: authorsData,
      posts: pagePosts.map(serializePostList),
      count: posts.length,
      total_pages: totalPages,
    })
  }

  // Пользователи
  if (pathname === '/api/mobile/users/' && method === 'GET') {
    const users = filterUsers(searchParams).map(publicUser)
    return jsonResponse(paginate(users, searchParams))
  }

  match = pathname.match(/^\/api\/mobile\/users\/by-username\/([^/]+)\/$/)
  if (match && method === 'GET') {
    const username = decodeURIComponent(match[1])
    const target = state.users.find(item => item.username === username && item.is_active !== false)
    if (!target) throw httpError(404, { detail: 'Не найдено' })
    return jsonResponse({ ...profileUser(target), achievements: achievementsFor(target.id) })
  }

  match = pathname.match(/^\/api\/mobile\/users\/(\d+)\/(stats|favorites|reviews|posts|achievements|profile)\/$/)
  if (match && method === 'GET') {
    const target = userById(match[1])
    if (!target || target.is_active === false) throw httpError(404, { detail: 'Не найдено' })
    return userAction(target, match[2], searchParams)
  }

  match = pathname.match(/^\/api\/mobile\/users\/(\d+)\/$/)
  if (match && method === 'GET') {
    const target = userById(match[1])
    if (!target || target.is_active === false) throw httpError(404, { detail: 'Не найдено' })
    return jsonResponse({ ...profileUser(target), achievements: achievementsFor(target.id) })
  }

  // Уведомления
  if (pathname === '/api/mobile/notifications/' && method === 'GET') {
    const actor = requireUser()
    const items = state.notifications
      .filter(item => item.recipientId === actor.id)
      .slice()
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .map(serializeNotification)
    return jsonResponse(paginate(items, searchParams))
  }
  if (pathname === '/api/mobile/notifications/unread_count/' && method === 'GET') {
    requireUser()
    return jsonResponse({ unread_count: unreadNotifications() })
  }
  if (pathname === '/api/mobile/notifications/mark_all_read/' && method === 'POST') {
    const actor = requireUser()
    state.notifications
      .filter(item => item.recipientId === actor.id && !item.is_read)
      .forEach(item => { item.is_read = true })
    persist()
    broadcastNotificationCount()
    return jsonResponse({ status: 'all marked as read' })
  }
  match = pathname.match(/^\/api\/mobile\/notifications\/(\d+)\/mark_read\/$/)
  if (match && method === 'POST') {
    const actor = requireUser()
    const notification = state.notifications.find(
      item => item.id === Number(match[1]) && item.recipientId === actor.id,
    )
    if (!notification) throw httpError(404, { detail: 'Не найдено' })
    notification.is_read = true
    persist()
    broadcastNotificationCount()
    return jsonResponse({ status: 'marked as read' })
  }

  // Чаты
  if (pathname === '/api/mobile/chats/' && method === 'GET') {
    const actor = requireUser()
    const chats = state.chats
      .filter(chat => chat.participantIds.includes(actor.id))
      .slice()
      .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
      .map(chat => serializeChat(chat))
    return jsonResponse(chats)
  }
  if (pathname === '/api/mobile/chats/' && method === 'POST') {
    const actor = requireUser()
    const { data } = await readBody(init)
    const participantId = asInt(data.participant_id)
    const participant = userById(participantId)
    if (!participant || participant.is_active === false) {
      throw httpError(400, { participant_id: ['Пользователь не найден'] })
    }
    if (participant.id === actor.id) throw httpError(400, { error: 'Нельзя создать чат с самим собой' })
    const existing = state.chats.find(chat => (
      chat.participantIds.includes(actor.id) && chat.participantIds.includes(participant.id)
    ))
    if (existing) return jsonResponse(serializeChat(existing, { detail: true }))
    const now = new Date().toISOString()
    const chat = {
      id: nextId('chat'),
      participantIds: [actor.id, participant.id],
      created_at: now,
      updated_at: now,
    }
    state.chats.push(chat)
    persist()
    return jsonResponse(serializeChat(chat, { detail: true }), 201)
  }

  match = pathname.match(/^\/api\/mobile\/chats\/(\d+)\/messages\/$/)
  if (match && method === 'GET') {
    const actor = requireUser()
    const chat = chatById(match[1])
    ensureChatParticipant(chat, actor)
    let changed = false
    for (const message of state.messages) {
      if (message.chatId === chat.id && message.senderId !== actor.id && !message.is_read) {
        message.is_read = true
        changed = true
      }
    }
    if (changed) persist()
    return jsonResponse(chatMessages(chat.id).map(serializeMessage))
  }

  match = pathname.match(/^\/api\/mobile\/chats\/(\d+)\/send\/$/)
  if (match && method === 'POST') {
    const actor = requireUser()
    const chat = chatById(match[1])
    ensureChatParticipant(chat, actor)
    const { data } = await readBody(init)
    const text = String(data.text || '').trim()
    if (!text) throw httpError(400, { text: ['Сообщение не может быть пустым'] })

    const recent = state.messages.find(message => (
      message.chatId === chat.id
      && message.senderId === actor.id
      && message.text === text
      && Date.now() - new Date(message.created_at).getTime() < 5000
    ))
    if (recent) return jsonResponse(serializeMessage(recent))

    const now = new Date().toISOString()
    const message = {
      id: nextId('message'),
      chatId: chat.id,
      senderId: actor.id,
      text,
      created_at: now,
      is_read: false,
    }
    state.messages.push(message)
    chat.updated_at = now
    for (const participantId of chat.participantIds) {
      if (participantId !== actor.id) {
        createNotification(
          participantId,
          actor.id,
          'chat_message',
          `${actor.username}: «${text.slice(0, 100)}»`,
          { chatId: chat.id },
        )
      }
    }
    persist()
    return jsonResponse(serializeMessage(message), 201)
  }

  match = pathname.match(/^\/api\/mobile\/chats\/(\d+)\/mark_read\/$/)
  if (match && (method === 'GET' || method === 'POST')) {
    const actor = requireUser()
    const chat = chatById(match[1])
    ensureChatParticipant(chat, actor)
    let marked = 0
    for (const message of state.messages) {
      if (message.chatId === chat.id && message.senderId !== actor.id && !message.is_read) {
        message.is_read = true
        marked += 1
      }
    }
    if (marked) persist()
    return jsonResponse({ marked_read: marked })
  }

  match = pathname.match(/^\/api\/mobile\/chats\/(\d+)\/$/)
  if (match && method === 'GET') {
    const actor = requireUser()
    const chat = chatById(match[1])
    ensureChatParticipant(chat, actor)
    return jsonResponse(serializeChat(chat, { detail: true }))
  }

  // Админка
  if (pathname === '/api/mobile/admin/stats/' && method === 'GET') {
    requireStaff()
    return jsonResponse(adminStats())
  }
  if (pathname === '/api/mobile/admin/users/' && method === 'GET') {
    requireStaff()
    return jsonResponse(adminUsers(searchParams))
  }
  match = pathname.match(/^\/api\/mobile\/admin\/users\/(\d+)\/role\/$/)
  if (match && method === 'POST') {
    return adminChangeRole(match[1], init)
  }
  match = pathname.match(/^\/api\/mobile\/admin\/users\/(\d+)\/ban\/$/)
  if (match && method === 'POST') {
    return adminToggleBan(match[1])
  }

  // Загрузка изображений
  if ((pathname === '/upload/' || pathname === '/api/mobile/media/upload_image/') && method === 'POST') {
    requireUser()
    const { form } = await readBody(init)
    const file = form?.get('upload') || form?.get('image')
    if (!file || typeof file === 'string') {
      throw httpError(400, { error: 'Изображение не предоставлено' })
    }
    const dataUrl = await imageFileToDataUrl(file, { maxSize: 1600, quality: 0.8 })
    return jsonResponse({ url: dataUrl, filename: `demo-${Date.now()}.webp` })
  }

  throw httpError(404, { detail: 'Не найдено' })
}

// ===== Обработчики auth и профиля =====

async function login(init) {
  const { data } = await readBody(init)
  const username = String(data.username || '').trim()
  const password = String(data.password || '')
  const found = state.users.find(user => user.username === username)
  if (!found || found.password !== password || found.is_active === false) {
    throw httpError(400, { error: 'Неверный логин или пароль' })
  }
  state.currentUserId = found.id
  persist()
  return jsonResponse(publicUser(found))
}

async function register(init) {
  const { data } = await readBody(init)
  const username = String(data.username || '').trim()
  const email = String(data.email || '').trim()
  const password1 = String(data.password1 || '')
  const password2 = String(data.password2 || '')
  const errors = {}

  if (!username) errors.username = ['Обязательное поле.']
  else if (state.users.some(user => user.username.toLowerCase() === username.toLowerCase())) {
    errors.username = ['Пользователь с таким именем уже существует.']
  }
  if (!email) errors.email = ['Обязательное поле.']
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = ['Введите корректный email.']
  else if (state.users.some(user => user.email.toLowerCase() === email.toLowerCase())) {
    errors.email = ['Такой email уже существует!']
  }
  if (!password1) errors.password1 = ['Обязательное поле.']
  else if (password1.length < 8) errors.password1 = ['Пароль должен содержать минимум 8 символов.']
  if (password1 !== password2) errors.password2 = ['Пароли не совпадают.']
  if (Object.keys(errors).length) throw httpError(400, { errors })

  const user = {
    id: nextId('user'),
    username,
    password: password1,
    email,
    first_name: String(data.first_name || '').trim(),
    last_name: String(data.last_name || '').trim(),
    about_me: '',
    avatar: null,
    banner_image: null,
    banner_gradient_start: '#0c6acf',
    banner_gradient_end: '#764ba2',
    data_birth: '',
    phone_namber: '',
    show_email: true,
    show_phone: false,
    show_birth_date: false,
    date_joined: new Date().toISOString(),
    is_staff: false,
    is_superuser: false,
    is_active: true,
    reputation: 0,
    likes: [],
  }
  state.users.push(user)
  state.currentUserId = user.id
  createNotification(
    user.id,
    userById(2)?.id || null,
    'follow',
    'Добро пожаловать на демо-стенд ФлакХаба! Данные хранятся только в вашем браузере.',
  )
  persist()
  return jsonResponse(publicUser(user), 201)
}

async function updateCurrentUser(init) {
  const user = requireUser()
  const { data, form } = await readBody(init)
  const allowed = ['first_name', 'last_name', 'about_me', 'banner_gradient_start', 'banner_gradient_end']
  for (const field of allowed) {
    if (data[field] !== undefined) user[field] = String(data[field])
  }
  for (const field of ['show_email', 'show_phone', 'show_birth_date']) {
    if (data[field] !== undefined) user[field] = parseBool(data[field], user[field])
  }
  if (data.phone_namber !== undefined) {
    const digits = String(data.phone_namber || '').replace(/\D/g, '')
    if (!digits) {
      user.phone_namber = ''
    } else {
      let normalized = digits.startsWith('8') ? `7${digits.slice(1)}` : digits
      if (!normalized.startsWith('7')) normalized = `7${normalized}`
      user.phone_namber = normalized.slice(0, 11)
    }
  }
  if (data.data_birth !== undefined) {
    user.data_birth = String(data.data_birth || '')
  }

  const photo = form?.get('photo')
  if (photo && typeof photo !== 'string') {
    user.avatar = await imageFileToDataUrl(photo, { maxSize: 400, quality: 0.85 })
  } else if (parseBool(data.photo_clear, false)) {
    user.avatar = null
  }
  const banner = form?.get('banner_image')
  if (banner && typeof banner !== 'string') {
    user.banner_image = await imageFileToDataUrl(banner, { maxSize: 1600, quality: 0.8 })
  } else if (parseBool(data.banner_image_clear, false)) {
    user.banner_image = null
  }

  persist()
  return jsonResponse({ ...profileUser(user), achievements: achievementsFor(user.id) })
}

async function changePassword(init) {
  const user = requireUser()
  const { data } = await readBody(init)
  const oldPassword = String(data.old_password || '')
  const password1 = String(data.new_password1 || '')
  const password2 = String(data.new_password2 || '')
  if (user.password !== oldPassword) throw httpError(400, { error: 'Старый пароль неверен' })
  if (!password1) throw httpError(400, { error: 'Введите новый пароль' })
  if (password1 !== password2) throw httpError(400, { error: 'Новые пароли не совпадают' })
  if (oldPassword === password1) throw httpError(400, { error: 'Новый пароль должен отличаться от старого' })
  if (password1.length < 8) throw httpError(400, { error: 'Пароль должен содержать минимум 8 символов' })
  user.password = password1
  persist()
  return jsonResponse({ status: 'ok', detail: 'Пароль успешно изменён' })
}

async function requestPasswordReset(init) {
  const { data } = await readBody(init)
  const email = String(data.email || '').trim()
  if (!email) throw httpError(400, { error: 'Введите email' })
  const user = state.users.find(item => item.email.toLowerCase() === email.toLowerCase())
  if (!user) throw httpError(400, { error: 'Пользователь с таким email не найден' })
  return jsonResponse({
    status: 'ok',
    detail: 'Демо-стенд не отправляет письма. Используйте пароль demo1234 или быстрый вход.',
  })
}

async function confirmPasswordReset(init) {
  const { data } = await readBody(init)
  const uidb64 = String(data.uidb64 || '')
  const token = String(data.token || '')
  const password1 = String(data.new_password1 || '')
  const password2 = String(data.new_password2 || '')
  if (!uidb64 || !token) throw httpError(400, { error: 'Неверная ссылка сброса пароля' })
  if (!password1 || !password2) throw httpError(400, { error: 'Введите новый пароль' })
  if (password1 !== password2) throw httpError(400, { error: 'Пароли не совпадают' })
  if (password1.length < 8) throw httpError(400, { error: 'Пароль должен содержать минимум 8 символов' })

  let id
  try {
    id = Number(window.atob(uidb64))
  } catch {
    id = null
  }
  const user = userById(id)
  if (!user) throw httpError(400, { error: 'Ссылка сброса недействительна' })
  user.password = password1
  persist()
  return jsonResponse({ status: 'ok', detail: 'Пароль успешно сброшен' })
}

// ===== Пользовательские действия и админка =====

function userAction(target, action, searchParams) {
  const actor = currentUser()
  if (action === 'stats') {
    const posts = state.posts.filter(post => post.authorId === target.id)
    const completedReviews = state.posts.filter(
      post => post.post_type === 'review' && post.review_status === 'completed',
    )
    return jsonResponse({
      posts_count: posts.filter(post => post.is_published).length,
      comments_count: state.comments.filter(
        comment => comment.authorId === target.id && comment.is_active !== false,
      ).length,
      likes_received: posts.reduce((total, post) => total + post.likes.length, 0),
      followers_count: state.subscriptions.filter(item => item.authorId === target.id).length,
      following_count: state.subscriptions.filter(item => item.subscriberId === target.id).length,
      reviews_given: completedReviews.filter(post => post.reviewerId === target.id).length,
      reviews_received: completedReviews.filter(post => post.authorId === target.id).length,
      reviews_requested: state.posts.filter(
        post => post.post_type === 'review' && post.authorId === target.id && post.is_published,
      ).length,
      review_languages: [...new Set(
        completedReviews
          .filter(post => post.reviewerId === target.id && post.code_language)
          .map(post => post.code_language),
      )].sort((a, b) => a.localeCompare(b)),
    })
  }

  if (action === 'achievements') {
    return jsonResponse(achievementsFor(target.id))
  }

  if (action === 'favorites') {
    if (!actor || actor.id !== target.id) throw httpError(403, { error: 'Доступ запрещен' })
    const posts = state.posts
      .filter(post => post.favorites.includes(target.id))
      .sort((a, b) => b.time_create.localeCompare(a.time_create))
      .map(serializePostList)
    return jsonResponse(paginate(posts, searchParams))
  }

  if (action === 'posts') {
    const posts = postsByAuthor(target.id)
      .sort((a, b) => b.time_create.localeCompare(a.time_create))
      .map(serializePostList)
    return jsonResponse(paginate(posts, searchParams))
  }

  if (action === 'reviews') {
    const role = searchParams.get('role') || 'given'
    if (!['given', 'received', 'requested'].includes(role)) {
      throw httpError(400, { role: 'Допустимо: given, received, requested' })
    }
    let posts = state.posts.filter(
      post => post.post_type === 'review' && post.is_published,
    )
    if (role === 'given') {
      posts = posts.filter(post => post.reviewerId === target.id && post.review_status === 'completed')
    } else if (role === 'received') {
      posts = posts.filter(post => post.authorId === target.id && post.review_status === 'completed')
    } else {
      posts = posts.filter(post => post.authorId === target.id)
    }
    posts = posts
      .sort((a, b) => b.time_create.localeCompare(a.time_create))
      .map(serializePostList)
    return jsonResponse(paginate(posts, searchParams))
  }

  // action === 'profile'
  return jsonResponse({ ...profileUser(target), achievements: achievementsFor(target.id) })
}

function adminStats() {
  const days = 14
  const today = new Date()
  const dateKeys = []
  for (let i = days - 1; i >= 0; i -= 1) {
    const date = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i)
    dateKeys.push(localDateKey(date))
  }
  const fill = values => {
    const counts = {}
    for (const value of values) {
      const key = localDateKey(value)
      counts[key] = (counts[key] || 0) + 1
    }
    return dateKeys.map(date => ({ date, count: counts[date] || 0 }))
  }

  return {
    total_users: state.users.length,
    total_posts: state.posts.length,
    published_posts: publishedPosts().length,
    total_comments: state.comments.filter(comment => comment.is_active !== false).length,
    total_admins: state.users.filter(user => user.is_superuser).length,
    total_moderators: state.users.filter(user => user.is_staff && !user.is_superuser).length,
    daily_registrations: fill(state.users.map(user => user.date_joined)),
    daily_posts: fill(state.posts.map(post => post.time_create)),
    daily_comments: fill(
      state.comments
        .filter(comment => comment.is_active !== false)
        .map(comment => comment.created_at),
    ),
  }
}

function adminUsers(searchParams) {
  const search = (searchParams.get('search') || '').trim().toLowerCase()
  const role = searchParams.get('role') || ''
  const page = Math.max(1, asInt(searchParams.get('page'), 1))
  let users = state.users.slice()
  if (search) {
    users = users.filter(user => [
      user.username,
      user.email,
      user.first_name,
      user.last_name,
    ].some(value => String(value || '').toLowerCase().includes(search)))
  }
  if (role === 'admin') users = users.filter(user => user.is_superuser)
  else if (role === 'moderator') users = users.filter(user => user.is_staff && !user.is_superuser)
  else if (role === 'user') users = users.filter(user => !user.is_staff && !user.is_superuser)
  users = users
    .sort((a, b) => b.date_joined.localeCompare(a.date_joined))
    .map(publicUser)
  const pageSize = 30
  const totalPages = Math.max(1, Math.ceil(users.length / pageSize))
  const currentPage = Math.min(page, totalPages)
  return {
    users: users.slice((currentPage - 1) * pageSize, currentPage * pageSize),
    count: users.length,
    total_pages: totalPages,
  }
}

async function adminChangeRole(userId, init) {
  const actor = requireSuperuser()
  const target = userById(userId)
  if (!target) throw httpError(404, { error: 'Пользователь не найден' })
  if (target.id === actor.id) throw httpError(400, { error: 'Нельзя изменить свою роль' })
  const { data } = await readBody(init)
  const role = String(data.role || '')
  if (!['user', 'moderator', 'admin'].includes(role)) {
    throw httpError(400, { error: 'Недопустимая роль. Допустимо: user, moderator, admin' })
  }
  target.is_superuser = role === 'admin'
  target.is_staff = role === 'admin' || role === 'moderator'
  persist()
  return jsonResponse({
    success: true,
    user_id: target.id,
    username: target.username,
    role,
  })
}

function adminToggleBan(userId) {
  const actor = requireSuperuser()
  const target = userById(userId)
  if (!target) throw httpError(404, { error: 'Пользователь не найден' })
  if (target.id === actor.id) throw httpError(400, { error: 'Нельзя заблокировать себя' })
  if (target.is_superuser) throw httpError(400, { error: 'Нельзя заблокировать администратора' })
  target.is_active = target.is_active === false
  persist()
  return jsonResponse({
    success: true,
    user_id: target.id,
    username: target.username,
    is_active: target.is_active,
  })
}

// ===== Подмена fetch и WebSocket =====

function isDemoPath(pathname) {
  return pathname.startsWith('/api/mobile/')
    || pathname === '/upload/'
    || pathname === '/ajax/subscribe/'
}

function installFetch() {
  if (window.fetch.__flachubDemo) return
  const nativeFetch = window.fetch.bind(window)
  const demoFetch = async function demoFetch(input, init = {}) {
    const rawUrl = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input)
    const parsed = new URL(rawUrl, window.location.origin)
    if (!isDemoPath(parsed.pathname)) return nativeFetch(input, init)

    try {
      return await handleRequest(parsed.pathname, parsed.searchParams, init, input)
    } catch (error) {
      if (error?.status) {
        return jsonResponse(error.payload || { detail: error.message }, error.status)
      }
      console.error('[demo] Ошибка обработчика:', error)
      return jsonResponse({ detail: 'Ошибка демо-сервера' }, 500)
    }
  }
  demoFetch.__flachubDemo = true
  window.fetch = demoFetch
}

function installWebSocket() {
  const NativeWebSocket = window.WebSocket
  if (!NativeWebSocket || NativeWebSocket.__flachubDemo) return

  class DemoWebSocket {
    constructor(url, protocols) {
      const raw = String(url)
      if (!raw.includes('/ws/')) return new NativeWebSocket(raw, protocols)

      this.url = raw
      this.readyState = DemoWebSocket.CONNECTING
      this.onopen = null
      this.onmessage = null
      this.onerror = null
      this.onclose = null
      this.timers = []
      liveSockets.add(this)

      this.timers.push(window.setTimeout(() => {
        if (this.readyState !== DemoWebSocket.CONNECTING) return
        this.readyState = DemoWebSocket.OPEN
        this.onopen?.({ type: 'open' })
        if (this.url.includes('/ws/notifications/')) {
          this.emit({ type: 'count', count: unreadNotifications() })
        }
      }, 0))
    }

    emit(data) {
      this.onmessage?.({ data: JSON.stringify(data) })
    }

    send(raw) {
      if (this.readyState !== DemoWebSocket.OPEN) return
      let data
      try {
        data = JSON.parse(raw)
      } catch {
        return
      }
      if (data?.type === 'mark_read' && this.url.includes('/ws/chat/')) {
        this.emit({ type: 'marked_read', by_user: currentUser()?.id || null })
      }
      // send_message уходит обычным POST /send/: не дублируем сообщение
      // через сокет, иначе в ленте появится две копии.
    }

    close() {
      if (this.readyState === DemoWebSocket.CLOSED) return
      this.readyState = DemoWebSocket.CLOSED
      for (const timer of this.timers) window.clearTimeout(timer)
      this.timers = []
      liveSockets.delete(this)
      this.onclose?.({ type: 'close', wasClean: true })
    }

    addEventListener(type, handler) {
      if (type === 'open') this.onopen = handler
      if (type === 'message') this.onmessage = handler
      if (type === 'close') this.onclose = handler
      if (type === 'error') this.onerror = handler
    }

    removeEventListener(type) {
      if (type === 'open') this.onopen = null
      if (type === 'message') this.onmessage = null
      if (type === 'close') this.onclose = null
      if (type === 'error') this.onerror = null
    }
  }

  DemoWebSocket.CONNECTING = 0
  DemoWebSocket.OPEN = 1
  DemoWebSocket.CLOSING = 2
  DemoWebSocket.CLOSED = 3
  DemoWebSocket.__flachubDemo = true
  window.WebSocket = DemoWebSocket
}

// ===== Плашка демо-стенда =====

function installBadge() {
  if (document.getElementById('flachub-demo-badge')) return
  const style = document.createElement('style')
  style.textContent = `
    #flachub-demo-badge {
      position: fixed; left: 16px; bottom: 16px; z-index: 10000;
      display: flex; align-items: center; gap: 9px;
      padding: 8px 10px 8px 12px; border-radius: 999px;
      background: rgba(17, 24, 39, 0.94); color: #f9fafb;
      font: 500 12px/1.2 system-ui, -apple-system, "Segoe UI", sans-serif;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.28);
      backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.12);
    }
    #flachub-demo-badge .flachub-demo-dot {
      width: 8px; height: 8px; border-radius: 50%; background: #34d399;
      box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.18); flex-shrink: 0;
    }
    #flachub-demo-badge strong { font-weight: 700; }
    #flachub-demo-badge button {
      margin-left: 2px; padding: 5px 10px; border: 0; border-radius: 999px;
      background: rgba(255, 255, 255, 0.14); color: #fff; cursor: pointer;
      font: inherit; transition: background 0.15s ease;
    }
    #flachub-demo-badge button:hover { background: rgba(255, 255, 255, 0.25); }
    #flachub-demo-toast {
      position: fixed; left: 50%; bottom: 24px; z-index: 10001;
      transform: translate(-50%, 20px); max-width: min(460px, calc(100vw - 32px));
      padding: 12px 18px; border-radius: 12px; background: #111827; color: #fff;
      font: 500 13px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35); opacity: 0;
      pointer-events: none; transition: opacity 0.2s ease, transform 0.2s ease;
    }
    #flachub-demo-toast.is-visible { opacity: 1; transform: translate(-50%, 0); }
    @media (max-width: 640px) {
      #flachub-demo-badge { left: 8px; bottom: 8px; padding: 6px 8px 6px 10px; font-size: 11px; }
      #flachub-demo-badge .flachub-demo-note { display: none; }
      #flachub-demo-badge button { padding: 4px 8px; }
    }
    @media print { #flachub-demo-badge, #flachub-demo-toast { display: none !important; } }
  `
  document.head.appendChild(style)

  const badge = document.createElement('div')
  badge.id = 'flachub-demo-badge'
  badge.title = 'Демо-стенд: demo / demo1234, admin / admin1234'
  badge.innerHTML = `
    <span class="flachub-demo-dot"></span>
    <span><strong>Демо</strong><span class="flachub-demo-note"> · данные в браузере</span></span>
    <button type="button">Сбросить</button>
  `
  badge.querySelector('button').addEventListener('click', () => {
    const confirmed = window.confirm(
      'Сбросить демо-данные? Все созданные записи, сообщения и загруженные файлы будут удалены.',
    )
    if (!confirmed) return
    try {
      window.localStorage.removeItem(DEMO_STORAGE_KEY)
    } catch {
      // Ничего страшного: страница всё равно перезагрузится.
    }
    window.location.assign(`${import.meta.env.BASE_URL}`)
  })
  document.body.appendChild(badge)
}

function showToast(message) {
  let toast = document.getElementById('flachub-demo-toast')
  if (!toast) {
    toast = document.createElement('div')
    toast.id = 'flachub-demo-toast'
    document.body.appendChild(toast)
  }
  toast.textContent = message
  toast.classList.add('is-visible')
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 4500)
}

// ===== Точка входа =====

export function installDemo() {
  if (window.__flachubDemoInstalled) return
  window.__flachubDemoInstalled = true

  if (!document.cookie.includes('csrftoken=')) {
    document.cookie = 'csrftoken=flachub-demo; path=/; SameSite=Lax'
  }

  installFetch()
  installWebSocket()
  if (document.body) {
    installBadge()
  } else {
    window.addEventListener('DOMContentLoaded', installBadge, { once: true })
  }
}
