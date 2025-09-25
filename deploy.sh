#!/bin/bash

# Car Service Management System - Production Deployment Script
# Run this script on your production server

set -e

echo "🚀 Starting Car Service Management System deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/car-service-managment-system"
COMPOSE_FILE="production-docker-compose.yml"
ENV_FILE=".env"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR

echo -e "${YELLOW}📁 Working in directory: $PROJECT_DIR${NC}"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp env.production.example $ENV_FILE
    echo -e "${RED}❌ Please edit $ENV_FILE with your production settings before continuing!${NC}"
    echo -e "${YELLOW}   - Set SECRET_KEY to a secure random string${NC}"
    echo -e "${YELLOW}   - Set DB_PASSWORD to a secure password${NC}"
    echo -e "${YELLOW}   - Update ALLOWED_HOSTS if needed${NC}"
    exit 1
fi

# Stop existing containers if running
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down || true

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest images...${NC}"
docker-compose -f $COMPOSE_FILE pull

# Build the application
echo -e "${YELLOW}🔨 Building application...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE exec web python manage.py migrate

# Migrate data from SQLite to PostgreSQL (if SQLite exists)
echo -e "${YELLOW}🔄 Checking for data migration...${NC}"
if docker-compose -f $COMPOSE_FILE exec web test -f /app/db.sqlite3; then
    echo -e "${YELLOW}📊 Found SQLite database, migrating data to PostgreSQL...${NC}"
    docker-compose -f $COMPOSE_FILE exec web python production_migrate.py
else
    echo -e "${YELLOW}⚠️  No SQLite database found, skipping data migration${NC}"
fi

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker-compose -f $COMPOSE_FILE exec web python manage.py collectstatic --noinput

# Create superuser (optional)
echo -e "${YELLOW}👤 Do you want to create a superuser? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose -f $COMPOSE_FILE exec web python manage.py createsuperuser
fi

# Show running containers
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}📊 Running containers:${NC}"
docker-compose -f $COMPOSE_FILE ps

echo -e "${GREEN}🌐 Application is available at: http://188.245.117.191:8031${NC}"
echo -e "${YELLOW}📝 To view logs: docker-compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "${YELLOW}🛑 To stop: docker-compose -f $COMPOSE_FILE down${NC}"
