#!/bin/bash
# ===========================================
# PageGlow 3.0 - Быстрый деплой скрипт
# Zero-downtime deployment с health checks
# ===========================================

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Настройки
HEALTH_URL="http://localhost/health/"
MAX_WAIT=120
CHECK_INTERVAL=3
PROJECT_NAME="pageglow"

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${CYAN}▸ $1${NC}"; }

# Логотип
echo -e "${BLUE}"
echo "  ____                 _       ____  _                   _ "
echo " |  _ \ _ __ ___  __ _| |_ ___|  _ \| | __ _ _ __   __ _| |_"
echo " | |_) | '__/ _ \/ _\` | __/ _ \ |_) | |/ _\` | '_ \ / _\` | __|"
echo " |  __/| | |  __/ (_| | ||  __/  __/| | (_| | | | | (_| | |_ "
echo " |_|   |_|  \___|\__,_|\__\___|_|   |_|\__,_|_| |_|\__,_|\__|"
echo -e "${NC}"
echo "Версия: 3.0 | $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker не найден! Установите Docker."
    exit 1
fi

# Проверка Docker Compose (V2 плагин или V1 standalone)
# Приоритет: docker compose (v2) > docker-compose (v1)
if docker compose help &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    log_error "Docker Compose не найден!"
    log_info "Установите: sudo apt install docker-compose-plugin"
    exit 1
fi

log_ok "Docker и Compose найдены ($COMPOSE_CMD)"

# Проверка .env файла
if [ ! -f .env ]; then
    log_warn ".env файл не найден"
    
    if [ -f .env.example ]; then
        log_info "Копирование .env.example → .env..."
        cp .env.example .env
        
        # Генерация SECRET_KEY
        log_info "Генерация SECRET_KEY..."
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || openssl rand -base64 64)
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
        
        log_ok ".env файл создан"
        log_warn "Отредактируйте .env и укажите правильные значения для DATABASE_PASSWORD, EMAIL_HOST_USER и ALLOWED_HOSTS"
    else
        log_error ".env.example не найден!"
        exit 1
    fi
else
    log_ok ".env файл найден"
fi

chmod 600 .env

# Создание директорий
log_step "Создание директорий..."
mkdir -p nginx/ssl nginx/certbot backups logs PageGlow/staticfiles PageGlow/media PageGlow/logs
log_ok "Директории созданы"

# Функция ожидания health check
wait_for_health() {
    local service=$1
    local url=$2
    local elapsed=0
    
    log_info "Ожидание запуска ${service}..."
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_ok "${service} запущен (${elapsed}с)"
            return 0
        fi
        sleep $CHECK_INTERVAL
        elapsed=$((elapsed + CHECK_INTERVAL))
        echo -ne "${YELLOW}⏳ ${elapsed}с/${MAX_WAIT}с${NC}\r"
    done
    
    echo ""
    log_error "${service} не запустился за ${MAX_WAIT}с"
    return 1
}

# Функция для graceful restart (zero-downtime)
graceful_restart() {
    log_step "Graceful restart..."
    
    # Проверяем, запущены ли контейнеры
    if $COMPOSE_CMD ps --format json 2>/dev/null | grep -q '"Running"'; then
        log_info "Контейнеры запущены, выполняем graceful restart..."
        
        # Пересобираем только если есть изменения
        log_info "Пересборка образа..."
        $COMPOSE_CMD build --quiet pageglow
        
        # Запускаем новый контейнер параллельно
        log_info "Запуск нового контейнера..."
        $COMPOSE_CMD up -d --no-deps --scale pageglow=2 --no-recreate pageglow 2>/dev/null || true
        
        # Ждём пока новый контейнер будет готов
        if wait_for_health "новый контейнер" "$HEALTH_URL"; then
            # Останавливаем старый контейнер
            log_info "Остановка старого контейнера..."
            $COMPOSE_CMD up -d --no-deps --scale pageglow=1 pageglow
            log_ok "Graceful restart завершён"
        else
            log_warn "Новый контейнер не запустился, откат..."
            $COMPOSE_CMD up -d --no-deps --scale pageglow=1 pageglow
            return 1
        fi
    else
        # Первый запуск
        log_info "Первый запуск..."
        $COMPOSE_CMD up -d --build
    fi
}

# Запуск сервисов
log_step "Запуск сервисов..."
graceful_restart

echo ""

# Ожидание PostgreSQL и Redis
log_step "Проверка зависимостей..."
$COMPOSE_CMD exec -T postgres pg_isready -U "${DATABASE_USERNAME:-postgres}" 2>/dev/null && \
    log_ok "PostgreSQL готов" || log_warn "PostgreSQL ещё инициализируется"

$COMPOSE_CMD exec -T redis redis-cli ping 2>/dev/null | grep -q PONG && \
    log_ok "Redis готов" || log_warn "Redis ещё инициализируется"

# Ожидание Django приложения
log_step "Проверка Django приложения..."
if wait_for_health "Django" "$HEALTH_URL"; then
    log_ok "Приложение работает"
else
    log_error "Приложение не ответило"
    log_info "Проверьте логи: $COMPOSE_CMD logs pageglow"
    exit 1
fi

# Проверка миграций
log_step "Проверка миграций..."
if $COMPOSE_CMD exec -T pageglow python manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
    log_warn "Есть неприменённые миграции"
    read -p "Применить миграции сейчас? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $COMPOSE_CMD exec pageglow python manage.py migrate
        log_ok "Миграции применены"
    fi
else
    log_ok "Все миграции применены"
fi

# Статус сервисов
echo ""
log_step "Статус сервисов:"
$COMPOSE_CMD ps

# Итог
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Деплой завершён успешно!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📍 Приложение доступно:"
echo "   http://localhost (nginx)"
echo "   http://localhost:8000 (django direct)"
echo ""
echo "🔧 Полезные команды:"
echo "   make logs           # Просмотр логов"
echo "   make logs-app       # Логи приложения"
echo "   make backup         # Резервное копирование"
echo "   make shell          # Django shell"
echo "   make createsuperuser# Создать админа"
echo "   make down           # Остановить"
echo ""
echo "📚 Документация: DEPLOYMENT_GUIDE.md"
echo ""
