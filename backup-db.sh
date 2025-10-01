#!/bin/bash
# Daily PostgreSQL Backup Script
# Usage: Add to crontab with: 0 2 * * * /var/www/car-service-managment-system/backup-db.sh >> /var/log/db-backup.log 2>&1

BACKUP_DIR="/var/www/car-service-managment-system/container/pg_dump/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Navigate to project directory
cd /var/www/car-service-managment-system || exit 1

# Create backup
echo "[$(date)] Starting backup..."
docker compose -f production-docker-compose.yml exec -T db pg_dump \
    -U car_service_user \
    -d car_service_db \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress
if [ -s "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    gzip "${BACKUP_DIR}/${BACKUP_FILE}"
    echo "[$(date)] Backup completed: ${BACKUP_FILE}.gz ($(du -h "${BACKUP_DIR}/${BACKUP_FILE}.gz" | cut -f1))"
    
    # Clean old backups
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    echo "[$(date)] Cleanup completed. Total backups: $(find "$BACKUP_DIR" -name "backup_*.sql.gz" | wc -l)"
else
    echo "[$(date)] ERROR: Backup failed"
    rm -f "${BACKUP_DIR}/${BACKUP_FILE}"
    exit 1
fi