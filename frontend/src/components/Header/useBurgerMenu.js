import { useEffect } from 'react'

export function useBurgerMenu() {
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

    function closeMenu() {
      siteHeader?.classList.remove('open')
      document.body.style.overflow = ''
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

    function onNavClick(e) {
      e.stopPropagation()
    }

    burger?.addEventListener('click', onBurgerClick)
    overlay?.addEventListener('click', onOverlayClick)
    document.addEventListener('keydown', onKeyDown)
    if (topNav) {
      topNav.querySelectorAll('a').forEach(link => link.addEventListener('click', onLinkClick))
      topNav.addEventListener('click', onNavClick)
    }

    return () => {
      burger?.removeEventListener('click', onBurgerClick)
      overlay?.removeEventListener('click', onOverlayClick)
      document.removeEventListener('keydown', onKeyDown)
      if (topNav) {
        topNav.querySelectorAll('a').forEach(link => link.removeEventListener('click', onLinkClick))
        topNav.removeEventListener('click', onNavClick)
      }
      document.body.style.overflow = ''
    }
  }, [])
}
