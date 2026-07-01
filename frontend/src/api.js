import { getCSRFToken } from './csrf'

const BASE = '/api/mobile'

async function request(url, options = {}) {
  const config = {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    ...options,
  }
  if (options.method && options.method !== 'GET') {
    const csrf = getCSRFToken()
    if (csrf) config.headers['X-CSRFToken'] = csrf
  }
  const res = await fetch(url, config)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  if (res.status === 204) return null
  return res.json()
}

export function fetchPost(slug) {
  return request(`${BASE}/posts/${slug}/`)
}

export function toggleLike(postId) {
  return request(`${BASE}/post-actions/${postId}/toggle_like/`, {
    method: 'POST',
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
  return request(`${BASE}/post-actions/${postId}/toggle_favorite/`, {
    method: 'POST',
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
  return request(`${BASE}/comments/${commentId}/`, {
    method: 'DELETE',
  })
}

export function toggleCommentLike(commentId) {
  return request('/ajax/toggle-comment-like/', {
    method: 'POST',
    body: new URLSearchParams({ comment_id: commentId }),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function deletePost(slug) {
  return request(`${BASE}/posts/${slug}/`, {
    method: 'DELETE',
  })
}
