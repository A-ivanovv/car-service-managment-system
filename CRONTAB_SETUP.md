# Database Backup - Crontab Setup

## Daily Automated Backup

This setup will automatically backup your PostgreSQL database every day at 2:00 AM.

### Installation Steps

1. **SSH to production server:**
   ```bash
   ssh -i ~/.ssh/antuni.ivanov root@188.245.117.191
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add this line to run daily backup at 2:00 AM:**
   ```cron
   0 2 * * * cd /var/www/car-service-managment-system && docker compose -f production-docker-compose.yml exec -T web python manage.py backup_database >> /var/log/db-backup.log 2>&1
   ```

4. **Save and exit** (`:wq` in vim or `Ctrl+X` in nano)

### Manual Backup

Run a backup manually anytime:
```bash
cd /var/www/car-service-managment-system
docker compose -f production-docker-compose.yml exec web python manage.py backup_database
```

### Command Options

```bash
# Keep backups for 60 days instead of 30
python manage.py backup_database --retention-days 60

# Skip compression (faster, but larger files)
python manage.py backup_database --no-compress

# Show help
python manage.py backup_database --help
```

### Backup Location

Backups are stored at:
```
/var/www/car-service-managment-system/container/pg_dump/backups/
```

Files are named: `backup_YYYYMMDD_HHMMSS.sql.gz`

### View Backup Logs

```bash
# View latest backup log
tail -f /var/log/db-backup.log

# View all backup logs
cat /var/log/db-backup.log
```

### Restore from Backup

To restore a backup:

```bash
# 1. Decompress the backup
gunzip /path/to/backup_YYYYMMDD_HHMMSS.sql.gz

# 2. Stop the web service
docker compose -f production-docker-compose.yml stop web

# 3. Restore the database
docker compose -f production-docker-compose.yml exec -T db psql -U car_service_user -d car_service_db < /path/to/backup_YYYYMMDD_HHMMSS.sql

# 4. Start the web service
docker compose -f production-docker-compose.yml start web
```

### Backup Features

- ✅ **Full schema + data** - Complete database dump
- ✅ **Automatic compression** - Saves disk space with gzip
- ✅ **Automatic cleanup** - Old backups deleted after 30 days
- ✅ **Timestamped files** - Easy to identify and sort
- ✅ **Django management command** - Clean, maintainable code
- ✅ **Logging** - All output saved to log file

### Cron Schedule Examples

```cron
# Every day at 2:00 AM
0 2 * * * [command]

# Every day at 3:30 AM
30 3 * * * [command]

# Every 6 hours
0 */6 * * * [command]

# Every Sunday at midnight
0 0 * * 0 [command]

# Twice daily (2 AM and 2 PM)
0 2,14 * * * [command]
```

### Monitoring

Check if backups are running:
```bash
# List recent backups
ls -lht /var/www/car-service-managment-system/container/pg_dump/backups/ | head

# Check backup size
du -sh /var/www/car-service-managment-system/container/pg_dump/backups/

# Count backups
ls /var/www/car-service-managment-system/container/pg_dump/backups/*.sql.gz | wc -l
```
