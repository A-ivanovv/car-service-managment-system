"""
Django management command for creating PostgreSQL database backups.
Usage: python manage.py backup_database
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates a full PostgreSQL database backup (schema + data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retention-days',
            type=int,
            default=30,
            help='Number of days to keep old backups (default: 30)'
        )
        parser.add_argument(
            '--no-compress',
            action='store_true',
            help='Skip compression of the backup file'
        )

    def handle(self, *args, **options):
        retention_days = options['retention_days']
        compress = not options['no_compress']
        
        # Get database settings from Django
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        # Setup backup directory
        backup_dir = Path('/var/www/car-service-managment-system/container/pg_dump/backups')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.sql'
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Starting database backup...'))
        self.stdout.write(f'Database: {db_name}')
        self.stdout.write(f'Backup file: {backup_file}')
        
        try:
            # Run pg_dump via docker compose
            cmd = [
                'docker', 'compose', '-f', 'production-docker-compose.yml',
                'exec', '-T', 'db', 'pg_dump',
                '-U', db_user,
                '-d', db_name,
                '--clean',
                '--if-exists',
                '--no-owner',
                '--no-privileges'
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    cwd='/var/www/car-service-managment-system',
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                self.stdout.write(self.style.ERROR(f'❌ Backup failed: {result.stderr}'))
                backup_file.unlink(missing_ok=True)
                return
            
            # Check if backup file has content
            if backup_file.stat().st_size == 0:
                self.stdout.write(self.style.ERROR('❌ Backup file is empty'))
                backup_file.unlink()
                return
            
            backup_size = self._format_size(backup_file.stat().st_size)
            self.stdout.write(self.style.SUCCESS(f'✅ Backup created: {backup_size}'))
            
            # Compress the backup
            if compress:
                self.stdout.write('🗜️  Compressing backup...')
                result = subprocess.run(['gzip', str(backup_file)])
                
                if result.returncode == 0:
                    compressed_file = Path(str(backup_file) + '.gz')
                    compressed_size = self._format_size(compressed_file.stat().st_size)
                    self.stdout.write(self.style.SUCCESS(f'✅ Compressed: {compressed_size}'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Compression failed, keeping uncompressed backup'))
            
            # Clean up old backups
            self.stdout.write(f'🧹 Cleaning up backups older than {retention_days} days...')
            deleted_count = self._cleanup_old_backups(backup_dir, retention_days)
            
            if deleted_count > 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Deleted {deleted_count} old backup(s)'))
            
            # Show summary
            backup_files = list(backup_dir.glob('backup_*.sql*'))
            total_size = sum(f.stat().st_size for f in backup_files)
            
            self.stdout.write(self.style.SUCCESS('\n📊 Backup Summary:'))
            self.stdout.write(f'   Total backups: {len(backup_files)}')
            self.stdout.write(f'   Total size: {self._format_size(total_size)}')
            self.stdout.write(self.style.SUCCESS('\n🎉 Backup completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            backup_file.unlink(missing_ok=True)
    
    def _cleanup_old_backups(self, backup_dir, retention_days):
        """Delete backups older than retention_days"""
        import time
        
        deleted_count = 0
        cutoff_time = time.time() - (retention_days * 86400)  # 86400 seconds in a day
        
        for backup_file in backup_dir.glob('backup_*.sql*'):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                deleted_count += 1
        
        return deleted_count
    
    def _format_size(self, size_bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
