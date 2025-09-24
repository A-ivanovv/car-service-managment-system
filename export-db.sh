#!/bin/bash

# Export Database Script for Car Service Management System
# Run this script to export the current database for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/private/var/www/deyanski/Programa"
EXPORT_DIR="./database-exports"
DATE=$(date +%Y%m%d_%H%M%S)
EXPORT_FILE="car_service_export_$DATE.sql"

echo -e "${YELLOW}🗄️  Exporting database for production deployment...${NC}"

# Navigate to project directory
cd $PROJECT_DIR

# Create export directory if it doesn't exist
mkdir -p $EXPORT_DIR

# Export database from development
echo -e "${YELLOW}📤 Exporting database from development...${NC}"
docker exec car_service_web python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > $EXPORT_DIR/car_service_data_$DATE.json

# Also create SQL dump if using PostgreSQL
echo -e "${YELLOW}📤 Creating SQL dump...${NC}"
docker exec car_service_db pg_dump -U postgres -d car_service_db > $EXPORT_DIR/$EXPORT_FILE

# Compress the exports
gzip $EXPORT_DIR/$EXPORT_FILE
gzip $EXPORT_DIR/car_service_data_$DATE.json

echo -e "${GREEN}✅ Database export completed!${NC}"
echo -e "${YELLOW}📁 Files created:${NC}"
echo -e "   - $EXPORT_DIR/$EXPORT_FILE.gz (SQL dump)"
echo -e "   - $EXPORT_DIR/car_service_data_$DATE.json.gz (Django data)"

echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "   1. Copy these files to your production server:"
echo -e "      scp $EXPORT_DIR/$EXPORT_FILE.gz root@188.245.117.191:/var/www/car-service-managment-system/"
echo -e "      scp $EXPORT_DIR/car_service_data_$DATE.json.gz root@188.245.117.191:/var/www/car-service-managment-system/"
echo -e "   2. On production server, run:"
echo -e "      gunzip $EXPORT_FILE.gz"
echo -e "      docker-compose -f production-docker-compose.yml exec -T db psql -U car_service_user -d car_service_db < $EXPORT_FILE"
