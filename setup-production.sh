#!/bin/bash

# Production Server Setup Script
# Run this script on your production server to prepare the environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Setting up production environment for Car Service Management System...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Update system packages
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create project directory
echo -e "${YELLOW}📁 Creating project directory...${NC}"
mkdir -p /var/www/car-service-managment-system
cd /var/www/car-service-managment-system

# Create backup directory
mkdir -p /var/backups/car-service

# Set up log rotation for Docker
echo -e "${YELLOW}📝 Setting up log rotation...${NC}"
cat > /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF

# Create systemd service for auto-start (optional)
echo -e "${YELLOW}⚙️  Creating systemd service...${NC}"
cat > /etc/systemd/system/car-service.service << EOF
[Unit]
Description=Car Service Management System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/car-service-managment-system
ExecStart=/usr/local/bin/docker-compose -f production-docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f production-docker-compose.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable car-service.service

echo -e "${GREEN}✅ Production environment setup completed!${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "   1. Copy your project files to /var/www/car-service-managment-system/"
echo -e "   2. Edit .env file with your production settings"
echo -e "   3. Run ./deploy.sh to start the application"
echo -e "   4. Import your database data"
echo -e ""
echo -e "${YELLOW}🔧 Useful commands:${NC}"
echo -e "   - Start service: systemctl start car-service"
echo -e "   - Stop service: systemctl stop car-service"
echo -e "   - View logs: docker-compose -f production-docker-compose.yml logs -f"
