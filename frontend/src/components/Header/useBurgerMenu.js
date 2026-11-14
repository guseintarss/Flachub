import { useCallback, useEffect } from 'react'

export function useBurgerMenu() {
  const closeMenu = useCallback(() => {
    document.querySelector('.site-header')?.classList.remove('open')
    document.body.style.overflow = ''
  }, [])

  useEffect(() => {
    const burger = document.getElementById('burger')
    const siteHeader = document.querySelector('.site-header')
    const topNav = document.querySelector('.top-nav')
    let overlay = document.getElementById('menu-overlay')

    if (!overlay) {
      overlay = document.createElement('div')
      overlay.id = 'menu-overlay'
      overlay.className = 'menu-overlay'
      siteHeader?.insertBefore(overlay, siteHeader.firstChild)
    }

    function openMenu() {
      siteHeader?.classList.add('open')
      document.body.style.overflow = 'hidden'
    }

    function onBurgerClick(e) {
      e.stopPropagation()
      e.preventDefault()
      if (siteHeader?.classList.contains('open')) {
        closeMenu()
      } else {
        openMenu()
      }
    }

    function onOverlayClick(e) {
      e.stopPropagation()
      closeMenu()
    }

    function onKeyDown(e) {
      if (e.key === 'Escape' && siteHeader?.classList.contains('open')) {
        closeMenu()
      }
    }

    function onLinkClick() {
      closeMenu()
    }

    burger?.addEventListener('click', onBurgerClick)
    overlay?.addEventListener('click', onOverlayClick)
    document.addEventListener('keydown', onKeyDown)
    topNav?.querySelectorAll('a').forEach(link => link.addEventListener('click', onLinkClick))

    return () => {
      burger?.removeEventListener('click', onBurgerClick)
      overlay?.removeEventListener('click', onOverlayClick)
      document.removeEventListener('keydown', onKeyDown)
      topNav?.querySelectorAll('a').forEach(link => link.removeEventListener('click', onLinkClick))
      closeMenu()
    }
  }, [closeMenu])

  return { closeMenu }
}
