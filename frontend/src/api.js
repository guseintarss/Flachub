const BASE = '/api/mobile'

function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]')
  if (meta) return meta.getAttribute('content')
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : null
}

async function request(url, options = {}) {
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  }
  if (options.method && options.method !== 'GET') {
    const csrf = getCSRFToken()
    if (csrf) config.headers['X-CSRFToken'] = csrf
  }
  const res = await fetch(url, config)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export function fetchPost(slug) {
  return request(`${BASE}/posts/${slug}/`)
}

export function toggleLike(postId) {
  return request('/ajax/like/', {
    method: 'POST',
    body: new URLSearchParams({ post_id: postId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function toggleBookmark(postId) {
  return request('/bookmarks/toggle/', {
    method: 'POST',
    body: new URLSearchParams({ post_id: postId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function toggleFavorite(postId) {
  return request('/ajax/favorite/', {
    method: 'POST',
    body: new URLSearchParams({ post_id: postId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function toggleSubscribe(authorId) {
  return request('/ajax/subscribe/', {
    method: 'POST',
    body: new URLSearchParams({ author_id: authorId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function addComment(postId, content, parentId = '') {
  return request('/ajax/add-comment/', {
    method: 'POST',
    body: new URLSearchParams({ post_id: postId, content, parent_id: parentId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function deleteComment(commentId) {
  return request('/ajax/delete-comment/', {
    method: 'POST',
    body: new URLSearchParams({ comment_id: commentId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function toggleCommentLike(commentId) {
  return request('/ajax/toggle-comment-like/', {
    method: 'POST',
    body: new URLSearchParams({ comment_id: commentId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}
