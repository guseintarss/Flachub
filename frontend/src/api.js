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

export function addComment(postId, content, parentId = '', extra = {}) {
  const payload = {
    post_id: postId,
    content,
    parent: parentId || undefined,
  }
  if (extra.line_start != null) {
    payload.line_start = extra.line_start
    payload.line_end = extra.line_end ?? extra.line_start
  }
  if (extra.severity) {
    payload.severity = extra.severity
  }
  return request(`${BASE}/comments/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function claimReview(slug) {
  return request(`${BASE}/posts/${slug}/claim_review/`, {
    method: 'POST',
  })
}

export function releaseReview(slug) {
  return request(`${BASE}/posts/${slug}/release_review/`, {
    method: 'POST',
  })
}

export function acceptReviewComment(commentId) {
  return request(`${BASE}/comments/${commentId}/accept/`, {
    method: 'POST',
  })
}

export function resolveReviewComment(commentId) {
  return request(`${BASE}/comments/${commentId}/resolve/`, {
    method: 'POST',
  })
}

export function deleteComment(commentId) {
  return request(`${BASE}/comments/${commentId}/`, {
    method: 'DELETE',
  })
}

export function toggleCommentLike(commentId) {
  return request(`${BASE}/comment-actions/${commentId}/toggle_like/`, {
    method: 'POST',
  })
}

export function deletePost(slug) {
  return request(`${BASE}/posts/${slug}/`, {
    method: 'DELETE',
  })
}

export function getChats() {
  return request(`${BASE}/chats/`)
}

export function getChat(id) {
  return request(`${BASE}/chats/${id}/`)
}

export function getChatMessages(id) {
  return request(`${BASE}/chats/${id}/messages/`)
}

export function sendMessage(chatId, text) {
  return request(`${BASE}/chats/${chatId}/send/`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function createChat(participantId) {
  return request(`${BASE}/chats/`, {
    method: 'POST',
    body: JSON.stringify({ participant_id: participantId }),
  })
}

export function markChatRead(chatId) {
  return request(`${BASE}/chats/${chatId}/mark_read/`, {
    method: 'POST',
  })
}

export function trackRead(slug, payload = {}) {
  const body = JSON.stringify({
    referrer: document.referrer || '',
    ...payload,
  })
  const headers = { 'Content-Type': 'application/json' }
  const csrf = getCSRFToken()
  if (csrf) headers['X-CSRFToken'] = csrf
  return fetch(`${BASE}/posts/${slug}/read/`, {
    method: 'POST',
    headers,
    credentials: 'same-origin',
    keepalive: true,
    body,
  }).catch(() => null)
}

export function fetchAuthorDashboard(days = 30) {
  return request(`${BASE}/author/dashboard/?days=${days}`)
}

export function importFromHabr(url) {
  return request(`${BASE}/import/habr/`, {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

export function importFromGithub(url) {
  return request(`${BASE}/import/github/`, {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

export function fetchReviewRequests(params = {}) {
  const query = new URLSearchParams()
  if (params.status) query.set('status', params.status)
  if (params.mine) query.set('mine', '1')
  if (params.reviewer) query.set('reviewer', params.reviewer)
  if (params.page) query.set('page', params.page)
  const suffix = query.toString() ? `?${query}` : ''
  return request(`${BASE}/review-requests/${suffix}`)
}

export function fetchReviewSpotlight() {
  return request(`${BASE}/review-spotlight/`)
}

export function createReviewOffer(requestId, payload) {
  return request(`${BASE}/review-requests/${requestId}/offer/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function selectReviewOffer(requestId, offerId) {
  return request(`${BASE}/review-requests/${requestId}/select_offer/`, {
    method: 'POST',
    body: JSON.stringify({ offer_id: offerId }),
  })
}

export function withdrawReviewOffer(requestId) {
  return request(`${BASE}/review-requests/${requestId}/withdraw_offer/`, {
    method: 'POST',
  })
}

export function cancelReviewRequest(requestId) {
  return request(`${BASE}/review-requests/${requestId}/cancel/`, {
    method: 'POST',
  })
}
