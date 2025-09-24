#!/bin/bash

# Database Backup Script for Car Service Management System
# Run this script to create a database dump

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/car-service-managment-system"
BACKUP_DIR="/var/backups/car-service"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="car_service_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo -e "${YELLOW}🗄️  Creating database backup...${NC}"

# Navigate to project directory
cd $PROJECT_DIR

# Create database dump
docker-compose -f production-docker-compose.yml exec -T db pg_dump -U car_service_user -d car_service_db > $BACKUP_DIR/$BACKUP_FILE

# Compress the backup
gzip $BACKUP_DIR/$BACKUP_FILE

echo -e "${GREEN}✅ Database backup created: $BACKUP_DIR/$BACKUP_FILE.gz${NC}"

# Keep only last 7 days of backups
echo -e "${YELLOW}🧹 Cleaning old backups (keeping last 7 days)...${NC}"
find $BACKUP_DIR -name "car_service_backup_*.sql.gz" -mtime +7 -delete

echo -e "${GREEN}✅ Backup completed successfully!${NC}"
