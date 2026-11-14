import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getCSRFToken } from '../csrf'
import { importFromHabr, importFromGithub } from '../api'
import Sidebar from '../components/Sidebar/Sidebar'
import { AddPostSkeleton } from '../components/Skeleton'
import { CODE_LANGUAGES, toDatetimeLocal } from '../reviewMeta'
import { CKEditor } from '@ckeditor/ckeditor5-react'
import 'ckeditor5/ckeditor5.css'
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

function csrfHeaders() {
  const token = getCSRFToken()
  return token ? { 'X-CSRFToken': token } : {}
}

function extractTitle(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  const block = div.querySelector('h1, h2, h3, p')
  const text = (block?.textContent || div.textContent || '')
    .replace(/\u00a0/g, ' ')
    .trim()
  return text.split('\n')[0].trim().slice(0, 200)
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
    const token = getCSRFToken()
    const res = await fetch('/upload/', {
      method: 'POST',
      body: fd,
      credentials: 'same-origin',
      headers: token ? { 'X-CSRFToken': token } : {},
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
  { value: 'review',    icon: 'fa-code',          title: 'Разбор',  desc: 'Запрос на разбор кода',
    rules: [
      'Вставьте фрагмент кода, который хотите разобрать',
      'Укажите язык и фокус — так разбор будет точнее',
      'Не вставляйте секреты: токены, пароли и приватные ключи',
      'Один разбор — один цельный фрагмент кода',
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
  const [importUrl, setImportUrl] = useState('')
  const [importing, setImporting] = useState(false)
  const [importStatus, setImportStatus] = useState(null)
  const [githubUrl, setGithubUrl] = useState('')
  const [importingGithub, setImportingGithub] = useState(false)
  const [githubStatus, setGithubStatus] = useState(null)
  const [githubFiles, setGithubFiles] = useState([])
  const searchRef = useRef(null)
  const editorRef = useRef(null)

  const [draftStatus, setDraftStatus] = useState('idle')
  const dirtyRef = useRef(false)
  const draftSlugRef = useRef(null)
  const savePromiseRef = useRef(null)
  const draftSnapshotRef = useRef('')
  const submittingRef = useRef(false)
  const lastLoadedContentRef = useRef(null)
  const draftTimerRef = useRef(null)
  const autoSaveRef = useRef(null)

  const [showRules, setShowRules] = useState(false)
  const [slashMenu, setSlashMenu] = useState({ visible: false, x: 0, y: 0, query: '' })
  const [slashIndex, setSlashIndex] = useState(0)
  const slashMenuRef = useRef(null)
  const hideSlashTimeout = useRef(null)
  const slashIndexRef = useRef(slashIndex)

  const visibleSlashCommands = useMemo(() => {
    const q = slashMenu.query.toLowerCase()
    return SLASH_COMMANDS.filter(c => {
      if (c.separator) return false
      if (!q) return true
      return c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
    })
  }, [slashMenu.query])

  useEffect(() => {
    slashIndexRef.current = slashIndex
  }, [slashIndex])

  useEffect(() => {
    if (slashMenu.visible) {
      // Сброс выбранного пункта при новом запросе слеш-меню.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSlashIndex(0)
    }
  }, [slashMenu.visible, slashMenu.query])

  useEffect(() => {
    if (!slashMenu.visible || slashIndex < 0) return
    const el = slashMenuRef.current?.querySelector(`[data-slash-index="${slashIndex}"]`)
    el?.scrollIntoView({ block: 'nearest' })
  }, [slashMenu.visible, slashIndex])

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

  useEffect(() => {
    if (!slashMenu.visible) return

    function handleKeyDown(e) {
      const filtered = SLASH_COMMANDS.filter(c => {
        if (c.separator) return false
        const q = slashMenu.query.toLowerCase()
        if (!q) return true
        return c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
      })
      if (filtered.length === 0) return

      if (e.key === 'ArrowDown') {
        e.preventDefault()
        e.stopPropagation()
        setSlashIndex(i => Math.min(i + 1, filtered.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        e.stopPropagation()
        setSlashIndex(i => Math.max(i - 1, 0))
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault()
        e.stopPropagation()
        execSlashCommand(filtered[slashIndexRef.current])
      }
    }

    document.addEventListener('keydown', handleKeyDown, true)
    return () => document.removeEventListener('keydown', handleKeyDown, true)
  }, [slashMenu.visible, slashMenu.query, execSlashCommand])

  const [form, setForm] = useState({
    content: '',
    post_type: 'post',
    is_published: '1',
    cat: '',
    code_snippet: '',
    code_language: '',
    review_focus: '',
    review_deadline: '',
    review_budget: '',
  })

  const lastSavedReviewRef = useRef({
    code_snippet: '',
    code_language: '',
    review_focus: '',
  })

  // Снимок сохраняемых данных: нужен, чтобы не потерять правки, сделанные
  // во время уже отправленного автосохранения.
  useEffect(() => {
    draftSnapshotRef.current = JSON.stringify([
      form.content,
      form.post_type,
      form.is_published,
      form.cat,
      form.code_snippet,
      form.code_language,
      form.review_focus,
      form.review_deadline,
      form.review_budget,
      [...selectedTagIds].sort((a, b) => a - b),
    ])
  }, [form, selectedTagIds])

  useEffect(() => {
    if (loading) return
    if (!user) { navigate('/login/'); return }
    fetch('/api/mobile/categories/', { credentials: 'same-origin' })
      .then(r => r.json()).then(d => setCategories(d.results || d)).catch(() => {})
    fetch('/api/mobile/tags/', { credentials: 'same-origin' })
      .then(r => r.json()).then(d => setAllTags(d.results || d)).catch(() => {})
  }, [user, loading, navigate])

  useEffect(() => {
    // Результаты поиска тегов — производное состояние от запроса.
    // eslint-disable-next-line react-hooks/set-state-in-effect
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
    // Загрузка существующего черновика в редактор.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoadingPost(true)
    fetch(`/api/mobile/posts/${slug}/`, { credentials: 'same-origin' })
      .then(async r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        if (data.author?.id !== user.id) throw new Error('Это не ваша статья')
        const loadedContent = `<h1>${data.title}</h1>${data.content || ''}`
        lastLoadedContentRef.current = loadedContent
        dirtyRef.current = false
        const reviewRequest = data.review_request || {}
        const reviewDeadline = reviewRequest.deadline || data.review_deadline || ''
        const reviewBudget = reviewRequest.budget ?? data.review_budget ?? ''
        setForm({
          content: loadedContent,
          post_type: data.post_type || 'post',
          is_published: data.is_published ? '1' : '0',
          cat: data.category?.id || '',
          code_snippet: data.code_snippet || '',
          code_language: data.code_language || '',
          review_focus: data.review_focus || '',
          review_deadline: toDatetimeLocal(reviewDeadline),
          review_budget: reviewBudget === null || reviewBudget === undefined ? '' : String(reviewBudget),
        })
        lastSavedReviewRef.current = {
          code_snippet: data.code_snippet || '',
          code_language: data.code_language || '',
          review_focus: data.review_focus || '',
          review_deadline: toDatetimeLocal(reviewDeadline),
          review_budget: reviewBudget === null || reviewBudget === undefined ? '' : String(reviewBudget),
        }
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

  useEffect(() => {
    const contentDirty = lastLoadedContentRef.current !== null
      ? form.content !== lastLoadedContentRef.current
      : form.content.trim().length > 0
    const savedReview = lastSavedReviewRef.current
    const reviewDirty =
      form.code_snippet !== savedReview.code_snippet ||
      form.code_language !== savedReview.code_language ||
      form.review_focus !== savedReview.review_focus ||
      form.review_deadline !== savedReview.review_deadline ||
      form.review_budget !== savedReview.review_budget
    dirtyRef.current = contentDirty || reviewDirty
  }, [form.content, form.code_snippet, form.code_language, form.review_focus, form.review_deadline, form.review_budget])

  const debounceRef = useRef(null)
  useEffect(() => {
    if (step < 2) return
    if (!form.content.trim()) return
    if (!dirtyRef.current) return
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      autoSaveRef.current?.()
    }, 1000)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [form.content, form.code_snippet, form.code_language, form.review_focus, form.post_type, step])

  autoSaveRef.current = autoSaveDraft

  useEffect(() => {
    if (step < 2) return
    if (!form.content.trim()) return

    draftTimerRef.current = setInterval(() => {
      if (!dirtyRef.current) return
      autoSaveRef.current?.()
    }, 30000)

    return () => {
      if (draftTimerRef.current) clearInterval(draftTimerRef.current)
    }
  }, [step, form.content])

  useEffect(() => {
    function onBeforeUnload(e) {
      if (dirtyRef.current) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => window.removeEventListener('beforeunload', onBeforeUnload)
  }, [])

  useEffect(() => {
    return () => {
      if (draftTimerRef.current) clearInterval(draftTimerRef.current)
    }
  }, [])

  function setSaved() {
    setDraftStatus('saved')
    setTimeout(() => setDraftStatus('idle'), 3000)
  }

  async function autoSaveDraft() {
    if (submittingRef.current) return
    if (!form.content.trim()) return
    if (savePromiseRef.current) return savePromiseRef.current

    const snapshot = draftSnapshotRef.current
    const title = extractTitle(form.content)
    const content = stripTitleFromContent(form.content)
    if (!title || !content.trim()) return
    if (form.post_type === 'review' && (!form.code_snippet.trim() || !form.code_language.trim())) return

    const fd = new FormData()
    fd.append('title', title)
    fd.append('content', content)
    fd.append('post_type', form.post_type)
    // При редактировании сохраняем текущий статус, иначе автосохранение снимало бы публикацию.
    fd.append('is_published', isEditing ? form.is_published : '0')
    if (form.cat) fd.append('cat', form.cat)
    if (form.post_type === 'review') {
      fd.append('code_snippet', form.code_snippet)
      fd.append('code_language', form.code_language.trim())
      fd.append('review_focus', form.review_focus.trim())
      fd.append('review_deadline', form.review_deadline || '')
      fd.append('review_budget', form.review_budget === '' ? '' : String(form.review_budget))
    }
    selectedTagIds.forEach(id => fd.append('tags', id))

    const targetSlug = isEditing ? slug : draftSlugRef.current
    const promise = (async () => {
      setDraftStatus('saving')
      try {
        const res = await fetch(
          targetSlug ? `/api/mobile/posts/${targetSlug}/` : '/api/mobile/posts/',
          {
            method: targetSlug ? 'PATCH' : 'POST',
            headers: csrfHeaders(),
            credentials: 'same-origin',
            body: fd,
          }
        )
        if (!res.ok) throw new Error()
        const data = await res.json().catch(() => null)
        if (!targetSlug && data?.slug) {
          draftSlugRef.current = data.slug
        }
        return true
      } catch {
        setDraftStatus('error')
        return false
      }
    })()

    savePromiseRef.current = promise
    let saved
    try {
      saved = await promise
    } finally {
      savePromiseRef.current = null
    }

    if (!saved) return
    if (draftSnapshotRef.current === snapshot) {
      lastSavedReviewRef.current = {
        code_snippet: form.code_snippet,
        code_language: form.code_language,
        review_focus: form.review_focus,
        review_deadline: form.review_deadline,
        review_budget: form.review_budget,
      }
      dirtyRef.current = false
      setSaved()
      return
    }

    // Пока запрос летел, пользователь продолжил печатать — сохраняем ещё раз.
    dirtyRef.current = true
    if (!submittingRef.current) {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => autoSaveRef.current?.(), 500)
    }
  }

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

  async function handleHabrImport(event) {
    event?.preventDefault?.()
    if (importing) return
    const url = importUrl.trim()
    if (!url) {
      setImportStatus({ type: 'error', text: 'Вставьте ссылку на статью Хабра.' })
      return
    }
    setImporting(true)
    setImportStatus({ type: 'info', text: 'Загружаем статью, картинки и теги…' })
    try {
      const draft = await importFromHabr(url)
      const safeTitle = String(draft.title || '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      const html = `<h1>${safeTitle}</h1>${draft.content || ''}`
      setForm(prev => ({ ...prev, content: html }))
      editorRef.current?.setData(html)

      if (Array.isArray(draft.tags) && draft.tags.length && allTags.length) {
        const ids = new Set()
        for (const name of draft.tags) {
          const found = allTags.find(tag => tag.tag.toLowerCase() === String(name).toLowerCase())
          if (found) ids.add(found.id)
        }
        if (ids.size) setSelectedTagIds(ids)
      }

      if (draft.cover_url) {
        setPhotoPreview(draft.cover_url)
        setFileName('Обложка с Хабра')
        try {
          const response = await fetch(draft.cover_url, { credentials: 'same-origin' })
          if (response.ok) {
            const blob = await response.blob()
            const ext = (blob.type.split('/')[1] || 'jpg').replace('jpeg', 'jpg')
            setPhotoFile(new File([blob], `habr-cover.${ext}`, { type: blob.type || 'image/jpeg' }))
          }
        } catch {
          // Обложку можно выбрать вручную — импорт текста уже удался.
        }
      }

      setImportStatus({
        type: 'success',
        text: `Готово: «${draft.title}». Проверьте заголовок, теги и обложку перед публикацией.`,
      })
    } catch (err) {
      setImportStatus({
        type: 'error',
        text: err.message && !err.message.startsWith('HTTP')
          ? err.message
          : 'Не удалось импортировать статью. Проверьте ссылку и попробуйте ещё раз.',
      })
    }
    setImporting(false)
  }

  async function handleGithubImport(event) {
    event?.preventDefault?.()
    if (importingGithub) return
    const url = githubUrl.trim()
    if (!url) {
      setGithubStatus({ type: 'error', text: 'Вставьте ссылку на репозиторий, файл или pull request.' })
      return
    }
    setImportingGithub(true)
    setGithubStatus({ type: 'info', text: 'Загружаем файлы из GitHub…' })
    try {
      const draft = await importFromGithub(url)
      const files = Array.isArray(draft.files) ? draft.files : []
      setGithubFiles(files)
      const first = files[0]
      setForm(prev => ({
        ...prev,
        code_snippet: first?.content || draft.code_snippet || '',
        code_language: first?.language || draft.code_language || prev.code_language,
        review_focus: prev.review_focus || (draft.description || '').slice(0, 255),
      }))

      const currentHtml = editorRef.current?.getData() || form.content
      if (!extractTitle(currentHtml)) {
        const html = draft.content || `<h1>${String(draft.title || 'Импорт из GitHub')
          .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</h1>`
        setForm(prev => ({ ...prev, content: html }))
        editorRef.current?.setData(html)
      }

      setGithubStatus({
        type: 'success',
        text: files.length > 1
          ? `Загружено файлов: ${files.length}. Выберите нужный — код подставится в редактор.`
          : `Готово: ${first?.path || draft.title}. Проверьте код и параметры разбора.`,
      })
    } catch (err) {
      setGithubStatus({
        type: 'error',
        text: err.message && !err.message.startsWith('HTTP')
          ? err.message
          : 'Не удалось импортировать код. Проверьте ссылку и что репозиторий публичный.',
      })
    }
    setImportingGithub(false)
  }

  function applyGithubFile(file) {
    setForm(prev => ({
      ...prev,
      code_snippet: file.content || '',
      code_language: file.language || prev.code_language,
    }))
    setGithubStatus({ type: 'success', text: `В редактор подставлен файл ${file.path}.` })
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

  function validateReviewFields() {
    if (form.post_type !== 'review') return ''
    if (!form.code_snippet.trim()) return 'Вставьте код для разбора'
    if (!form.code_language.trim()) return 'Укажите язык кода'
    if (form.review_deadline) {
      const deadline = new Date(form.review_deadline)
      if (Number.isNaN(deadline.getTime())) return 'Проверьте дату дедлайна'
      if (deadline.getTime() <= Date.now()) return 'Дедлайн должен быть в будущем'
    }
    return ''
  }

  function handleEditorContinue() {
    const reviewError = validateReviewFields()
    if (reviewError) { setError(reviewError); return }
    setError('')
    goTo(3)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const fullHtml = form.content
    const title = extractTitle(fullHtml)
    const content = stripTitleFromContent(fullHtml)
    if (!title) { setError('Введите заголовок'); return }
    if (!content.trim()) { setError('Введите содержание'); return }
    const reviewError = validateReviewFields()
    if (reviewError) { setError(reviewError); return }

    // Дожидаемся автосохранения, иначе финальный запрос может создать второй черновик.
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
      debounceRef.current = null
    }
    if (savePromiseRef.current) {
      try { await savePromiseRef.current } catch { /* сохраним повторно при отправке */ }
    }

    submittingRef.current = true
    setError('')
    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('title', title)
      fd.append('content', content)
      fd.append('post_type', form.post_type)
      fd.append('is_published', form.is_published)
      if (form.cat) fd.append('cat', form.cat)
      if (form.post_type === 'review') {
        fd.append('code_snippet', form.code_snippet)
        fd.append('code_language', form.code_language.trim())
        fd.append('review_focus', form.review_focus.trim())
        fd.append('review_deadline', form.review_deadline || '')
        fd.append('review_budget', form.review_budget === '' ? '' : String(form.review_budget))
      }
      selectedTagIds.forEach(id => fd.append('tags', id))
      if (photoFile) fd.append('photo', photoFile)

      const targetSlug = isEditing ? slug : draftSlugRef.current
      const url = targetSlug ? `/api/mobile/posts/${targetSlug}/` : '/api/mobile/posts/'
      const method = targetSlug ? 'PATCH' : 'POST'
      const res = await fetch(url, {
        method,
        headers: csrfHeaders(),
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
    submittingRef.current = false
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

              {step >= 2 && draftStatus !== 'idle' && (
                <div style={{ padding: '8px 14px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 8, marginBottom: 12, fontSize: '0.85rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <i className={`fas ${draftStatus === 'saving' ? 'fa-spinner fa-spin' : draftStatus === 'saved' ? 'fa-check-circle' : 'fa-exclamation-circle'}`}
                    style={{ color: draftStatus === 'saved' ? '#16a34a' : draftStatus === 'error' ? '#dc2626' : 'var(--muted)' }} />
                  {draftStatus === 'saving' && 'Сохранение черновика...'}
                  {draftStatus === 'saved' && 'Черновик сохранён'}
                  {draftStatus === 'error' && 'Ошибка сохранения черновика'}
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
                  {!isEditing && (
                    <section className="habr-import" aria-label="Импорт статьи с Хабра">
                      <div className="habr-import-icon" aria-hidden="true">
                        <i className="fas fa-file-import" />
                      </div>
                      <div className="habr-import-body">
                        <h3>Переезжаете с Хабра?</h3>
                        <p>Вставьте ссылку на статью — перенесём текст, картинки и теги в черновик. Оригинал останется на Хабре.</p>
                        <div className="habr-import-form">
                          <label htmlFor="habr-import-url" className="visually-hidden">Ссылка на статью Хабра</label>
                          <input
                            id="habr-import-url"
                            type="url"
                            className="form-control"
                            placeholder="https://habr.com/ru/articles/123456/"
                            value={importUrl}
                            onChange={e => setImportUrl(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') handleHabrImport(e) }}
                            disabled={importing}
                          />
                          <button type="button" className="btn btn-primary" onClick={handleHabrImport} disabled={importing || !importUrl.trim()}>
                            {importing
                              ? <><i className="fas fa-spinner fa-spin" /> Импортируем…</>
                              : <><i className="fas fa-download" /> Импортировать</>}
                          </button>
                        </div>
                        {importStatus && (
                          <div className={`habr-import-status is-${importStatus.type}`} role="status">
                            <i className={`fas ${importStatus.type === 'success' ? 'fa-check-circle' : importStatus.type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}`} />
                            {importStatus.text}
                          </div>
                        )}
                      </div>
                    </section>
                  )}
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
                          {visibleSlashCommands.map((cmd, i) => (
                            <div key={cmd.id} className={`slash-menu-item${i === slashIndex ? ' highlighted' : ''}`}
                              data-slash-index={i}
                              onMouseDown={(e) => { e.preventDefault(); setSlashIndex(i); execSlashCommand(cmd) }}
                              onMouseEnter={() => setSlashIndex(i)}>
                              <div className="slash-menu-item-icon">
                                <i className={cmd.icon} />
                              </div>
                              <div className="slash-menu-item-info">
                                <span className="slash-menu-item-label">{cmd.label}</span>
                                <span className="slash-menu-item-group">{cmd.group}</span>
                              </div>
                            </div>
                          ))}
                          {visibleSlashCommands.length === 0 && (
                            <div className="slash-menu-empty">Ничего не найдено</div>
                          )}
                        </div>
                      </div>
                    )}
                    </div>
                  </div>

                  {form.post_type === 'review' && (
                    <div className="review-editor-block">
                      <div className="review-editor-header">
                        <h3><i className="fas fa-code" /> Параметры разбора</h3>
                        <p>Укажите язык и фокус, чтобы ревьюер понимал задачу. Код и язык обязательны.</p>
                      </div>
                      <div className="github-import">
                        <div className="github-import-head">
                          <i className="fab fa-github" aria-hidden="true" />
                          <div>
                            <strong>Импорт из GitHub</strong>
                            <span>Репозиторий, отдельный файл или pull request</span>
                          </div>
                        </div>
                        <div className="github-import-form">
                          <label htmlFor="github-import-url" className="visually-hidden">Ссылка на GitHub</label>
                          <input
                            id="github-import-url"
                            type="url"
                            className="form-control"
                            placeholder="https://github.com/owner/repo/pull/42"
                            value={githubUrl}
                            onChange={e => setGithubUrl(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') handleGithubImport(e) }}
                            disabled={importingGithub}
                          />
                          <button type="button" className="btn btn-primary" onClick={handleGithubImport} disabled={importingGithub || !githubUrl.trim()}>
                            {importingGithub
                              ? <><i className="fas fa-spinner fa-spin" /> Загружаем…</>
                              : <><i className="fas fa-download" /> Импортировать</>}
                          </button>
                        </div>
                        {githubStatus && (
                          <div className={`github-import-status is-${githubStatus.type}`} role="status">
                            <i className={`fas ${githubStatus.type === 'success' ? 'fa-check-circle' : githubStatus.type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}`} />
                            {githubStatus.text}
                          </div>
                        )}
                        {githubFiles.length > 1 && (
                          <div className="github-import-files" aria-label="Файлы из GitHub">
                            {githubFiles.map(file => (
                              <button
                                key={file.path}
                                type="button"
                                className={`github-import-file${form.code_snippet === file.content ? ' is-active' : ''}`}
                                onClick={() => applyGithubFile(file)}
                                title={file.path}
                              >
                                <span className="github-import-file-path">{file.path}</span>
                                <span className="github-import-file-meta">
                                  {file.lines} стр.
                                  {file.additions != null && ` · +${file.additions}/−${file.deletions}`}
                                </span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label htmlFor="review-language">
                            <i className="fas fa-language" /> Язык кода <span className="review-required">*</span>
                          </label>
                          <input
                            id="review-language"
                            type="text"
                            className="form-control"
                            list="review-language-options"
                            value={form.code_language}
                            maxLength={50}
                            autoComplete="off"
                            placeholder="Например, JavaScript"
                            onChange={e => f('code_language', e.target.value)}
                          />
                          <datalist id="review-language-options">
                            {CODE_LANGUAGES.map(lang => (
                              <option key={lang} value={lang} />
                            ))}
                          </datalist>
                        </div>
                        <div className="form-group">
                          <label htmlFor="review-focus">
                            <i className="fas fa-crosshairs" /> Фокус разбора
                          </label>
                          <input
                            id="review-focus"
                            type="text"
                            className="form-control"
                            value={form.review_focus}
                            maxLength={255}
                            placeholder="Например, безопасность и обработка ошибок"
                            onChange={e => f('review_focus', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label htmlFor="review-deadline">
                            <i className="fas fa-hourglass-half" /> Дедлайн откликов
                          </label>
                          <input
                            id="review-deadline"
                            type="datetime-local"
                            className="form-control"
                            value={form.review_deadline}
                            onChange={e => f('review_deadline', e.target.value)}
                          />
                          <p className="review-field-hint">После этого времени новые отклики не принимаются.</p>
                        </div>
                        <div className="form-group">
                          <label htmlFor="review-budget">
                            <i className="fas fa-wallet" /> Бюджет, ₽
                          </label>
                          <input
                            id="review-budget"
                            type="number"
                            min="0"
                            max="10000000"
                            step="100"
                            className="form-control"
                            placeholder="Необязательно"
                            value={form.review_budget}
                            onChange={e => f('review_budget', e.target.value)}
                          />
                          <p className="review-field-hint">Ориентир для ревьюеров. Ставку можно обсудить в отклике.</p>
                        </div>
                      </div>
                      <div className="form-group">
                        <label htmlFor="review-code">
                          <i className="fas fa-terminal" /> Код <span className="review-required">*</span>
                        </label>
                        <textarea
                          id="review-code"
                          className="form-control review-code-input"
                          rows={16}
                          value={form.code_snippet}
                          spellCheck={false}
                          autoCapitalize="off"
                          autoCorrect="off"
                          placeholder={'function example() {\n  // вставьте фрагмент кода\n}'}
                          onChange={e => f('code_snippet', e.target.value)}
                        />
                      </div>
                      <p className="review-secret-hint">
                        <i className="fas fa-shield-alt" /> Не вставляйте секреты: токены, пароли и приватные ключи. Замените их заглушками.
                      </p>
                    </div>
                  )}

                  <div className="step-rules">
                    <button type="button" className="step-rules-header" onClick={() => setShowRules(s => !s)} aria-expanded={showRules}>
                      <div className="step-rules-toggle">
                        <i className={`fas ${showRules ? 'fa-chevron-down' : 'fa-chevron-right'}`}></i>
                        <i className="fas fa-clipboard-list"></i>
                        <span>Правила для «{POST_TYPES.find(pt => pt.value === form.post_type)?.title || 'Поста'}»</span>
                      </div>
                      {!showRules && (
                        <span className="step-rules-hint">Нажмите, чтобы посмотреть</span>
                      )}
                    </button>
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
                    <button type="button" className="btn btn-primary" onClick={handleEditorContinue}>
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
                      <i className={`fas ${form.is_published === '1' ? 'fa-paper-plane' : 'fa-save'}`}></i>{' '}
                      {submitting
                        ? 'Сохранение...'
                        : form.is_published === '1'
                          ? (isEditing ? 'Сохранить изменения' : 'Опубликовать')
                          : 'Сохранить черновик'}
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
