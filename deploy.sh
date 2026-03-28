#!/bin/bash
# ===========================================
# PageGlow 3.0 - Быстрый деплой скрипт
# ===========================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логотип
echo -e "${BLUE}"
echo "  ____                 _       ____  _                   _ "
echo " |  _ \ _ __ ___  __ _| |_ ___|  _ \| | __ _ _ __   __ _| |_"
echo " | |_) | '__/ _ \/ _\` | __/ _ \ |_) | |/ _\` | '_ \ / _\` | __|"
echo " |  __/| | |  __/ (_| | ||  __/  __/| | (_| | | | | (_| | |_ "
echo " |_|   |_|  \___|\__,_|\__\___|_|   |_|\__,_|_| |_|\__,_|\__|"
echo -e "${NC}"
echo ""
echo "Версия: 3.0"
echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден! Установите Docker.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не найден! Установите Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker и Docker Compose найдены${NC}"
echo ""

# Проверка .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env файл не найден${NC}"
    
    if [ -f .env.example ]; then
        echo -e "${BLUE}📋 Копирование .env.example в .env...${NC}"
        cp .env.example .env
        
        # Генерация SECRET_KEY
        echo -e "${BLUE}🔑 Генерация SECRET_KEY...${NC}"
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || openssl rand -base64 64)
        
        # Замена SECRET_KEY в .env
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        
        echo -e "${GREEN}✅ .env файл создан и настроен${NC}"
    else
        echo -e "${RED}❌ .env.example не найден! Создайте .env файл вручную.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env файл найден${NC}"
fi

echo ""

# Проверка прав доступа к .env
chmod 600 .env

# Создание необходимых директорий
echo -e "${BLUE}📁 Создание директорий...${NC}"
mkdir -p nginx/ssl
mkdir -p nginx/certbot
mkdir -p backups
mkdir -p logs
mkdir -p PageGlow/staticfiles
mkdir -p PageGlow/media
mkdir -p PageGlow/logs

echo -e "${GREEN}✅ Директории созданы${NC}"
echo ""

# Остановка старых контейнеров
echo -e "${BLUE}🛑 Остановка старых контейнеров (если есть)...${NC}"
docker compose down 2>/dev/null || true
echo -e "${GREEN}✅ Контейнеры остановлены${NC}"
echo ""

# Запуск сервисов
echo -e "${BLUE}🚀 Запуск сервисов...${NC}"
docker compose up -d --build

echo ""
echo -e "${YELLOW}⏳ Ожидание инициализации сервисов (30 секунд)...${NC}"
sleep 30

# Проверка статуса
echo ""
echo -e "${BLUE}📊 Проверка статуса сервисов...${NC}"
docker compose ps

echo ""

# Проверка здоровья
echo -e "${BLUE}🏥 Проверка health check...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Приложение работает (HTTP $HEALTH_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠️  Приложение ещё не готово (HTTP $HEALTH_STATUS)${NC}"
    echo -e "${YELLOW}   Проверьте логи: docker compose logs pageglow${NC}"
fi

echo ""

# Создание суперпользователя
echo -e "${BLUE}👤 Создание суперпользователя${NC}"
read -p "Создать суперпользователя сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose exec pageglow python manage.py createsuperuser
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Деплой завершён успешно!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📍 Приложение доступно по адресу:"
echo "   http://localhost:8000"
echo "   http://localhost (через nginx)"
echo ""
echo "🔧 Полезные команды:"
echo "   docker compose ps              # Статус сервисов"
echo "   docker compose logs -f         # Просмотр логов"
echo "   docker compose restart         # Перезапуск"
echo "   docker compose down            # Остановка"
echo ""
echo "📚 Документация: DEPLOYMENT_GUIDE.md"
echo ""
