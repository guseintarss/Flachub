/**
 * Notification Manager для PageGlow
 * AJAX Polling система уведомлений (без WebSocket)
 * 
 * Использование:
 * <script src="{% static 'main/js/notifications.js' %}"></script>
 */

(function() {
    'use strict';

    class NotificationManager {
        constructor() {
            // DOM элементы
            this.bell = document.getElementById('notification-bell');
            this.dropdown = document.getElementById('notification-dropdown');
            this.badge = document.getElementById('notification-badge');
            this.list = document.getElementById('notification-list');
            this.markAllBtn = document.getElementById('mark-all-read');
            
            // Настройки
            this.pollInterval = 30000; // 30 секунд
            this.pollTimer = null;
            this.isOpen = false;
            
            // Инициализация
            this.init();
        }

        /**
         * Инициализация
         */
        init() {
            if (!this.bell) {
                console.log('[Notifications] Элементы уведомлений не найдены');
                return;
            }

            console.log('[Notifications] Инициализация...');
            
            this.attachEventListeners();
            this.loadNotifications();
            this.startPolling();
        }

        /**
         * Обработчики событий
         */
        attachEventListeners() {
            // Клик на колокольчик
            this.bell.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });

            // Отметить все как прочитанные
            if (this.markAllBtn) {
                this.markAllBtn.addEventListener('click', () => {
                    this.markAllAsRead();
                });
            }

            // Закрытие при клике вне
            document.addEventListener('click', (e) => {
                if (!this.dropdown.contains(e.target) && 
                    !this.bell.contains(e.target)) {
                    this.closeDropdown();
                }
            });
        }

        /**
         * Открыть/закрыть dropdown
         */
        toggleDropdown() {
            this.isOpen = !this.isOpen;
            this.dropdown.style.display = this.isOpen ? 'block' : 'none';
            
            if (this.isOpen) {
                this.loadNotifications();
            }
        }

        /**
         * Закрыть dropdown
         */
        closeDropdown() {
            this.isOpen = false;
            this.dropdown.style.display = 'none';
        }

        /**
         * Загрузка уведомлений с сервера
         */
        async loadNotifications() {
            try {
                const response = await fetch('/ajax/notifications/', {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                this.updateBadge(data.unread_count);
                
                // Обновляем список только если dropdown открыт
                if (this.isOpen) {
                    this.renderList(data.notifications);
                }
            } catch (error) {
                console.error('[Notifications] Ошибка загрузки:', error);
            }
        }

        /**
         * Обновление счётчика (badge)
         */
        updateBadge(count) {
            if (!this.badge) return;

            if (count > 0) {
                this.badge.textContent = count > 99 ? '99+' : count;
                this.badge.style.display = 'flex';
            } else {
                this.badge.style.display = 'none';
            }
        }

        /**
         * Отрисовка списка уведомлений
         */
        renderList(notifications) {
            if (!this.list) return;

            this.list.innerHTML = '';

            if (!notifications || notifications.length === 0) {
                this.list.innerHTML = '<div class="notification-empty">Нет уведомлений</div>';
                return;
            }

            notifications.forEach(n => {
                const item = document.createElement('div');
                item.className = 'notification-item' + (n.is_read ? '' : ' unread');
                
                item.innerHTML = `
                    <div class="notification-content">
                        <span class="notification-message">${this.escapeHtml(n.message)}</span>
                        <span class="notification-time">${this.formatTime(n.created_at)}</span>
                    </div>
                `;

                if (n.post_url) {
                    item.style.cursor = 'pointer';
                    item.onclick = () => {
                        window.location.href = n.post_url;
                    };
                }

                this.list.appendChild(item);
            });
        }

        /**
         * Отметить все уведомления как прочитанные
         */
        async markAllAsRead() {
            try {
                const response = await fetch('/ajax/notifications/read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Обновляем список после отметки
                this.loadNotifications();
            } catch (error) {
                console.error('[Notifications] Ошибка отметки прочитанных:', error);
            }
        }

        /**
         * Запуск периодического опроса
         */
        startPolling() {
            this.pollTimer = setInterval(() => {
                this.loadNotifications();
            }, this.pollInterval);
            
            console.log(`[Notifications] Polling запущен (интервал: ${this.pollInterval / 1000} сек)`);
        }

        /**
         * Остановка периодического опроса
         */
        stopPolling() {
            if (this.pollTimer) {
                clearInterval(this.pollTimer);
                this.pollTimer = null;
                console.log('[Notifications] Polling остановлен');
            }
        }

        /**
         * Получение CSRF токена
         */
        getCSRFToken() {
            // Ищем в meta теге
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                return metaTag.getAttribute('content');
            }

            // Ищем в cookie
            const name = 'csrftoken=';
            const decodedCookie = decodeURIComponent(document.cookie);
            const ca = decodedCookie.split(';');
            
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i].trim();
                if (c.indexOf(name) === 0) {
                    return c.substring(name.length);
                }
            }

            return '';
        }

        /**
         * Экранирование HTML
         */
        escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /**
         * Форматирование времени
         */
        formatTime(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 1) return 'только что';
            if (minutes < 60) return `${minutes} мин. назад`;
            if (hours < 24) return `${hours} час. назад`;
            if (days < 7) return `${days} дн. назад`;

            return date.toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'short',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    // Инициализация после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.notificationManager = new NotificationManager();
        });
    } else {
        window.notificationManager = new NotificationManager();
    }

    // Остановка polling при выгрузке страницы
    window.addEventListener('beforeunload', () => {
        if (window.notificationManager) {
            window.notificationManager.stopPolling();
        }
    });

})();
