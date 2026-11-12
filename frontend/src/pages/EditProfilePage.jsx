import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FormSkeleton } from '../components/Skeleton'

function formatPhone(raw) {
  const digits = raw.replace(/\D/g, '')
  if (!digits.length) return ''
  const d = digits.startsWith('8') ? '7' + digits.slice(1) : digits
  if (d.length <= 1) return '+7'
  if (d.length <= 4) return `+7 (${d.slice(1)}`
  if (d.length <= 7) return `+7 (${d.slice(1, 4)}) ${d.slice(4)}`
  if (d.length <= 9) return `+7 (${d.slice(1, 4)}) ${d.slice(4, 7)}-${d.slice(7)}`
  return `+7 (${d.slice(1, 4)}) ${d.slice(4, 7)}-${d.slice(7, 9)}-${d.slice(9, 11)}`
}

function EditProfilePage() {
  const { user, loading: authLoading, setUser } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const [bannerPreview, setBannerPreview] = useState(null)
  const [avatarPreview, setAvatarPreview] = useState(null)
  const [activePreset, setActivePreset] = useState(null)
  const [bannerImageFile, setBannerImageFile] = useState(null)
  const [clearBanner, setClearBanner] = useState(false)
  const [clearAvatar, setClearAvatar] = useState(false)

  const avatarInputRef = useRef(null)
  const bannerInputRef = useRef(null)

  const fetchProfile = useCallback(async () => {
    try {
      const res = await fetch('/api/mobile/me/')
      if (res.ok) {
        const data = await res.json()
        setForm({
          username: data.username || '',
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          email: data.email || '',
          about_me: data.bio || '',
          banner_gradient_start: data.banner_gradient_start || '#2c5d48',
          banner_gradient_end: data.banner_gradient_end || '#7a8f63',
          data_birth: data.data_birth || '',
          phone_namber: formatPhone(data.phone_namber || ''),
          show_email: data.show_email ?? true,
          show_phone: data.show_phone ?? true,
          show_birth_date: data.show_birth_date ?? true,
        })
        setAvatarPreview(data.avatar || null)
        setBannerPreview(data.avatar ? null : 'gradient')
      }
    } catch (e) {
      setError('Ошибка загрузки профиля')
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        navigate('/login/', { replace: true })
        return
      }
      fetchProfile()
    }
  }, [authLoading, user, navigate, fetchProfile])

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  function handlePhoneChange(e) {
    setForm(f => ({ ...f, phone_namber: formatPhone(e.target.value) }))
  }

  function updateBannerPreview() {
    if (bannerImageFile) {
      const reader = new FileReader()
      reader.onload = e => setBannerPreview(e.target.result)
      reader.readAsDataURL(bannerImageFile)
    } else if (!clearBanner) {
      setBannerPreview('gradient')
    }
  }

  useEffect(() => {
    if (bannerPreview === 'gradient' && form) {
      setBannerPreview(null)
    }
  }, [form?.banner_gradient_start, form?.banner_gradient_end])

  function handleAvatarChange(e) {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      alert('Размер файла не должен превышать 5MB')
      e.target.value = ''
      return
    }
    setClearAvatar(false)
    const reader = new FileReader()
    reader.onload = e => setAvatarPreview(e.target.result)
    reader.readAsDataURL(file)
  }

  function handleRemoveAvatar() {
    if (confirm('Вы уверены что хотите удалить аватарку?')) {
      setClearAvatar(true)
      setAvatarPreview(null)
      if (avatarInputRef.current) avatarInputRef.current.value = ''
    }
  }

  function handleBannerImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setBannerImageFile(file)
    setClearBanner(false)
    const reader = new FileReader()
    reader.onload = e => setBannerPreview(e.target.result)
    reader.readAsDataURL(file)
  }

  function handlePreset(start, end, idx) {
    setForm(f => ({ ...f, banner_gradient_start: start, banner_gradient_end: end }))
    setBannerImageFile(null)
    setClearBanner(false)
    setActivePreset(idx)
    if (bannerInputRef.current) bannerInputRef.current.value = ''
    setBannerPreview('gradient')
  }

  function handleClearBanner() {
    if (confirm('Вы уверены что хотите удалить изображение баннера? Будет использован градиент.')) {
      setClearBanner(true)
      setBannerImageFile(null)
      if (bannerInputRef.current) bannerInputRef.current.value = ''
      setBannerPreview('gradient')
    }
  }

  function getCSRF() {
    const meta = document.querySelector('meta[name="csrf-token"]')
    if (meta) return meta.getAttribute('content')
    const m = document.cookie.match(/csrftoken=([^;]+)/)
    return m ? m[1] : ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSuccess(false)
    setSaving(true)

    try {
      const fd = new FormData()
      fd.append('first_name', form.first_name)
      fd.append('last_name', form.last_name)
      fd.append('about_me', form.about_me)
      fd.append('banner_gradient_start', form.banner_gradient_start)
      fd.append('banner_gradient_end', form.banner_gradient_end)

      fd.append('data_birth', form.data_birth || '')
      fd.append('phone_namber', form.phone_namber || '')
      fd.append('show_email', form.show_email ? '1' : '0')
      fd.append('show_phone', form.show_phone ? '1' : '0')
      fd.append('show_birth_date', form.show_birth_date ? '1' : '0')

      if (clearAvatar) {
        fd.append('photo_clear', 'true')
      } else if (avatarInputRef.current?.files[0]) {
        fd.append('photo', avatarInputRef.current.files[0])
      }

      if (clearBanner) {
        fd.append('banner_image_clear', 'true')
      } else if (bannerImageFile) {
        fd.append('banner_image', bannerImageFile)
      }

      const headers = {}
      const csrf = getCSRF()
      if (csrf) headers['X-CSRFToken'] = csrf

      const res = await fetch('/api/mobile/me/', {
        method: 'PATCH',
        headers,
        credentials: 'same-origin',
        body: fd,
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text.slice(0, 200) || 'Ошибка сохранения')
      }

      const data = await res.json()
      setUser(data)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
      fetchProfile()
    } catch (e) {
      setError(e.message)
    }
    setSaving(false)
  }

  if (loading || authLoading) return <FormSkeleton />

  if (!form) return null

  const bannerBgStyle = bannerImageFile || (clearBanner)
    ? null
    : { background: `linear-gradient(135deg, ${form.banner_gradient_start} 0%, ${form.banner_gradient_end} 100%)` }

  const presets = [
    { start: '#2c5d48', end: '#7a8f63' },
    { start: '#6d5427', end: '#b39a5f' },
    { start: '#6b4a3a', end: '#b0836a' },
    { start: '#3d5560', end: '#7d95a0' },
    { start: '#544a63', end: '#928aa8' },
    { start: '#22302a', end: '#4c6355' },
    { start: '#7a3f2f', end: '#c07a55' },
    { start: '#1e2d26', end: '#3f5a4a' },
  ]

  return (
    <main className="page">
      <div className="pg-container">
        <div className="post edit-profile-page">
          <h1>Редактирование профиля</h1>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}
          {success && (
            <div className="alert alert-success" role="status">
              Профиль успешно сохранён!
            </div>
          )}

          <form method="post" encType="multipart/form-data" onSubmit={handleSubmit}>
            <div className="avatar-preview-container">
              <div className="avatar-wrappers">
                {avatarPreview ? (
                  <img id="avatar-preview" className="user-img-article"
                    src={avatarPreview} alt="Аватар" />
                ) : (
                  <div id="avatar-preview" className="user-img-article"
                    style={{
                      background: 'linear-gradient(135deg, #2f5d48, #7a8f63)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '3rem', fontWeight: 700, color: '#fff',
                    }}>
                    {user?.username?.[0]?.toUpperCase() || '?'}
                  </div>
                )}
                <label className="avatar-overlay" onClick={() => avatarInputRef.current?.click()}>
                  <i className="fas fa-camera" />
                  <span>Изменить</span>
                </label>
              </div>
              <div className="avatar-actions">
                <input ref={avatarInputRef} type="file" accept="image/*"
                  onChange={handleAvatarChange} style={{ display: 'none' }} />
                <button type="button" className="btn btn-sm btn-outline-danger" onClick={handleRemoveAvatar}>
                  <i className="fas fa-trash" /> Удалить
                </button>
              </div>
              <p className="avatar-help">
                <i className="fas fa-info-circle" /> Рекомендуемый размер: 400×400px. Форматы: JPG, PNG
              </p>
            </div>

            <div className="form-sections">
              <div className="form-section">
                <h3><i className="fas fa-user" /> Основная информация</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label><i className="fas fa-at" /> Логин</label>
                    <input type="text" value={form.username} disabled className="form-control" />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label><i className="fas fa-user" /> Имя</label>
                    <input type="text" value={form.first_name} onChange={set('first_name')}
                      className="form-control" placeholder="Ваше имя" />
                  </div>
                  <div className="form-group">
                    <label><i className="fas fa-user" /> Фамилия</label>
                    <input type="text" value={form.last_name} onChange={set('last_name')}
                      className="form-control" placeholder="Ваша фамилия" />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label><i className="fas fa-envelope" /> E-mail</label>
                    <input type="email" value={form.email} disabled className="form-control" />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h3><i className="fas fa-info-circle" /> Дополнительно</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label><i className="fas fa-align-left" /> О себе</label>
                    <textarea value={form.about_me} onChange={set('about_me')}
                      className="form-control" rows={4}
                      placeholder="Расскажите немного о себе..." maxLength={255} />
                    <small className="form-text">
                      Краткая информация о себе (максимум 255 символов)
                    </small>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label><i className="fas fa-calendar" /> Дата рождения</label>
                    <input type="date" value={form.data_birth} onChange={set('data_birth')}
                      className="form-control" />
                    <small className="form-text">
                      <i className="fas fa-info-circle" /> Формат: ГГГГ-ММ-ДД
                    </small>
                  </div>
                  <div className="form-group">
                    <label><i className="fas fa-phone" /> Номер телефона</label>
                    <input type="tel" value={form.phone_namber} onChange={handlePhoneChange} placeholder="+7 (___) ___-__-__"
                      className="form-control" placeholder="+7 (___) ___-__-__" />
                    <small className="form-text">
                      <i className="fas fa-info-circle" /> Например: 9991234567
                    </small>
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h3><i className="fas fa-shield-alt" /> Конфиденциальность</h3>
                <div className="privacy-toggles">
                  <label className="privacy-toggle">
                    <input type="checkbox" checked={form.show_email}
                      onChange={e => setForm(f => ({ ...f, show_email: e.target.checked }))} />
                    <span className="toggle-track">
                      <span className="toggle-thumb" />
                    </span>
                    <span className="toggle-label">
                      <i className="fas fa-envelope" /> Показывать email
                    </span>
                  </label>
                  <label className="privacy-toggle">
                    <input type="checkbox" checked={form.show_phone}
                      onChange={e => setForm(f => ({ ...f, show_phone: e.target.checked }))} />
                    <span className="toggle-track">
                      <span className="toggle-thumb" />
                    </span>
                    <span className="toggle-label">
                      <i className="fas fa-phone" /> Показывать телефон
                    </span>
                  </label>
                  <label className="privacy-toggle">
                    <input type="checkbox" checked={form.show_birth_date}
                      onChange={e => setForm(f => ({ ...f, show_birth_date: e.target.checked }))} />
                    <span className="toggle-track">
                      <span className="toggle-thumb" />
                    </span>
                    <span className="toggle-label">
                      <i className="fas fa-calendar" /> Показывать дату рождения
                    </span>
                  </label>
                </div>
              </div>

              <div className="form-section">
                <h3><i className="fas fa-palette" /> Кастомизация баннера профиля</h3>

                <div className="live-banner-preview">
                  <div id="live-banner-bg"
                    style={{
                      height: 160, borderRadius: 12, overflow: 'hidden',
                      transition: 'background 0.3s ease',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      ...(bannerPreview && bannerPreview !== 'gradient'
                        ? { background: `url(${bannerPreview}) center/cover no-repeat` }
                        : bannerBgStyle || { background: `linear-gradient(135deg, ${form.banner_gradient_start} 0%, ${form.banner_gradient_end} 100%)` }),
                    }} />
                  <span className="preview-label"><i className="fas fa-eye" /> Предпросмотр</span>
                </div>

                <div className="form-row color-row">
                  <div className="form-group color-group">
                    <label><i className="fas fa-fill-drip" /> Начало градиента</label>
                    <div className="color-input-wrapper">
                      <input type="color" value={form.banner_gradient_start}
                        onChange={e => {
                          setForm(f => ({ ...f, banner_gradient_start: e.target.value }))
                          setBannerImageFile(null)
                          setClearBanner(false)
                          setActivePreset(null)
                          if (bannerInputRef.current) bannerInputRef.current.value = ''
                        }} />
                      <span className="color-value">{form.banner_gradient_start}</span>
                    </div>
                  </div>
                  <div className="form-group color-group">
                    <label><i className="fas fa-fill-drip" /> Конец градиента</label>
                    <div className="color-input-wrapper">
                      <input type="color" value={form.banner_gradient_end}
                        onChange={e => {
                          setForm(f => ({ ...f, banner_gradient_end: e.target.value }))
                          setBannerImageFile(null)
                          setClearBanner(false)
                          setActivePreset(null)
                          if (bannerInputRef.current) bannerInputRef.current.value = ''
                        }} />
                      <span className="color-value">{form.banner_gradient_end}</span>
                    </div>
                  </div>
                </div>

                <div className="gradient-presets">
                  <span className="presets-label">Быстрые пресеты:</span>
                  <div className="presets-grid">
                    {presets.map((p, i) => (
                      <button key={i} type="button"
                        className={`preset-btn ${activePreset === i ? 'active' : ''}`}
                        onClick={() => handlePreset(p.start, p.end, i)}>
                        <span style={{ background: `linear-gradient(135deg, ${p.start}, ${p.end})` }} />
                      </button>
                    ))}
                  </div>
                </div>

                <div className="form-group image-upload-group" style={{ marginTop: 20 }}>
                  <label><i className="fas fa-image" /> Изображение баннера</label>
                  {bannerImageFile && (
                    <div className="current-banner-info">
                      <div className="current-banner-preview">
                        {bannerPreview && bannerPreview !== 'gradient' && (
                          <img src={bannerPreview} alt="Новый баннер" />
                        )}
                      </div>
                      <div className="current-banner-actions">
                        <label className="clear-banner-checkbox">
                          <input type="checkbox" checked={clearBanner}
                            onChange={handleClearBanner} />
                          <span className="clear-banner-label">
                            <i className="fas fa-trash" /> Удалить изображение
                          </span>
                        </label>
                        <span className="current-banner-text">
                          <i className="fas fa-check-circle" /> Новое изображение выбрано
                        </span>
                      </div>
                    </div>
                  )}
                  <input ref={bannerInputRef} type="file" accept="image/*"
                    onChange={handleBannerImageChange} className="form-control"
                    style={{ padding: 10, border: '2px dashed var(--border)', borderRadius: 8, cursor: 'pointer' }} />
                  <small className="form-text">
                    <i className="fas fa-lightbulb" /> Если загрузить изображение, оно будет использоваться вместо градиента. Рекомендуемый размер: 1200×300px.
                  </small>
                </div>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary btn-lg" disabled={saving}>
                <i className="fas fa-save" /> {saving ? 'Сохранение...' : 'Сохранить изменения'}
              </button>
              <Link to="/profile/" className="btn btn-secondary btn-lg">
                <i className="fas fa-arrow-left" /> Отмена
              </Link>
            </div>
          </form>

          <hr />
          <p>
            <Link to="/password/change/" className="text-decoration-none">
              <i className="fas fa-key" /> Изменить пароль
            </Link>
          </p>
        </div>
      </div>

    </main>
  )
}

export default EditProfilePage
