import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FormSkeleton } from '../components/Skeleton'

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
          banner_gradient_start: data.banner_gradient_start || '#0c6acf',
          banner_gradient_end: data.banner_gradient_end || '#764ba2',
          data_birth: '',
          phone_namber: '',
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

      if (form.data_birth) fd.append('data_birth', form.data_birth)
      if (form.phone_namber) fd.append('phone_namber', form.phone_namber)
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
    { start: '#0c6acf', end: '#764ba2' },
    { start: '#10b981', end: '#34d399' },
    { start: '#f59e0b', end: '#ef4444' },
    { start: '#8b5cf6', end: '#ec4899' },
    { start: '#06b6d4', end: '#3b82f6' },
    { start: '#1f2937', end: '#4b5563' },
    { start: '#dc2626', end: '#f97316' },
    { start: '#0f172a', end: '#1e3a5f' },
  ]

  return (
    <main className="page">
      <div className="pg-container">
        <div className="post edit-profile-page">
          <h1>🛠 Редактирование профиля</h1>

          {error && (
            <div className="alert alert-danger" style={{ padding: '12px 16px', background: '#fee2e2', color: '#dc2626', borderRadius: 8, marginBottom: 16 }}>
              {error}
            </div>
          )}
          {success && (
            <div className="alert alert-success" style={{ padding: '12px 16px', background: '#d1fae5', color: '#065f46', borderRadius: 8, marginBottom: 16 }}>
              Профиль успешно сохранён!
            </div>
          )}

          <form method="post" encType="multipart/form-data" onSubmit={handleSubmit}>
            <div className="avatar-preview-container">
              <div className="avatar-wrappers">
                <img id="avatar-preview" className="user-img-article"
                  src={avatarPreview || '/media/users/default.png'}
                  alt="Аватар" />
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
                    <input type="tel" value={form.phone_namber} onChange={set('phone_namber')}
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

      <style>{`
        .edit-profile-page { max-width: 800px; margin: 0 auto; }
        .edit-profile-page h1 { margin-bottom: 30px; color: var(--text); }

        .avatar-preview-container {
          text-align: center; margin-bottom: 30px; padding: 20px;
          background: var(--bg); border-radius: var(--radius);
        }
        .avatar-wrappers {
          position: relative; display: inline-block; margin-bottom: 15px;
        }
        .avatar-wrappers .user-img-article {
          width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
          border: 4px solid var(--border); transition: all 0.3s ease;
        }
        .avatar-overlay {
          position: absolute; top: 0; left: 0; width: 100%; height: 100%;
          background: rgba(0,0,0,0.6); border-radius: 50%;
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          color: white; cursor: pointer; opacity: 0; transition: opacity 0.3s ease;
        }
        .avatar-overlay i { font-size: 24px; margin-bottom: 5px; }
        .avatar-overlay span { font-size: 14px; font-weight: 600; }
        .avatar-wrappers:hover .avatar-overlay { opacity: 1; }
        .avatar-wrappers:hover .user-img-article { transform: scale(1.05); border-color: var(--primary); }

        .avatar-actions {
          display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px;
        }
        .avatar-actions input[type="file"] { display: none; }
        .avatar-help { color: var(--muted); font-size: 0.9rem; margin: 0; }

        .form-sections { margin-bottom: 30px; }
        .form-section {
          background: var(--bg); padding: 20px; border-radius: var(--radius); margin-bottom: 20px;
        }
        .form-section h3 {
          margin-bottom: 20px; color: var(--text); font-size: 1.2rem;
          display: flex; align-items: center; gap: 10px;
        }
        .form-section h3 i { color: var(--primary); }

        .form-row {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px; margin-bottom: 20px;
        }
        .form-group { display: flex; flex-direction: column; }
        .form-group label {
          font-weight: 600; margin-bottom: 8px; color: var(--text);
          display: flex; align-items: center; gap: 8px;
        }
        .form-group label i { color: var(--primary); font-size: 14px; }
        .form-group input, .form-group textarea, .form-group select {
          padding: 12px 15px; border: 2px solid var(--border); border-radius: 8px;
          font-size: 1rem; background: var(--surface); color: var(--text);
          transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
          outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(12,106,207,0.1);
        }
        .form-group input:disabled { opacity: 0.6; cursor: not-allowed; }
        .form-group textarea { min-height: 100px; resize: vertical; }

        .form-group input[type="color"] { width: 100%; height: 60px; padding: 5px; cursor: pointer; }
        .form-group input[type="color"]:hover { border-color: var(--primary); }

        .form-text { color: var(--muted); font-size: 0.85rem; margin-top: 5px; }
        .form-error { color: #dc3545; font-size: 0.85rem; margin-top: 5px; }

        .live-banner-preview { margin-bottom: 20px; position: relative; }
        .preview-label {
          display: inline-flex; align-items: center; gap: 6px;
          margin-top: 8px; font-size: 0.8rem; color: var(--muted);
        }

        .color-row { gap: 16px; }
        .color-input-wrapper {
          position: relative; display: flex; align-items: center; gap: 12px;
        }
        .color-input-wrapper input[type="color"] { width: 60px; height: 50px; flex-shrink: 0; }
        .color-value {
          font-family: 'JetBrains Mono', 'Consolas', monospace;
          font-size: 0.95rem; color: var(--muted); background: var(--bg);
          padding: 12px 14px; border-radius: 8px; border: 1px solid var(--border); flex: 1;
        }

        .gradient-presets { margin-top: 16px; }
        .presets-label {
          display: block; font-size: 0.85rem; color: var(--muted);
          margin-bottom: 10px; font-weight: 500;
        }
        .presets-grid { display: flex; gap: 8px; flex-wrap: wrap; }
        .preset-btn {
          width: 44px; height: 44px; border: 2px solid var(--border);
          border-radius: 10px; padding: 0; cursor: pointer;
          overflow: hidden; transition: all 0.2s ease; background: none;
        }
        .preset-btn span { display: block; width: 100%; height: 100%; }
        .preset-btn:hover { transform: scale(1.1); border-color: var(--primary); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .preset-btn.active { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(12,106,207,0.2); }

        .image-upload-group input[type="file"]:hover { border-color: var(--primary); background: rgba(12,106,207,0.03); }

        .current-banner-info {
          display: flex; align-items: center; gap: 16px; padding: 12px;
          background: var(--bg); border: 1px solid var(--border);
          border-radius: 10px; margin-bottom: 12px;
        }
        .current-banner-preview { flex-shrink: 0; width: 120px; height: 50px; border-radius: 8px; overflow: hidden; }
        .current-banner-preview img { width: 100%; height: 100%; object-fit: cover; }
        .current-banner-actions {
          display: flex; align-items: center; gap: 12px; flex-wrap: wrap; flex: 1;
        }
        .clear-banner-checkbox { display: inline-flex; align-items: center; cursor: pointer; user-select: none; }
        .clear-banner-checkbox input[type="checkbox"] { display: none; }
        .clear-banner-label {
          display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px;
          font-size: 0.85rem; font-weight: 600; border-radius: 8px; white-space: nowrap;
          border: 2px solid #dc3545; color: #dc3545; background: transparent;
          transition: all 0.2s ease; cursor: pointer;
        }
        .clear-banner-label:hover { background: #dc3545; color: #fff; }
        .clear-banner-checkbox input[type="checkbox"]:checked + .clear-banner-label { background: #dc3545; color: #fff; }
        .current-banner-text {
          display: inline-flex; align-items: center; gap: 6px;
          font-size: 0.85rem; color: #10b981; font-weight: 500;
        }

        .privacy-toggles { display: flex; flex-direction: column; gap: 14px; }
        .privacy-toggle {
          display: flex; align-items: center; gap: 12px; cursor: pointer; user-select: none;
        }
        .privacy-toggle input { display: none; }
        .toggle-track {
          width: 44px; height: 24px; border-radius: 12px; background: var(--border);
          position: relative; transition: background 0.25s ease; flex-shrink: 0;
        }
        .toggle-thumb {
          width: 20px; height: 20px; border-radius: 50%; background: #fff;
          position: absolute; top: 2px; left: 2px; transition: transform 0.25s ease;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .privacy-toggle input:checked + .toggle-track { background: var(--primary); }
        .privacy-toggle input:checked + .toggle-track .toggle-thumb { transform: translateX(20px); }
        .toggle-label {
          display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: var(--text);
        }
        .toggle-label i { color: var(--primary); font-size: 0.9rem; }

        .form-actions {
          display: flex; gap: 15px; justify-content: flex-start;
          margin-top: 30px; padding-top: 30px; border-top: 1px solid var(--border);
        }
        .form-actions .btn {
          display: inline-flex; align-items: center; gap: 8px;
          padding: 12px 24px; font-weight: 600;
        }

        @media (max-width: 768px) {
          .form-row { grid-template-columns: 1fr; }
          .form-actions { flex-direction: column; }
          .form-actions .btn { width: 100%; justify-content: center; }
          .avatar-wrappers .user-img-article { width: 120px; height: 120px; }
          #live-banner-bg { height: 120px !important; }
          .presets-grid { gap: 6px; }
          .preset-btn { width: 38px; height: 38px; }
          .color-input-wrapper { flex-direction: column; align-items: stretch; }
          .color-input-wrapper input[type="color"] { width: 100%; height: 45px; }
          .color-value { text-align: center; }
          .current-banner-info { flex-direction: column; align-items: stretch; gap: 10px; }
          .current-banner-preview { width: 100%; height: 60px; }
          .current-banner-actions { flex-direction: column; align-items: stretch; }
          .clear-banner-label { width: 100%; justify-content: center; }
          .current-banner-text { justify-content: center; }
        }
      `}</style>
    </main>
  )
}

export default EditProfilePage
