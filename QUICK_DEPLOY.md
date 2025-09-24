# 🚀 Quick Deployment Guide - Car Service Management System

## 📋 Prerequisites
- Hetzner server running (188.245.117.191)
- SSH access configured
- Project cloned to `/var/www/car-service-managment-system`

## ⚡ One-Command Deployment

### Step 1: Export Current Database
```bash
cd /private/var/www/deyanski/Programa
./export-db.sh
```

### Step 2: Deploy to Production
```bash
# Copy files to production server
scp -r /private/var/www/deyanski/Programa/* root@188.245.117.191:/var/www/car-service-managment-system/

# SSH into production server
ssh root@188.245.117.191

# Setup production environment (first time only)
cd /var/www/car-service-managment-system
chmod +x setup-production.sh
./setup-production.sh

# Deploy application
chmod +x deploy.sh
./deploy.sh

# Import database
gunzip car_service_export_*.sql.gz
docker-compose -f production-docker-compose.yml exec -T db psql -U car_service_user -d car_service_db < car_service_export_*.sql
```

## 🌐 Access Your Application

- **URL**: http://188.245.117.191:8031
- **Admin**: http://188.245.117.191:8031/admin/

## 🔧 Configuration

Edit `.env` file on production server:
```bash
nano /var/www/car-service-managment-system/.env
```

Required changes:
- `SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` - Set a secure password
- `ALLOWED_HOSTS` - Add your domain if you have one

## 📊 Service Management

```bash
# View logs
docker-compose -f production-docker-compose.yml logs -f

# Restart services
docker-compose -f production-docker-compose.yml restart

# Stop services
docker-compose -f production-docker-compose.yml down

# Create backup
./backup-db.sh
```

## 🆘 Troubleshooting

```bash
# Check container status
docker-compose -f production-docker-compose.yml ps

# Check specific service logs
docker-compose -f production-docker-compose.yml logs web
docker-compose -f production-docker-compose.yml logs db
docker-compose -f production-docker-compose.yml logs nginx

# Reset everything
docker-compose -f production-docker-compose.yml down -v
docker system prune -f
./deploy.sh
```

## 📁 File Structure

```
/var/www/car-service-managment-system/
├── production-docker-compose.yml    # Production Docker setup
├── nginx.conf                       # Nginx configuration
├── deploy.sh                        # Deployment script
├── backup-db.sh                     # Database backup script
├── setup-production.sh              # Server setup script
├── env.production.example           # Environment variables template
├── .env                            # Your production environment variables
└── database-exports/               # Database dumps
```

## 🔒 Security Notes

1. **Change all default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **Configure firewall** if needed
4. **Set up SSL** for HTTPS (recommended)
5. **Regular backups** using `./backup-db.sh`

---

**Port Configuration**: The application runs on port **8031** to avoid conflicts with your existing services (Car Hunter: 8000, Mantos: 8010, Pool Reservation: 8020, Other Service: 8030).
