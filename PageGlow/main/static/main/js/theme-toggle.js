/**
 * Theme Toggle for PageGlow
 * Переключение светлой/темной темы с сохранением в localStorage
 */

(function() {
    'use strict';

    // DOM элементы
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = document.querySelector('.sun-icon');
    const moonIcon = document.querySelector('.moon-icon');
    const htmlElement = document.documentElement;

    // Ключ для localStorage
    const THEME_KEY = 'pageglow-theme';

    /**
     * Обновляет иконку в зависимости от темы
     */
    function updateIcon(isDark) {
        if (isDark) {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline';
        } else {
            sunIcon.style.display = 'inline';
            moonIcon.style.display = 'none';
        }
    }

    /**
     * Применяет тему к документу
     */
    function applyTheme(isDark) {
        if (isDark) {
            htmlElement.classList.add('dark-mode');
            htmlElement.setAttribute('data-bs-theme', 'dark');
        } else {
            htmlElement.classList.remove('dark-mode');
            htmlElement.setAttribute('data-bs-theme', 'light');
        }
        updateIcon(isDark);
        
        // Сохраняем состояние ARIA
        if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', isDark.toString());
        }
    }

    /**
     * Переключает тему
     */
    function toggleTheme() {
        const isDark = htmlElement.classList.contains('dark-mode');
        const newIsDark = !isDark;
        
        // Применяем новую тему
        applyTheme(newIsDark);
        
        // Сохраняем в localStorage
        localStorage.setItem(THEME_KEY, newIsDark ? 'dark' : 'light');
        
        // Отправляем событие для других скриптов
        window.dispatchEvent(new CustomEvent('theme-change', { 
            detail: { isDark: newIsDark } 
        }));
    }

    /**
     * Инициализация темы при загрузке
     */
    function initTheme() {
        // Проверяем сохраненную тему
        const savedTheme = localStorage.getItem(THEME_KEY);
        
        if (savedTheme) {
            // Используем сохраненную тему
            const isDark = savedTheme === 'dark';
            applyTheme(isDark);
        } else {
            // Проверяем системные предпочтения
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(prefersDark);
        }
    }

    /**
     * Навешиваем обработчики событий
     */
    function attachEventListeners() {
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
            
            // Добавляем обработку клавиши Enter и Space
            themeToggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleTheme();
                }
            });
        }

        // Слушаем изменения системной темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const savedTheme = localStorage.getItem(THEME_KEY);
            // Если нет сохраненной темы, используем системную
            if (!savedTheme) {
                applyTheme(e.matches);
            }
        });
    }

    /**
     * Инициализация
     */
    function init() {
        initTheme();
        attachEventListeners();
        console.log('[Theme Toggle] Инициализирован');
    }

    // Запускаем после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Делаем функцию доступной глобально (для отладки)
    window.PageGlowTheme = {
        toggle: toggleTheme,
        setDark: function() { 
            applyTheme(true); 
            localStorage.setItem(THEME_KEY, 'dark');
        },
        setLight: function() { 
            applyTheme(false); 
            localStorage.setItem(THEME_KEY, 'light');
        },
        getTheme: function() {
            return htmlElement.classList.contains('dark-mode') ? 'dark' : 'light';
        }
    };

})();
