/**
 * Reading Progress Indicator
 * Для отслеживания прогресса чтения статей на PageGlow
 * 
 * Использование:
 * <script src="{% static 'main/js/reading-progress.js' %}"></script>
 * <script>
 *   ReadingProgress.init({
 *     contentSelector: '.article-content',
 *     showCompletionMessage: true
 *   });
 * </script>
 */

const ReadingProgress = (function() {
  'use strict';

  // Конфигурация по умолчанию
  const defaultConfig = {
    contentSelector: 'article, .article-content, main',
    progressBarColor: '#4a90e2',
    completionColor: '#4CAF50',
    completionMessageDuration: 2000,
    showCompletionMessage: true,
    trackingCallback: null
  };

  // Переменные состояния
  let config = { ...defaultConfig };
  let progressBar = null;
  let contentElement = null;
  let isCompleted = false;

  /**
   * Инициализация индикатора
   */
  function init(options = {}) {
    // Объединяем конфигурацию
    config = { ...config, ...options };

    // Создаем элемент progress bar
    createProgressBar();

    // Находим элемент контента
    contentElement = document.querySelector(config.contentSelector);
    
    if (!contentElement) {
      console.warn('[ReadingProgress] Элемент контента не найден:', config.contentSelector);
      return;
    }

    // Добавляем слушатели событий
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleScroll);

    // Начальная проверка
    handleScroll();

    return this;
  }

  /**
   * Создание progress bar элемента
   */
  function createProgressBar() {
    progressBar = document.createElement('div');
    progressBar.id = 'reading-progress-bar';
    progressBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 2px;
      width: 0%;
      background-color: ${config.progressBarColor};
      z-index: 10000;
      transition: width 0.1s ease-out, background-color 0.3s ease-out;
      box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
    `;
    document.body.insertBefore(progressBar, document.body.firstChild);
  }

  /**
   * Обработчик события scroll
   */
  function handleScroll() {
    if (!contentElement) return;

    // Получаем координаты элемента контента
    const rect = contentElement.getBoundingClientRect();
    const contentHeight = contentElement.scrollHeight;
    
    // Вычисляем прогресс (от начала контента до конца экрана)
    const windowHeight = window.innerHeight;
    const contentStart = rect.top;
    const contentEnd = rect.bottom;
    
    // Точка, где контент начинает входить в экран (от верхнего края)
    const scrollProgress = Math.max(0, -contentStart);
    const totalDistance = contentHeight + windowHeight;
    
    let progress = (scrollProgress / totalDistance) * 100;
    progress = Math.min(100, Math.max(0, progress));

    // Обновляем ширину progress bar
    progressBar.style.width = progress + '%';

    // Проверяем, завершено ли чтение
    if (progress >= 95 && !isCompleted) {
      completeReading();
    } else if (progress < 95 && isCompleted) {
      isCompleted = false;
      progressBar.style.backgroundColor = config.progressBarColor;
    }

    // Вызываем callback если он установлен
    if (config.trackingCallback && typeof config.trackingCallback === 'function') {
      config.trackingCallback(progress);
    }
  }

  /**
   * Обработка завершения чтения
   */
  function completeReading() {
    if (isCompleted) return;
    
    isCompleted = true;

    // Меняем цвет на зеленый
    progressBar.style.backgroundColor = config.completionColor;

    // Показываем сообщение если нужно
    if (config.showCompletionMessage) {
      showCompletionMessage();
    }

    // Скрываем progress bar через время
    setTimeout(() => {
      progressBar.style.opacity = '0';
      progressBar.style.transition = 'opacity 0.5s ease-out';
    }, config.completionMessageDuration);
  }

  /**
   * Показать сообщение о завершении
   */
  function showCompletionMessage() {
    const message = document.createElement('div');
    message.id = 'reading-completion-message';
    message.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      padding: 20px 40px;
      background-color: ${config.completionColor};
      color: white;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      z-index: 10001;
      box-shadow: 0 10px 25px rgba(76, 175, 80, 0.3);
      animation: slideUp 0.4s ease-out;
      pointer-events: none;
    `;
    message.textContent = '✓ Статья прочитана!';
    
    document.body.appendChild(message);

    // Удаляем сообщение через время
    setTimeout(() => {
      message.style.animation = 'slideDown 0.4s ease-out';
      message.style.opacity = '0';
      setTimeout(() => message.remove(), 400);
    }, config.completionMessageDuration - 500);
  }

  /**
   * Получить текущий прогресс (0-100)
   */
  function getProgress() {
    if (!progressBar) return 0;
    return parseFloat(progressBar.style.width);
  }

  /**
   * Сбросить индикатор
   */
  function reset() {
    if (progressBar) {
      progressBar.style.width = '0%';
      progressBar.style.backgroundColor = config.progressBarColor;
      progressBar.style.opacity = '1';
      progressBar.style.transition = 'width 0.1s ease-out, background-color 0.3s ease-out';
    }
    isCompleted = false;
  }

  /**
   * Уничтожить индикатор (очистить ресурсы)
   */
  function destroy() {
    window.removeEventListener('scroll', handleScroll);
    window.removeEventListener('resize', handleScroll);
    
    if (progressBar && progressBar.parentNode) {
      progressBar.parentNode.removeChild(progressBar);
    }
    
    progressBar = null;
    contentElement = null;
    isCompleted = false;
  }

  /**
   * Обновить конфигурацию
   */
  function updateConfig(newConfig = {}) {
    config = { ...config, ...newConfig };
    
    // Пересоздаем progress bar если изменился цвет
    if (progressBar && !isCompleted) {
      progressBar.style.backgroundColor = config.progressBarColor;
    }
  }

  // Публичный API
  return {
    init,
    getProgress,
    reset,
    destroy,
    updateConfig
  };
})();

// Добавляем стили для анимаций если их еще нет
if (!document.getElementById('reading-progress-styles')) {
  const style = document.createElement('style');
  style.id = 'reading-progress-styles';
  style.textContent = `
    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translate(-50%, 20px);
      }
      to {
        opacity: 1;
        transform: translate(-50%, -50%);
      }
    }

    @keyframes slideDown {
      from {
        opacity: 1;
        transform: translate(-50%, -50%);
      }
      to {
        opacity: 0;
        transform: translate(-50%, 20px);
      }
    }
  `;
  document.head.appendChild(style);
}

// Автоматическая инициализация если добавлен атрибут data-reading-progress
document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('[data-reading-progress]')) {
    ReadingProgress.init();
  }
});
