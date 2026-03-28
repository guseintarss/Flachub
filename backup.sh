#!/bin/bash
# ===========================================
# PageGlow 3.0 - Скрипт резервного копирования
# ===========================================

set -e

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Настройки
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${DATABASE_NAME:-pageglow_db}"
DB_USER="${DATABASE_USERNAME:-postgres}"

echo -e "${BLUE}🔄 PageGlow Backup${NC}"
echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Создание директории
mkdir -p "$BACKUP_DIR"

# Бэкап базы данных
echo -e "${YELLOW}📦 Бэкап базы данных...${NC}"
DB_BACKUP_FILE="$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

if docker compose ps postgres | grep -q "Up"; then
    docker compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$DB_BACKUP_FILE"
    DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ БД сохранена: $DB_BACKUP_FILE ($DB_SIZE)${NC}"
else
    echo -e "${RED}❌ PostgreSQL не запущен${NC}"
fi

# Бэкап медиа файлов
echo -e "${YELLOW}📸 Бэкап медиа файлов...${NC}"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_$TIMESTAMP.tar.gz"

if [ -d "./PageGlow/media" ]; then
    tar -czf "$MEDIA_BACKUP_FILE" ./PageGlow/media 2>/dev/null
    MEDIA_SIZE=$(du -h "$MEDIA_BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Медиа сохранены: $MEDIA_BACKUP_FILE ($MEDIA_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  Директория media не найдена${NC}"
fi

# Бэкап статики (опционально)
# echo -e "${YELLOW}🎨 Бэкап статики...${NC}"
# STATIC_BACKUP_FILE="$BACKUP_DIR/static_$TIMESTAMP.tar.gz"
# tar -czf "$STATIC_BACKUP_FILE" ./PageGlow/staticfiles 2>/dev/null

# Удаление старых бэкапов (старше 30 дней)
echo -e "${YELLOW}🧹 Очистка старых бэкапов...${NC}"
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "*.gz" -mtime +30 -type f | wc -l)

if [ "$OLD_BACKUPS" -gt 0 ]; then
    find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
    echo -e "${GREEN}✅ Удалено $OLD_BACKUPS старых файлов${NC}"
else
    echo "Старых бэкапов не найдено"
fi

# Список последних бэкапов
echo ""
echo -e "${BLUE}📋 Последние бэкапы:${NC}"
ls -lh "$BACKUP_DIR"/*.gz 2>/dev/null | tail -5 || echo "Бэкапы не найдены"

# Итог
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Резервное копирование завершено${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Бэкап БД: $DB_BACKUP_FILE"
echo "Бэкап медиа: $MEDIA_BACKUP_FILE"
echo ""
echo "Для восстановления:"
echo "  gunzip < $DB_BACKUP_FILE | docker compose exec -T postgres psql -U $DB_USER $DB_NAME"
echo "  tar -xzf $MEDIA_BACKUP_FILE -C ./PageGlow/"
echo ""
