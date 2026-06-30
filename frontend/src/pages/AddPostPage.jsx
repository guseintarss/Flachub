import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/Sidebar/Sidebar'
import { AddPostSkeleton } from '../components/Skeleton'
import { CKEditor } from '@ckeditor/ckeditor5-react'
import {
  BalloonEditor, Essentials, Paragraph, Heading, Title,
  Bold, Italic, Underline, Strikethrough, Code,
  List, Link as CkLink, BlockQuote, CodeBlock, Table,
  Font, Alignment, Indent, HorizontalLine,
  Autoformat, PasteFromOffice, RemoveFormat,
  Image, ImageUpload, ImageToolbar, ImageStyle, ImageResize, ImageTextAlternative,
  AutoImage,
  MediaEmbed, AutoMediaEmbed, MediaEmbedResize, MediaEmbedToolbar,
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

function stripTitleFromContent(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  const h = div.querySelector('h1, h2, h3')
  if (h) h.remove()
  return div.innerHTML
}

class MyUploadAdapter {
  constructor(loader) {
    this.loader = loader
  }

  async upload() {
    const file = await this.loader.file
    const fd = new FormData()
    fd.append('upload', file)
    const res = await fetch('/upload/', {
      method: 'POST',
      body: fd,
      credentials: 'same-origin',
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || 'Ошибка загрузки изображения')
    }
    const data = await res.json()
    return { default: data.url }
  }

  abort() {}
}

const editorConfig = {
  licenseKey: 'GPL',
  plugins: [
    Essentials, Paragraph, Heading, Title,
    Bold, Italic, Underline, Strikethrough, Code,
    List, CkLink, BlockQuote, CodeBlock, Table,
    Font, Alignment, Indent, HorizontalLine,
    Autoformat, PasteFromOffice, RemoveFormat,
    Image, ImageUpload, ImageToolbar, ImageStyle, ImageResize, ImageTextAlternative,
    AutoImage,
    MediaEmbed, AutoMediaEmbed, MediaEmbedResize, MediaEmbedToolbar,
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
    'insertImage', 'mediaEmbed', '|',
    'removeFormat',
  ],
  image: {
    toolbar: [
      'imageStyle:block',
      'imageStyle:wrapText',
      'imageStyle:breakText',
      '|',
      'toggleImageCaption',
      'imageTextAlternative',
      '|',
      'resizeImage:original',
      'resizeImage:50',
      'resizeImage:75',
    ],
    resizeOptions: [
      { name: 'resizeImage:original', value: null, label: 'Оригинал' },
      { name: 'resizeImage:50', value: '50', label: '50%' },
      { name: 'resizeImage:75', value: '75', label: '75%' },
    ],
    styles: {
      options: [
        'inline',
        'alignLeft',
        'alignRight',
        'alignCenter',
        'alignBlockLeft',
        'alignBlockRight',
      ],
    },
  },
  mediaEmbed: {
    previewsInData: true,
    toolbar: ['mediaEmbedResize', 'mediaEmbedStyle'],
  },
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

const SLASH_COMMANDS = [
  { id: 'heading1',     icon: 'fas fa-heading',       label: 'Заголовок 1',  command: 'heading',      args: [{ value: 'heading1' }],       group: 'Структура' },
  { id: 'heading2',     icon: 'fas fa-heading',       label: 'Заголовок 2',  command: 'heading',      args: [{ value: 'heading2' }],       group: 'Структура' },
  { id: 'heading3',     icon: 'fas fa-heading',       label: 'Заголовок 3',  command: 'heading',      args: [{ value: 'heading3' }],       group: 'Структура' },
  { id: 'bulletList',   icon: 'fas fa-list-ul',       label: 'Маркированный список', command: 'bulletedList', args: [],            group: 'Структура' },
  { id: 'numberedList', icon: 'fas fa-list-ol',       label: 'Нумерованный список',  command: 'numberedList', args: [],            group: 'Структура' },
  { id: 'blockquote',   icon: 'fas fa-quote-right',   label: 'Цитата',       command: 'blockQuote',   args: [],                 group: 'Структура' },
  { id: 'codeBlock',    icon: 'fas fa-code',          label: 'Блок кода',    command: 'codeBlock',    args: [],                 group: 'Структура' },
  { id: 'separator1',   separator: true },
  { id: 'bold',         icon: 'fas fa-bold',          label: 'Жирный',       command: 'bold',         args: [],                 group: 'Форматирование' },
  { id: 'italic',       icon: 'fas fa-italic',        label: 'Курсив',       command: 'italic',       args: [],                 group: 'Форматирование' },
  { id: 'underline',    icon: 'fas fa-underline',     label: 'Подчеркнутый', command: 'underline',    args: [],                 group: 'Форматирование' },
  { id: 'strikethrough',icon: 'fas fa-strikethrough', label: 'Зачеркнутый',  command: 'strikethrough', args: [],                 group: 'Форматирование' },
  { id: 'code',         icon: 'fas fa-code',          label: 'Код',          command: 'code',         args: [],                 group: 'Форматирование' },
  { id: 'separator2',   separator: true },
  { id: 'horizontalLine',icon: 'fas fa-minus',        label: 'Горизонтальная линия', command: 'horizontalLine', args: [],        group: 'Вставка' },
  { id: 'table',        icon: 'fas fa-table',         label: 'Таблица',      command: 'insertTable',  args: [{ rows: 3, columns: 3 }], group: 'Вставка' },
  { id: 'image',        icon: 'fas fa-image',         label: 'Изображение',  command: 'uploadImage',  args: [],                 group: 'Вставка' },
  { id: 'mediaEmbed',   icon: 'fas fa-video',         label: 'Видео',        command: 'mediaEmbed',   args: [],                 group: 'Вставка' },
  { id: 'link',         icon: 'fas fa-link',          label: 'Ссылка',       command: 'link',         args: [],                 group: 'Вставка' },
]

const POST_TYPES = [
  { value: 'post',      icon: 'fa-sticky-note',  title: 'Пост',    desc: 'Короткая публикация или заметка',
    rules: [
      'Краткость — сестра таланта. Оптимально до 500 символов',
      'Одна главная мысль на весь пост',
      'Форматирование (жирный, курсив) помогает расставить акценты',
      'Можно добавить 1-2 изображения для наглядности',
    ] },
  { value: 'article',   icon: 'fa-file-alt',      title: 'Статья',  desc: 'Подробный материал с анализом',
    rules: [
      'Раскрывайте тему полностью — от 1000 символов',
      'Структурируйте текст: введение, основная часть, выводы',
      'Используйте подзаголовки, списки, таблицы',
      'Добавляйте изображения, цитаты и ссылки на источники',
    ] },
  { value: 'news',      icon: 'fa-newspaper',     title: 'Новость', desc: 'Актуальная информация о событиях',
    rules: [
      'Заголовок должен чётко отражать суть новости',
      'Указывайте источник информации и дату события',
      'Излагайте факты без лишних оценок',
      'Проверяйте информацию — объективность превыше всего',
    ] },
  { value: 'idea',      icon: 'fa-lightbulb',     title: 'Идея',    desc: 'Креативная мысль или предложение',
    rules: [
      'Опишите проблему, которую решает ваша идея',
      'Предложите конкретное решение или подход',
      'Оцените примерные ресурсы и сроки реализации',
      'Приведите примеры, аналогии или прототипы',
    ] },
]

function AddPostPage() {
  const { slug } = useParams()
  const isEditing = !!slug
  const { user, loading, setUser } = useAuth()
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

  const [showRules, setShowRules] = useState(false)
  const [slashMenu, setSlashMenu] = useState({ visible: false, x: 0, y: 0, query: '' })
  const slashMenuRef = useRef(null)
  const hideSlashTimeout = useRef(null)

  const getSlashQuery = useCallback(() => {
    try {
      const sel = window.getSelection()
      if (!sel || !sel.rangeCount || !sel.isCollapsed) return null
      const range = sel.getRangeAt(0)
      if (range.startContainer.nodeType !== Node.TEXT_NODE) return null
      const text = range.startContainer.textContent.slice(0, range.startOffset)
      const slashIdx = text.lastIndexOf('/')
      if (slashIdx === -1) return null
      if (slashIdx > 0 && text[slashIdx - 1] !== ' ') return null
      return text.slice(slashIdx + 1)
    } catch (e) {
      console.error('[SlashMenu] getSlashQuery error:', e)
      return null
    }
  }, [])

  const execSlashCommand = useCallback((cmd) => {
    try {
      const editor = editorRef.current
      if (!editor) return

      if (cmd.command === 'uploadImage') {
        editor.execute('uploadImage')
      } else if (cmd.command === 'link') {
        const url = prompt('Введите URL ссылки:')
        if (!url) return
        editor.model.change(writer => {
          const sel = editor.model.document.selection
          const pos = sel.getFirstPosition()
          if (!pos) return
          const parent = pos.parent
          const slashPos = findSlashPosition(writer, parent, pos)
          if (slashPos) writer.setSelection(writer.createRange(slashPos, pos))
        })
        editor.execute('delete')
        editor.execute('link', url)
      } else if (cmd.command === 'mediaEmbed') {
        const url = prompt('Введите URL видео:')
        if (!url) return
        editor.model.change(writer => {
          const sel = editor.model.document.selection
          const pos = sel.getFirstPosition()
          if (!pos) return
          const parent = pos.parent
          const slashPos = findSlashPosition(writer, parent, pos)
          if (slashPos) writer.setSelection(writer.createRange(slashPos, pos))
        })
        editor.execute('delete')
        editor.execute('mediaEmbed', url)
      } else {
        editor.model.change(writer => {
          const sel = editor.model.document.selection
          const pos = sel.getFirstPosition()
          if (!pos) return
          const parent = pos.parent
          const slashPos = findSlashPosition(writer, parent, pos)
          if (slashPos) writer.setSelection(writer.createRange(slashPos, pos))
        })
        editor.execute('delete')
        editor.execute(cmd.command, ...(cmd.args || []))
      }

      setSlashMenu({ visible: false, x: 0, y: 0, query: '' })
      editor.editing.view.focus()
    } catch (e) {
      console.error('[SlashMenu] execSlashCommand error:', e)
    }
  }, [])

  function findSlashPosition(writer, parent, pos) {
    const range = writer.createRange(
      writer.createPositionAt(parent, 0),
      pos
    )
    let textBefore = ''
    const textSegments = []
    for (const value of range.getWalker({ ignoreElementEnd: true })) {
      if (value.item.is('text')) {
        textBefore += value.item.data
        textSegments.push({ text: value.item.data, node: value.item })
      }
    }

    const slashIdx = textBefore.lastIndexOf('/')
    if (slashIdx === -1) return null
    if (slashIdx > 0 && textBefore[slashIdx - 1] !== ' ' && textBefore[slashIdx - 1] !== '\n') return null

    let accumulated = 0
    for (const seg of textSegments) {
      if (slashIdx < accumulated + seg.text.length) {
        return writer.createPositionAt(seg.node, slashIdx - accumulated)
      }
      accumulated += seg.text.length
    }
    return null
  }

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
          content: data.content ? `<h1>${data.title}</h1>${data.content}` : '',
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
      .catch(e => { setError(e.message); goTo(1) })
      .finally(() => setLoadingPost(false))
  }, [slug, user])

  useEffect(() => {
    function handleClick(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) setShowSearch(false)
      if (slashMenuRef.current && !slashMenuRef.current.contains(e.target)) {
        setSlashMenu(s => ({ ...s, visible: false }))
      }
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  function goTo(s) {
    setStep(s)
  }

  useEffect(() => {
    const scrollToTop = () => {
      window.scroll(0, 0)
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
    }
    scrollToTop()
    setTimeout(scrollToTop, 50)
  }, [step])

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
    const content = stripTitleFromContent(fullHtml)
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
      fetch('/api/mobile/me/', { credentials: 'same-origin' })
        .then(r => r.ok ? r.json() : null)
        .then(u => { if (u) setUser(u) })
        .catch(() => {})
      navigate(`/post/${data.slug || slug}/`)
    } catch (err) {
      setError(err.message)
    }
    setSubmitting(false)
  }

  const steps = [{ n: 1, t: 'Тип поста' }, { n: 2, t: 'Редактор' }, { n: 3, t: 'Настройки' }]

  if (loading || loadingPost) return <AddPostSkeleton />

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
  onReady={(editor) => {
    editorRef.current = editor
    editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
      return new MyUploadAdapter(loader)
    }

    editor.editing.view.document.on('keydown', (evt, data) => {
      if (data.keyCode === 27) {
        setSlashMenu({ visible: false, x: 0, y: 0, query: '' })
      }
    })
  }}
  onChange={(event, editor) => {
    let query = null
    try { query = getSlashQuery(editor) } catch (e) { console.error('[SlashMenu] onChange error:', e) }

    if (hideSlashTimeout.current) clearTimeout(hideSlashTimeout.current)

    if (query !== null) {
      try {
        const nativeSel = window.getSelection()
        let x = 40, y = 40
        if (nativeSel && nativeSel.rangeCount) {
          const rect = nativeSel.getRangeAt(0).getBoundingClientRect()
          const editorEl = document.querySelector('.editor-container')
          const editorRect = editorEl?.getBoundingClientRect()
          if (rect && editorRect) {
            x = rect.left - editorRect.left
            y = rect.bottom - editorRect.top + 4
          }
        }
        setSlashMenu({ visible: true, x, y, query })
      } catch (e) {
        console.error('[SlashMenu] positioning error:', e)
        setSlashMenu({ visible: true, x: 40, y: 40, query })
      }
      f('content', editor.getData())
    } else {
      f('content', editor.getData())
      hideSlashTimeout.current = setTimeout(() => {
        setSlashMenu(s => s.visible ? { ...s, visible: false } : s)
      }, 100)
    }
  }}
  onError={(error, details) => {
    console.error('CKEditor error:', error, details)
  }}
/>
                    )}
                    {slashMenu.visible && (
                      <div className="slash-menu" ref={slashMenuRef}
                        style={{ left: slashMenu.x, top: slashMenu.y }}>
                        <div className="slash-menu-header">
                          <i className="fas fa-slash" /> Форматирование
                        </div>
                        <div className="slash-menu-items">
                          {SLASH_COMMANDS.filter(c => {
                            if (c.separator) return false
                            const q = slashMenu.query.toLowerCase()
                            if (!q) return true
                            return c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
                          }).map(cmd => (
                            <div key={cmd.id} className="slash-menu-item"
                              onMouseDown={(e) => { e.preventDefault(); execSlashCommand(cmd) }}>
                              <div className="slash-menu-item-icon">
                                <i className={cmd.icon} />
                              </div>
                              <div className="slash-menu-item-info">
                                <span className="slash-menu-item-label">{cmd.label}</span>
                                <span className="slash-menu-item-group">{cmd.group}</span>
                              </div>
                            </div>
                          ))}
                          {SLASH_COMMANDS.filter(c => {
                            if (c.separator) return false
                            const q = slashMenu.query.toLowerCase()
                            if (!q) return true
                            return c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
                          }).length === 0 && (
                            <div className="slash-menu-empty">Ничего не найдено</div>
                          )}
                        </div>
                      </div>
                    )}
                    </div>
                  </div>
                  <div className="step-rules">
                    <div className="step-rules-header" onClick={() => setShowRules(s => !s)}>
                      <div className="step-rules-toggle">
                        <i className={`fas ${showRules ? 'fa-chevron-down' : 'fa-chevron-right'}`}></i>
                        <i className="fas fa-clipboard-list"></i>
                        <span>Правила для «{POST_TYPES.find(pt => pt.value === form.post_type)?.title || 'Поста'}»</span>
                      </div>
                      {!showRules && (
                        <span className="step-rules-hint">Нажмите, чтобы посмотреть</span>
                      )}
                    </div>
                    {showRules && (
                      <div className="step-rules-body">
                        <ul className="step-rules-list">
                          {POST_TYPES.find(pt => pt.value === form.post_type)?.rules.map((rule, i) => (
                            <li key={i}><i className="fas fa-check-circle"></i> {rule}</li>
                          ))}
                        </ul>
                      </div>
                    )}
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
