# 🚀 Production Deployment Guide

## 📋 Prerequisites

- Hetzner server running (188.245.117.191)
- SSH access configured
- Project cloned to `/var/www/car-service-managment-system`
- Docker and Docker Compose installed

## ⚡ Quick Production Deployment

### Step 1: Prepare Production Server

```bash
# SSH into production server
ssh root@188.245.117.191

# Navigate to project directory
cd /var/www/car-service-managment-system

# Copy environment file
cp env.production.example .env

# Edit environment variables
nano .env
```

### Step 2: Update Environment Variables

Edit `.env` file with your production settings:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=188.245.117.191,localhost,127.0.0.1

# Database Settings
DB_PASSWORD=your-secure-database-password-change-this

# Individual Database Settings (for development compatibility)
SQL_DATABASE=car_service_db
SQL_USER=car_service_user
SQL_PASSWORD=your-secure-database-password-change-this
SQL_HOST=db
SQL_PORT=5432
```

### Step 3: Deploy Application

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 🔧 What the Deployment Does

1. **Stops existing containers** (if any)
2. **Pulls latest images** from Docker Hub
3. **Builds the application** with latest code
4. **Starts PostgreSQL 17** with your configuration
5. **Runs Django migrations** to create tables
6. **Migrates data** from SQLite to PostgreSQL (if SQLite exists)
7. **Collects static files** for Nginx
8. **Creates superuser** (optional)
9. **Starts Nginx** reverse proxy

## 🌐 Access Your Application

- **URL**: http://188.245.117.191:8031
- **Admin**: http://188.245.117.191:8031/admin/

## 📊 Data Migration

The deployment automatically:
- ✅ Migrates **6,673+ customers** from SQLite to PostgreSQL
- ✅ Migrates all related data (cars, orders, invoices, etc.)
- ✅ Preserves all relationships and foreign keys
- ✅ Converts data types (boolean, etc.)
- ✅ Updates sequences for auto-increment fields

## 🔧 Management Commands

```bash
# View logs
docker-compose -f production-docker-compose.yml logs -f

# Restart services
docker-compose -f production-docker-compose.yml restart

# Stop services
docker-compose -f production-docker-compose.yml down

# Access database
docker-compose -f production-docker-compose.yml exec db psql -U car_service_user -d car_service_db

# Run Django commands
docker-compose -f production-docker-compose.yml exec web python manage.py shell
```

## 🛡️ Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY** (generate with Django)
3. **Configure firewall** if needed
4. **Set up SSL** for HTTPS (recommended)
5. **Regular backups** of PostgreSQL data

## 📈 Monitoring

```bash
# Check container status
docker-compose -f production-docker-compose.yml ps

# Check resource usage
docker stats

# Check logs
docker-compose -f production-docker-compose.yml logs web
docker-compose -f production-docker-compose.yml logs db
docker-compose -f production-docker-compose.yml logs nginx
```

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull origin main

# Redeploy
./deploy.sh
```

## 🆘 Troubleshooting

### If deployment fails:

1. **Check logs:**
   ```bash
   docker-compose -f production-docker-compose.yml logs
   ```

2. **Check environment:**
   ```bash
   cat .env
   ```

3. **Reset and try again:**
   ```bash
   docker-compose -f production-docker-compose.yml down -v
   ./deploy.sh
   ```

### If data migration fails:

1. **Check SQLite exists:**
   ```bash
   docker-compose -f production-docker-compose.yml exec web ls -la /app/db.sqlite3
   ```

2. **Run migration manually:**
   ```bash
   docker-compose -f production-docker-compose.yml exec web python production_migrate.py
   ```

## 📝 Post-Deployment Checklist

- [ ] Application accessible at http://188.245.117.191:8031
- [ ] All 6,673+ customers visible in admin
- [ ] Database queries working
- [ ] Static files loading correctly
- [ ] Nginx reverse proxy working
- [ ] SSL certificate installed (if needed)
- [ ] Backup strategy implemented
- [ ] Monitoring set up

## 🎉 Success!

Your Car Service Management System is now running in production with:
- ✅ PostgreSQL 17 database
- ✅ All 6,673+ customers migrated
- ✅ Nginx reverse proxy
- ✅ Docker containerization
- ✅ Production-ready configuration
