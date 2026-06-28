import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/Sidebar/Sidebar'
import { CKEditor } from '@ckeditor/ckeditor5-react'
import {
  BalloonEditor, Essentials, Paragraph, Heading, Title,
  Bold, Italic, Underline, Strikethrough, Code,
  List, Link as CkLink, BlockQuote, CodeBlock, Table,
  Font, Alignment, Indent, HorizontalLine,
  Autoformat, PasteFromOffice, RemoveFormat,
} from 'ckeditor5'

function csrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/)
  return m ? m[1] : ''
}

function extractTitle(html) {
  const m = html.match(/<h[1-3][^>]*>([^<]+)<\/h[1-3]>/)
  if (m) return m[1].trim()
  const m2 = html.match(/<p>([^<]+)<\/p>/)
  if (m2) return m2[1].trim()
  const div = document.createElement('div')
  div.innerHTML = html
  const text = div.textContent.trim()
  return text.split('\n')[0].trim() || text.slice(0, 100)
}

const editorConfig = {
  licenseKey: 'GPL',
  plugins: [
    Essentials, Paragraph, Heading, Title,
    Bold, Italic, Underline, Strikethrough, Code,
    List, CkLink, BlockQuote, CodeBlock, Table,
    Font, Alignment, Indent, HorizontalLine,
    Autoformat, PasteFromOffice, RemoveFormat,
  ],
  toolbar: [
    'undo', 'redo', '|',
    'heading', '|',
    'bold', 'italic', 'underline', 'strikethrough', 'code', '|',
    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
    'alignment', '|',
    'outdent', 'indent', '|',
    'numberedList', 'bulletedList', '|',
    'link', 'blockQuote', 'codeBlock', 'insertTable', 'horizontalLine', '|',
    'removeFormat',
  ],
  heading: {
    options: [
      { model: 'paragraph', title: 'Параграф', class: 'ck-heading_paragraph' },
      { model: 'heading1', view: 'h1', title: 'Заголовок 1', class: 'ck-heading_h1' },
      { model: 'heading2', view: 'h2', title: 'Заголовок 2', class: 'ck-heading_h2' },
      { model: 'heading3', view: 'h3', title: 'Заголовок 3', class: 'ck-heading_h3' },
      { model: 'heading4', view: 'h4', title: 'Заголовок 4', class: 'ck-heading_h4' },
      { model: 'heading5', view: 'h5', title: 'Заголовок 5', class: 'ck-heading_h5' },
      { model: 'heading6', view: 'h6', title: 'Заголовок 6', class: 'ck-heading_h6' },
    ],
  },
  alignment: {
    options: ['left', 'center', 'right', 'justify'],
  },
  table: {
    contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells'],
  },
  title: {
    placeholder: 'Заголовок публикации',
  },
  placeholder: 'Начните писать текст публикации...',
}

const POST_TYPES = [
  { value: 'post',      icon: 'fa-sticky-note',  title: 'Пост',    desc: 'Короткая публикация или заметка' },
  { value: 'article',   icon: 'fa-file-alt',      title: 'Статья',  desc: 'Подробный материал с анализом' },
  { value: 'news',      icon: 'fa-newspaper',     title: 'Новость', desc: 'Актуальная информация о событиях' },
  { value: 'idea',      icon: 'fa-lightbulb',     title: 'Идея',    desc: 'Креативная мысль или предложение' },
]

function AddPostPage() {
  const { slug } = useParams()
  const isEditing = !!slug
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loadingPost, setLoadingPost] = useState(false)
  const [categories, setCategories] = useState([])
  const [allTags, setAllTags] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [showSearch, setShowSearch] = useState(false)
  const [selectedTagIds, setSelectedTagIds] = useState(new Set())
  const [tagFilter, setTagFilter] = useState('all')
  const [photoFile, setPhotoFile] = useState(null)
  const [photoPreview, setPhotoPreview] = useState(null)
  const [fileName, setFileName] = useState('Файл не выбран')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const searchRef = useRef(null)
  const editorRef = useRef(null)

  const [form, setForm] = useState({
    content: '',
    post_type: 'post',
    is_published: '1',
    cat: '',
  })

  useEffect(() => {
    if (loading) return
    if (!user) { navigate('/login/'); return }
    fetch('/api/mobile/categories/', { credentials: 'same-origin' })
      .then(r => r.json()).then(d => setCategories(d.results || d)).catch(() => {})
    fetch('/api/mobile/tags/', { credentials: 'same-origin' })
      .then(r => r.json()).then(d => setAllTags(d.results || d)).catch(() => {})
  }, [user, loading])

  useEffect(() => {
    if (searchQuery.length < 2) { setShowSearch(false); return }
    const q = searchQuery.toLowerCase()
    const filtered = allTags.filter(t =>
      t.tag.toLowerCase().includes(q) && !selectedTagIds.has(t.id)
    )
    setSearchResults(filtered)
    setShowSearch(true)
  }, [searchQuery, allTags, selectedTagIds])

  useEffect(() => {
    if (!slug || !user) return
    setLoadingPost(true)
    fetch(`/api/mobile/posts/${slug}/`, { credentials: 'same-origin' })
      .then(async r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        if (data.author?.id !== user.id) throw new Error('Это не ваша статья')
        setForm({
          content: data.content || '',
          post_type: data.post_type || 'post',
          is_published: String(data.is_published ?? '1'),
          cat: data.category?.id || '',
        })
        setSelectedTagIds(new Set(data.tags?.map(t => t.id) || []))
        if (data.photo) {
          setPhotoPreview(data.photo)
          setFileName('Текущая обложка')
        }
      })
      .catch(e => { setError(e.message); setStep(1) })
      .finally(() => setLoadingPost(false))
  }, [slug, user])

  useEffect(() => {
    function handleClick(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) setShowSearch(false)
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  function goTo(s) {
    setStep(s)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function f(field, value) {
    setForm(p => ({ ...p, [field]: value }))
  }

  function handlePhoto(e) {
    const file = e.target.files[0]
    if (!file) return
    setPhotoFile(file)
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = ev => setPhotoPreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  function addTag(tagId) {
    if (selectedTagIds.has(tagId)) return
    const newSet = new Set(selectedTagIds)
    newSet.add(tagId)
    setSelectedTagIds(newSet)
    setSearchQuery('')
    setShowSearch(false)
  }

  function removeTag(tagId) {
    const newSet = new Set(selectedTagIds)
    newSet.delete(tagId)
    setSelectedTagIds(newSet)
  }

  function selectFromSearch(tagId) {
    addTag(tagId)
    setShowSearch(false)
    setSearchQuery('')
  }

  const filteredGridTags = allTags.filter(t => {
    if (tagFilter === 'popular' && !t.is_popular) return false
    return true
  })

  async function handleSubmit(e) {
    e.preventDefault()
    const fullHtml = form.content
    const title = extractTitle(fullHtml)
    const content = fullHtml
    if (!title) { setError('Введите заголовок'); return }
    if (!content.trim()) { setError('Введите содержание'); return }
    setError('')
    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('title', title)
      fd.append('content', content)
      fd.append('post_type', form.post_type)
      fd.append('is_published', form.is_published)
      if (form.cat) fd.append('cat', form.cat)
      selectedTagIds.forEach(id => fd.append('tags', id))
      if (photoFile) fd.append('photo', photoFile)

      console.log('Submitting post:', { title, content_length: content.length, post_type: form.post_type, is_published: form.is_published, cat: form.cat, tags: [...selectedTagIds] })

      const url = isEditing ? `/api/mobile/posts/${slug}/` : '/api/mobile/posts/'
      const method = isEditing ? 'PATCH' : 'POST'
      const res = await fetch(url, {
        method,
        headers: { 'X-CSRFToken': csrfToken() },
        credentials: 'same-origin',
        body: fd,
      })
      const text = await res.text()
      let data
      try { data = JSON.parse(text) } catch { throw new Error(`Ошибка (${res.status}): ${text.slice(0, 200)}`) }
      if (!res.ok) {
        const msg = typeof data === 'object' && data !== null
          ? Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
          : data.error || data
        throw new Error(msg)
      }
      navigate(`/post/${data.slug || slug}/`)
    } catch (err) {
      setError(err.message)
    }
    setSubmitting(false)
  }

  const steps = [{ n: 1, t: 'Тип поста' }, { n: 2, t: 'Редактор' }, { n: 3, t: 'Настройки' }]

  if (loading || loadingPost) {
    return (
      <main className="page">
        <div className="pg-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#666' }}></i>
        </div>
      </main>
    )
  }

  return (
    <main className="page">
      <div className="pg-container layout">
        <div className="content" style={{ flex: 1, minWidth: 0 }}>
          <div className="add-article-wizard">
            <div className="wizard-progress">
              {steps.map((s, i) => (
                <span key={s.n} style={{ display: 'contents' }}>
                  {i > 0 && <div className="progress-bar"></div>}
                  <div className={`progress-step${step === s.n ? ' active' : ''}`} data-step={s.n}>
                    <div className="step-number">{s.n}</div>
                    <div className="step-text">{s.t}</div>
                  </div>
                </span>
              ))}
            </div>

            <form method="post" encType="multipart/form-data" id="article-form" onSubmit={handleSubmit}>
              {error && (
                <div style={{ padding: '12px 16px', background: '#fee2e2', color: '#dc2626', borderRadius: 8, marginBottom: 16 }}>
                  {error}
                </div>
              )}

              {/* Шаг 1: Тип поста */}
              <div className={`wizard-step${step === 1 ? ' active' : ''}`} id="step-1">
                <div className="step-content">
                  <div className="step-header">
                    <h1><i className="fas fa-shapes"></i> Тип публикации</h1>
                    <p>Выберите формат вашего материала</p>
                  </div>
                  <div className="post-type-grid">
                    {POST_TYPES.map(pt => (
                      <label key={pt.value}
                        className={`post-type-card${form.post_type === pt.value ? ' active' : ''}`}
                        data-type={pt.value}
                        onClick={() => f('post_type', pt.value)}
                      >
                        <input type="radio" name="post_type" value={pt.value}
                          checked={form.post_type === pt.value} readOnly
                        />
                        <div className="type-icon"><i className={`fas ${pt.icon}`}></i></div>
                        <div className="type-title">{pt.title}</div>
                        <div className="type-desc">{pt.desc}</div>
                      </label>
                    ))}
                  </div>
                  <div className="step-footer">
                    <button type="button" className="btn btn-primary" onClick={() => goTo(2)}>
                      Продолжить <i className="fas fa-arrow-right"></i>
                    </button>
                  </div>
                </div>
              </div>

              {/* Шаг 2: Редактор */}
              <div className={`wizard-step${step === 2 ? ' active' : ''}`} id="step-2">
                <div className="editor-container">
                  <div className="form-group full-width">
                    {step === 2 && (
                      <CKEditor
                        editor={BalloonEditor}
                        data={form.content}
                        config={editorConfig}
                        disableWatchdog
                        onReady={(editor) => { editorRef.current = editor }}
                        onChange={(event, editor) => {
                          f('content', editor.getData())
                        }}
                        onError={(error, details) => {
                          console.error('CKEditor error:', error, details)
                        }}
                      />
                    )}
                  </div>
                </div>
                <div className="step-footer" style={{ marginTop: 20 }}>
                  <button type="button" className="btn btn-secondary" onClick={() => goTo(1)}>
                    <i className="fas fa-arrow-left"></i> Назад
                  </button>
                  <button type="button" className="btn btn-primary" onClick={() => goTo(3)}>
                    Продолжить <i className="fas fa-arrow-right"></i>
                  </button>
                </div>
              </div>

              {/* Шаг 3: Настройки */}
              <div className={`wizard-step${step === 3 ? ' active' : ''}`} id="step-3">
                <div className="step-content">
                  <div className="step-header">
                    <h1><i className="fas fa-cog"></i> Настройки</h1>
                    <p>Категория, теги и параметры публикации</p>
                  </div>
                  <div className="settings-grid">
                    <div className="settings-section">
                      <h3><i className="fas fa-info-circle"></i> Основная информация</h3>
                      <div className="form-row">
                        <div className="form-group">
                          <label><i className="fas fa-folder"></i> Категория</label>
                          <select className="form-control" value={form.cat}
                            onChange={e => f('cat', e.target.value)}
                          >
                            <option value="">Не выбрано</option>
                            {categories.map(c => (
                              <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                          </select>
                        </div>
                        <div className="form-group">
                          <label><i className="fas fa-toggle-on"></i> Статус</label>
                          <select className="form-control" value={form.is_published}
                            onChange={e => f('is_published', e.target.value)}
                          >
                            <option value="1">Опубликовано</option>
                            <option value="0">Черновик</option>
                          </select>
                        </div>
                      </div>
                      <div className="form-group">
                        <label><i className="fas fa-image"></i> Обложка</label>
                        <div className="file-upload-wrapper">
                          <div className="cover-upload-container">
                            <input type="file" id="photo-input" accept="image/*"
                              onChange={handlePhoto} style={{ display: 'none' }}
                            />
                            <label htmlFor="photo-input" className="cover-file-label">
                              <i className="fas fa-upload"></i>
                              <span>Выбрать обложку...</span>
                            </label>
                            <span className="file-name">{fileName}</span>
                          </div>
                          {photoPreview && (
                            <div className="file-preview">
                              <img src={photoPreview} alt="Preview" />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="settings-section">
                      <h3><i className="fas fa-tags"></i> Теги</h3>
                      <div className="tag-search-container" ref={searchRef}>
                        <div className="search-wrapper">
                          <i className="fas fa-search"></i>
                          <input type="text" id="tag-search" className="tag-search-input"
                            placeholder="Поиск тегов..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            onFocus={() => { if (searchQuery.length >= 2) setShowSearch(true) }}
                          />
                        </div>
                        {showSearch && (
                          <div className="search-results active" id="tag-search-results">
                            {searchResults.length === 0 ? (
                              <div className="search-result-item">Ничего не найдено</div>
                            ) : (
                              searchResults.map(t => (
                                <div key={t.id} className="search-result-item"
                                  data-tag-id={t.id} data-tag-name={t.tag}
                                  onClick={() => selectFromSearch(t.id)}
                                >
                                  <span>{t.tag}</span>
                                  <i className="fas fa-plus-circle"></i>
                                </div>
                              ))
                            )}
                          </div>
                        )}
                      </div>
                      <div className="selected-tags-container">
                        <div className="selected-tags" id="selectedTags">
                          {selectedTagIds.size === 0 ? (
                            <span className="no-tags" id="no-tags-msg">Теги не выбраны</span>
                          ) : (
                            [...selectedTagIds].map(id => {
                              const t = allTags.find(tt => tt.id === id)
                              if (!t) return null
                              return (
                                <span key={t.id} className="tag-selected" data-id={t.id}
                                  onClick={() => removeTag(t.id)}
                                  style={{ cursor: 'pointer' }}
                                >
                                  {t.tag}
                                  <span className="tag-remove" data-id={t.id}
                                    onClick={e => { e.stopPropagation(); removeTag(t.id) }}
                                  >
                                    <i className="fas fa-times"></i>
                                  </span>
                                </span>
                              )
                            })
                          )}
                        </div>
                      </div>
                      <div className="available-skills">
                        <div className="tags-header">
                          <label>Все теги:</label>
                          <div className="tags-filter">
                            <button type="button"
                              className={`filter-btn${tagFilter === 'all' ? ' active' : ''}`}
                              data-filter="all"
                              onClick={() => setTagFilter('all')}
                            >Все</button>
                            <button type="button"
                              className={`filter-btn${tagFilter === 'popular' ? ' active' : ''}`}
                              data-filter="popular"
                              onClick={() => setTagFilter('popular')}
                            >Популярные</button>
                          </div>
                        </div>
                        <div className="tags-grid" id="tagsGrid">
                          {filteredGridTags.map(t => {
                            const isSelected = selectedTagIds.has(t.id)
                            return (
                              <div key={t.id}
                                className={`tag-wrapper${t.is_popular ? ' popular' : ''}${isSelected ? ' hidden' : ''}`}
                                data-tag-id={t.id} data-tag-name={t.tag}
                                style={{ display: isSelected ? 'none' : 'inline-flex' }}
                              >
                                <input type="checkbox" name="tags" value={t.id}
                                  id={`tag-${t.id}`} data-tag-id={t.id} data-tag-name={t.tag}
                                  checked={isSelected}
                                  onChange={() => isSelected ? removeTag(t.id) : addTag(t.id)}
                                  style={{ position: 'absolute', opacity: 0, pointerEvents: 'none' }}
                                />
                                <label htmlFor={`tag-${t.id}`} className="tag-option">{t.tag}</label>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="step-footer">
                    <button type="button" className="btn btn-secondary" onClick={() => goTo(2)}>
                      <i className="fas fa-arrow-left"></i> Назад
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={submitting}>
                      <i className="fas fa-save"></i> {submitting ? 'Сохранение...' : isEditing ? 'Сохранить' : 'Опубликовать'}
                    </button>
                    <Link to="/" className="btn btn-secondary">
                      <i className="fas fa-times"></i> Отмена
                    </Link>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
        <aside className="sidebar" aria-label="Боковая панель">
          <Sidebar compact />
        </aside>
      </div>
    </main>
  )
}

export default AddPostPage
