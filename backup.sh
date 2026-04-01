#!/bin/bash
# ===========================================
# PageGlow 3.0 - Скрипт резервного копирования
# ===========================================

set -euo pipefail

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
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}🔄 PageGlow Backup${NC}"
echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Хранение: ${RETENTION_DAYS} дней"
echo ""

# Создание директории
mkdir -p "$BACKUP_DIR"

# Бэкап базы данных
log_info "Бэкап базы данных..."
DB_BACKUP_FILE="$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

if docker compose ps postgres 2>/dev/null | grep -q "Up"; then
    docker compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$DB_BACKUP_FILE"
    DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
    log_ok "БД сохранена: $DB_BACKUP_FILE ($DB_SIZE)"
else
    log_warn "PostgreSQL не запущен, пропускаем бэкап БД"
fi

# Бэкап медиа файлов
log_info "Бэкап медиа файлов..."
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_${TIMESTAMP}.tar.gz"

if [ -d "./PageGlow/media" ] && [ "$(ls -A ./PageGlow/media 2>/dev/null)" ]; then
    tar -czf "$MEDIA_BACKUP_FILE" -C ./PageGlow media
    MEDIA_SIZE=$(du -h "$MEDIA_BACKUP_FILE" | cut -f1)
    log_ok "Медиа сохранены: $MEDIA_BACKUP_FILE ($MEDIA_SIZE)"
else
    log_warn "Директория media пуста или не найдена"
    rm -f "$MEDIA_BACKUP_FILE"
fi

# Удаление старых бэкапов
log_info "Очистка старых бэкапов (старше ${RETENTION_DAYS} дней)..."
OLD_COUNT=$(find "$BACKUP_DIR" -name "*.gz" -mtime +${RETENTION_DAYS} -type f 2>/dev/null | wc -l)

if [ "$OLD_COUNT" -gt 0 ]; then
    find "$BACKUP_DIR" -name "*.gz" -mtime +${RETENTION_DAYS} -delete
    log_ok "Удалено $OLD_COUNT старых файлов"
else
    log_info "Старых бэкапов нет"
fi

# Сводка
echo ""
echo -e "${BLUE}📋 Последние бэкапы:${NC}"
ls -lh "$BACKUP_DIR"/*.gz 2>/dev/null | tail -5 || echo "  Бэкапы не найдены"

# Итог
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Резервное копирование завершено${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Для восстановления:"
echo "  make restore BACKUP_FILE=$DB_BACKUP_FILE"
echo "  tar -xzf $MEDIA_BACKUP_FILE -C ./PageGlow/"
echo ""
