/**
 * WebSocket Notifications Client for PageGlow
 * Real-time уведомления через WebSocket
 */

(function() {
    'use strict';

    class NotificationsWebSocket {
        constructor() {
            this.socket = null;
            this.reconnectAttempts = 0;
            this.maxReconnectAttempts = 5;
            this.reconnectDelay = 1000;
            this.heartbeatInterval = null;
            this.heartbeatTimeout = 30000; // 30 секунд
            
            // DOM элементы
            this.bellElement = document.getElementById('notification-bell');
            this.badgeElement = document.getElementById('notification-badge');
            this.dropdownElement = document.getElementById('notification-dropdown');
            this.listElement = document.getElementById('notification-list');
            this.markAllBtn = document.getElementById('mark-all-read');
            
            this.init();
        }

        init() {
            // Проверяем что пользователь авторизован
            if (!this.bellElement) {
                console.log('[WS Notifications] Элементы уведомлений не найдены');
                return;
            }

            this.connect();
            this.attachEventListeners();
        }

        /**
         * Подключение к WebSocket
         */
        connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

            console.log('[WS Notifications] Подключение к', wsUrl);

            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('[WS Notifications] Подключено');
                this.reconnectAttempts = 0;
                this.startHeartbeat();
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.socket.onerror = (error) => {
                console.error('[WS Notifications] Ошибка:', error);
            };

            this.socket.onclose = (event) => {
                console.log('[WS Notifications] Отключено', event.code, event.reason);
                this.stopHeartbeat();
                this.reconnect();
            };
        }

        /**
         * Обработка сообщений от сервера
         */
        handleMessage(data) {
            console.log('[WS Notifications] Сообщение:', data);

            switch (data.type) {
                case 'notification':
                    this.handleNewNotification(data.data);
                    break;
                case 'count':
                    this.updateCount(data.count);
                    break;
            }
        }

        /**
         * Обработка нового уведомления
         */
        handleNewNotification(notification) {
            // Добавляем звук уведомления (опционально)
            this.playNotificationSound();

            // Показывем badge
            if (this.badgeElement) {
                this.badgeElement.style.display = 'block';
            }

            // Добавляем в список
            if (this.listElement && this.dropdownElement.style.display === 'block') {
                this.prependNotificationToList(notification);
            }

            // Показываем toast уведомление
            this.showToast(notification);
        }

        /**
         * Обновление счётчика
         */
        updateCount(count) {
            if (!this.badgeElement) return;

            if (count > 0) {
                this.badgeElement.textContent = count > 99 ? '99+' : count;
                this.badgeElement.style.display = 'block';
            } else {
                this.badgeElement.style.display = 'none';
            }
        }

        /**
         * Добавление уведомления в список
         */
        prependNotificationToList(notification) {
            const item = document.createElement('div');
            item.className = 'notification-item unread';
            item.innerHTML = `
                <div class="notification-content">
                    <span class="notification-message">${this.escapeHtml(notification.message)}</span>
                    <span class="notification-time">${this.formatTime(notification.created_at)}</span>
                </div>
            `;

            if (notification.post_url) {
                item.style.cursor = 'pointer';
                item.onclick = () => window.location.href = notification.post_url;
            }

            // Удаляем "Нет уведомлений" если есть
            const emptyState = this.listElement.querySelector('.notification-empty');
            if (emptyState) {
                emptyState.remove();
            }

            this.listElement.insertBefore(item, this.listElement.firstChild);
        }

        /**
         * Переподключение при обрыве
         */
        reconnect() {
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
                
                console.log(`[WS Notifications] Переподключение через ${delay}ms (попытка ${this.reconnectAttempts})`);
                
                setTimeout(() => {
                    this.connect();
                }, delay);
            } else {
                console.error('[WS Notifications] Превышено количество попыток переподключения');
            }
        }

        /**
         * Heartbeat для поддержания соединения
         */
        startHeartbeat() {
            this.heartbeatInterval = setInterval(() => {
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    this.socket.send(JSON.stringify({ type: 'ping' }));
                }
            }, this.heartbeatTimeout / 2);
        }

        stopHeartbeat() {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
                this.heartbeatInterval = null;
            }
        }

        /**
         * Обработчики событий
         */
        attachEventListeners() {
            // Открытие/закрытие dropdown
            if (this.bellElement) {
                this.bellElement.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleDropdown();
                });
            }

            // Отметить все как прочитанные
            if (this.markAllBtn) {
                this.markAllBtn.addEventListener('click', () => {
                    this.markAllAsRead();
                });
            }

            // Закрытие при клике вне
            document.addEventListener('click', (e) => {
                if (this.dropdownElement && 
                    !this.dropdownElement.contains(e.target) && 
                    !this.bellElement.contains(e.target)) {
                    this.closeDropdown();
                }
            });
        }

        toggleDropdown() {
            const isHidden = this.dropdownElement.style.display === 'none';
            this.dropdownElement.style.display = isHidden ? 'block' : 'none';
            
            if (isHidden && this.socket) {
                // Загружаем уведомления при открытии
                this.loadNotifications();
            }
        }

        closeDropdown() {
            this.dropdownElement.style.display = 'none';
        }

        loadNotifications() {
            fetch('/api/notifications/')
                .then(response => response.json())
                .then(data => {
                    this.renderNotificationsList(data.notifications || data);
                })
                .catch(error => console.error('[WS Notifications] Ошибка загрузки:', error));
        }

        renderNotificationsList(notifications) {
            if (!this.listElement) return;

            this.listElement.innerHTML = '';

            if (!notifications || notifications.length === 0) {
                this.listElement.innerHTML = '<div class="notification-empty">Нет уведомлений</div>';
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
                    item.onclick = () => window.location.href = n.post_url;
                }

                this.listElement.appendChild(item);
            });
        }

        markAllAsRead() {
            if (this.socket) {
                this.socket.send(JSON.stringify({ type: 'mark_all_read' }));
            }

            // Оптимистичное обновление UI
            const unreadItems = this.listElement.querySelectorAll('.unread');
            unreadItems.forEach(item => item.classList.remove('unread'));
            this.updateCount(0);
        }

        /**
         * Toast уведомление
         */
        showToast(notification) {
            // Создаём toast если нет
            let toast = document.getElementById('ws-notification-toast');
            if (!toast) {
                toast = document.createElement('div');
                toast.id = 'ws-notification-toast';
                toast.className = 'ws-notification-toast';
                document.body.appendChild(toast);
            }

            toast.innerHTML = `
                <div class="toast-content">
                    <span class="toast-icon">🔔</span>
                    <span class="toast-message">${this.escapeHtml(notification.message)}</span>
                </div>
            `;

            toast.classList.add('show');

            // Скрываем через 5 секунд
            setTimeout(() => {
                toast.classList.remove('show');
            }, 5000);
        }

        /**
         * Звук уведомления (опционально)
         */
        playNotificationSound() {
            // Можно добавить звук
            // const audio = new Audio('/static/sounds/notification.mp3');
            // audio.play().catch(() => {});
        }

        /**
         * Утилиты
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

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
                month: 'short' 
            });
        }
    }

    // Инициализация после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.notificationsWS = new NotificationsWebSocket();
        });
    } else {
        window.notificationsWS = new NotificationsWebSocket();
    }

})();
