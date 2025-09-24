# Car Service Management System - Production Deployment Guide

This guide will help you deploy the Car Service Management System to your Hetzner server.

## 🚀 Quick Deployment

### 1. Export Current Database

On your local machine (where you have the current data):

```bash
cd /private/var/www/deyanski/Programa
chmod +x export-db.sh
./export-db.sh
```

This will create database exports in the `database-exports/` directory.

### 2. Transfer Files to Production Server

```bash
# Copy the entire project
scp -r /private/var/www/deyanski/Programa/* root@188.245.117.191:/var/www/car-service-managment-system/

# Copy database exports
scp database-exports/*.gz root@188.245.117.191:/var/www/car-service-managment-system/
```

### 3. Deploy on Production Server

SSH into your production server:

```bash
ssh root@188.245.117.191
cd /var/www/car-service-managment-system
```

Make scripts executable and run deployment:

```bash
chmod +x deploy.sh backup-db.sh
./deploy.sh
```

### 4. Import Database

After deployment, import your data:

```bash
# Extract the database dump
gunzip car_service_export_*.sql.gz

# Import into production database
docker-compose -f production-docker-compose.yml exec -T db psql -U car_service_user -d car_service_db < car_service_export_*.sql
```

## 🔧 Configuration

### Environment Variables

Edit the `.env` file on your production server:

```bash
nano .env
```

Update these values:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=188.245.117.191,localhost,127.0.0.1

# Database Settings
DB_PASSWORD=your-secure-database-password-change-this
```

### Port Configuration

The application will run on port **8030** to avoid conflicts with your existing services:
- Car Hunter: 8000
- Mantos: 8010  
- Pool Reservation: 8020
- **Car Service Management: 8030** ← New service

## 📊 Service Management

### View Logs
```bash
docker-compose -f production-docker-compose.yml logs -f
```

### Restart Services
```bash
docker-compose -f production-docker-compose.yml restart
```

### Stop Services
```bash
docker-compose -f production-docker-compose.yml down
```

### Update Application
```bash
git pull origin main
docker-compose -f production-docker-compose.yml build --no-cache
docker-compose -f production-docker-compose.yml up -d
```

## 🗄️ Database Management

### Create Backup
```bash
./backup-db.sh
```

### Restore from Backup
```bash
gunzip /var/backups/car-service/car_service_backup_YYYYMMDD_HHMMSS.sql.gz
docker-compose -f production-docker-compose.yml exec -T db psql -U car_service_user -d car_service_db < /var/backups/car-service/car_service_backup_YYYYMMDD_HHMMSS.sql
```

## 🔒 Security Considerations

1. **Change default passwords** in `.env` file
2. **Use strong SECRET_KEY** (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
3. **Configure firewall** if needed
4. **Set up SSL** with Let's Encrypt for HTTPS
5. **Regular backups** using the backup script

## 📱 Access the Application

After deployment, access your application at:
- **URL**: http://188.245.117.191:8031
- **Admin**: http://188.245.117.191:8031/admin/

## 🆘 Troubleshooting

### Check Container Status
```bash
docker-compose -f production-docker-compose.yml ps
```

### Check Logs
```bash
docker-compose -f production-docker-compose.yml logs web
docker-compose -f production-docker-compose.yml logs db
docker-compose -f production-docker-compose.yml logs nginx
```

### Database Connection Issues
```bash
docker-compose -f production-docker-compose.yml exec db psql -U car_service_user -d car_service_db -c "\dt"
```

### Reset Everything
```bash
docker-compose -f production-docker-compose.yml down -v
docker system prune -f
./deploy.sh
```

## 📈 Monitoring

### Health Check
```bash
curl http://188.245.117.191:8031/health/
```

### Resource Usage
```bash
docker stats
```

## 🔄 Updates

To update the application:

1. Export current database (if needed)
2. Pull latest changes: `git pull origin main`
3. Rebuild and restart: `docker-compose -f production-docker-compose.yml up -d --build`
4. Run migrations: `docker-compose -f production-docker-compose.yml exec web python manage.py migrate`

---

**Note**: This deployment uses Docker Compose with separate containers for the web application, database, and Nginx reverse proxy. The application is configured to run on port 8030 to avoid conflicts with your existing services.
