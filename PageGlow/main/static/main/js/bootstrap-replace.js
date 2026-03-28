/**
 * PageGlow - Custom JS для замены Bootstrap функциональности
 * Dropdown, Modal, Collapse, Alert
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // =====================================================
    // DROPDOWN
    // =====================================================
    
    function initDropdowns() {
        document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(toggle => {
            const target = toggle.getAttribute('data-bs-target');
            const dropdown = target ? document.querySelector(target) : toggle.nextElementSibling;
            
            if (!dropdown) return;
            
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Закрыть все остальные dropdowns
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    if (menu !== dropdown) {
                        menu.classList.remove('show');
                    }
                });
                
                // Переключить текущий
                dropdown.classList.toggle('show');
            });
        });
        
        // Закрытие при клике вне
        document.addEventListener('click', function(e) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                const toggle = menu.previousElementSibling;
                if (!toggle || (!toggle.contains(e.target) && !menu.contains(e.target))) {
                    menu.classList.remove('show');
                }
            });
        });
    }
    
    // =====================================================
    // MODAL
    // =====================================================
    
    function initModals() {
        // Обработчик для кнопок с data-bs-toggle="modal"
        document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('data-bs-target');
                const modal = document.querySelector(targetId);
                
                if (modal) {
                    openModal(modal);
                }
            });
        });
        
        // Обработчик для кнопок закрытия модальных окон
        document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(closeBtn => {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const modal = this.closest('.modal');
                if (modal) {
                    closeModal(modal);
                }
            });
        });
        
        // Закрытие по клику вне modal-content
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal(modal);
                }
            });
        });
        
        // Закрытие по Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show').forEach(modal => {
                    closeModal(modal);
                });
            }
        });
    }
    
    function openModal(modal) {
        // Создать backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.id = 'modalBackdrop';
        document.body.appendChild(backdrop);
        
        // Показать модальное окно
        modal.style.display = 'flex';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Фокус на первом элементе
        const firstInput = modal.querySelector('input, button, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
    
    function closeModal(modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.style.overflow = '';
        
        // Удалить backdrop
        const backdrop = document.getElementById('modalBackdrop');
        if (backdrop) {
            backdrop.remove();
        }
    }
    
    // =====================================================
    // COLLAPSE
    // =====================================================
    
    function initCollapse() {
        document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(trigger => {
            const targetId = trigger.getAttribute('data-bs-target') || trigger.getAttribute('href');
            const target = targetId ? document.querySelector(targetId) : null;
            
            if (!target) return;
            
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                target.classList.toggle('show');
                
                if (target.classList.contains('show')) {
                    target.style.display = 'block';
                    target.style.height = 'auto';
                } else {
                    target.style.display = 'none';
                }
            });
        });
    }
    
    // =====================================================
    // ALERT - автозакрытие
    // =====================================================
    
    function initAlerts() {
        document.querySelectorAll('.alert').forEach(alert => {
            const closeBtn = alert.querySelector('[data-bs-dismiss="alert"]');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    alert.style.opacity = '0';
                    alert.style.transform = 'scale(0.9)';
                    setTimeout(() => alert.remove(), 200);
                });
            }
        });
    }
    
    // =====================================================
    // TOOLTIP (упрощенный)
    // =====================================================
    
    function initTooltips() {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(element => {
            const title = element.getAttribute('data-bs-title') || element.getAttribute('title');
            if (!title) return;
            
            element.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0,0,0,0.9);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    z-index: 10000;
                    pointer-events: none;
                `;
                document.body.appendChild(tooltip);
                
                const rect = element.getBoundingClientRect();
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
                tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
                
                element._tooltip = tooltip;
            });
            
            element.addEventListener('mouseleave', function() {
                if (element._tooltip) {
                    element._tooltip.remove();
                    element._tooltip = null;
                }
            });
        });
    }
    
    // =====================================================
    // TAB (упрощенный)
    // =====================================================
    
    function initTabs() {
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('data-bs-target');
                
                // Удалить active у всех
                this.closest('.nav').querySelectorAll('.active').forEach(el => {
                    el.classList.remove('active');
                });
                
                // Добавить active текущему
                this.classList.add('active');
                
                // Показать целевую панель
                if (targetId) {
                    const target = document.querySelector(targetId);
                    if (target) {
                        target.classList.add('active');
                        target.style.display = 'block';
                    }
                }
            });
        });
    }
    
    // Инициализация всех компонентов
    initDropdowns();
    initModals();
    initCollapse();
    initAlerts();
    initTooltips();
    initTabs();
    
    // Экспорт функций для глобального доступа
    window.openModal = openModal;
    window.closeModal = closeModal;
});
