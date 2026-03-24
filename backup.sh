#!/bin/bash
# Automated Backup Script for PageGlow 3.0
# Usage: ./backup.sh [backup_dir]

set -e

# Configuration
BACKUP_DIR="${1:-/home/$USER/backups/pageglow}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=30

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔄 PageGlow Backup Script${NC}"
echo "================================"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if using Docker
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}Docker mode detected${NC}"
    MODE="docker"
else
    echo -e "${YELLOW}VPS mode detected${NC}"
    MODE="vps"
fi

# Backup database
echo -e "${YELLOW}[1/3] Backing up database...${NC}"
if [ "$MODE" = "docker" ]; then
    docker-compose exec -T postgres pg_dump -U postgres pageglow_db > "$BACKUP_DIR/db_$TIMESTAMP.sql"
else
    # Get DB credentials from .env
    if [ -f ".env" ]; then
        source .env
        PGPASSWORD=$DATABASE_PASSWORD pg_dump -h $DATABASE_HOST -U $DATABASE_USERNAME -d $DATABASE_NAME > "$BACKUP_DIR/db_$TIMESTAMP.sql"
    else
        echo -e "${RED}.env file not found!${NC}"
        exit 1
    fi
fi

# Compress backup
echo -e "${YELLOW}[2/3] Compressing backup...${NC}"
gzip "$BACKUP_DIR/db_$TIMESTAMP.sql"
echo -e "${GREEN}✓ Database backup: db_$TIMESTAMP.sql.gz${NC}"

# Backup media files (optional)
echo -e "${YELLOW}[3/3] Backing up media files...${NC}"
if [ -d "PageGlow/media" ]; then
    tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" PageGlow/media/
    echo -e "${GREEN}✓ Media backup: media_$TIMESTAMP.tar.gz${NC}"
fi

# Remove old backups
echo -e "${YELLOW}Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$KEEP_DAYS -delete

# Show backup size
echo
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Backup completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo
du -sh "$BACKUP_DIR"
echo
ls -lh "$BACKUP_DIR"/*_$TIMESTAMP.*
echo
echo -e "${YELLOW}Backup location: $BACKUP_DIR${NC}"
echo -e "${YELLOW}Retention period: $KEEP_DAYS days${NC}"
