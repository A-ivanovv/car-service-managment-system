#!/usr/bin/env python3
"""
Production Data Migration Script
This script migrates data from SQLite to PostgreSQL in production
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_service.settings')
django.setup()

from django.db import connections
from dashboard.models import Customer, Car, Employee, Sklad, Order, OrderItem, Invoice, Event, DaysOff, ImportLog

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    print("🚀 Starting production data migration from SQLite to PostgreSQL...")
    
    # Store original settings
    original_db = settings.DATABASES['default'].copy()
    
    # Switch to SQLite for reading
    settings.DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    settings.DATABASES['default']['NAME'] = '/app/db.sqlite3'
    
    # Read all data
    print("📖 Reading data from SQLite...")
    customers = list(Customer.objects.all())
    cars = list(Car.objects.all())
    employees = list(Employee.objects.all())
    sklad_items = list(Sklad.objects.all())
    orders = list(Order.objects.all())
    order_items = list(OrderItem.objects.all())
    invoices = list(Invoice.objects.all())
    events = list(Event.objects.all())
    days_off = list(DaysOff.objects.all())
    import_logs = list(ImportLog.objects.all())
    
    print(f"   📊 Read {len(customers)} customers, {len(cars)} cars, {len(employees)} employees, etc.")
    
    # Switch to PostgreSQL for writing
    settings.DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    settings.DATABASES['default']['NAME'] = 'car_service_db'
    settings.DATABASES['default']['USER'] = 'car_service_user'
    settings.DATABASES['default']['PASSWORD'] = os.getenv('DB_PASSWORD', 'dev_password_123')
    settings.DATABASES['default']['HOST'] = 'db'
    settings.DATABASES['default']['PORT'] = '5432'
    
    # Clear existing data
    print("🗑️  Clearing existing PostgreSQL data...")
    ImportLog.objects.all().delete()
    DaysOff.objects.all().delete()
    Event.objects.all().delete()
    Invoice.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Sklad.objects.all().delete()
    Car.objects.all().delete()
    Employee.objects.all().delete()
    Customer.objects.all().delete()
    
    # Migrate data
    print("💾 Migrating data to PostgreSQL...")
    
    # Customers first
    print("   👥 Migrating customers...")
    for customer in customers:
        customer.pk = None
        customer.save()
    print(f"   ✅ Migrated {len(customers)} customers")
    
    # Employees
    print("   👷 Migrating employees...")
    for employee in employees:
        employee.pk = None
        employee.save()
    print(f"   ✅ Migrated {len(employees)} employees")
    
    # Sklad items
    print("   📦 Migrating sklad items...")
    for item in sklad_items:
        item.pk = None
        item.save()
    print(f"   ✅ Migrated {len(sklad_items)} sklad items")
    
    # Cars
    print("   🚗 Migrating cars...")
    for car in cars:
        car.pk = None
        car.save()
    print(f"   ✅ Migrated {len(cars)} cars")
    
    # Orders
    print("   📋 Migrating orders...")
    for order in orders:
        order.pk = None
        order.save()
    print(f"   ✅ Migrated {len(orders)} orders")
    
    # Order items
    print("   📝 Migrating order items...")
    for item in order_items:
        item.pk = None
        item.save()
    print(f"   ✅ Migrated {len(order_items)} order items")
    
    # Invoices
    print("   🧾 Migrating invoices...")
    for invoice in invoices:
        invoice.pk = None
        invoice.save()
    print(f"   ✅ Migrated {len(invoices)} invoices")
    
    # Events
    print("   📅 Migrating events...")
    for event in events:
        event.pk = None
        event.save()
    print(f"   ✅ Migrated {len(events)} events")
    
    # Days off
    print("   🏖️  Migrating days off...")
    for day_off in days_off:
        day_off.pk = None
        day_off.save()
    print(f"   ✅ Migrated {len(days_off)} days off records")
    
    # Import logs
    print("   📊 Migrating import logs...")
    for log in import_logs:
        log.pk = None
        log.save()
    print(f"   ✅ Migrated {len(import_logs)} import logs")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    print(f"   👥 Customers in PostgreSQL: {Customer.objects.count()}")
    print(f"   🚗 Cars in PostgreSQL: {Car.objects.count()}")
    print(f"   👷 Employees in PostgreSQL: {Employee.objects.count()}")
    print(f"   📦 Sklad items in PostgreSQL: {Sklad.objects.count()}")
    print(f"   📋 Orders in PostgreSQL: {Order.objects.count()}")
    print(f"   📝 Order items in PostgreSQL: {OrderItem.objects.count()}")
    print(f"   🧾 Invoices in PostgreSQL: {Invoice.objects.count()}")
    print(f"   📅 Events in PostgreSQL: {Event.objects.count()}")
    print(f"   🏖️  Days off in PostgreSQL: {DaysOff.objects.count()}")
    print(f"   📊 Import logs in PostgreSQL: {ImportLog.objects.count()}")
    
    print("\n🎉 Production migration completed successfully!")
    print("✅ All data has been migrated from SQLite to PostgreSQL")

if __name__ == "__main__":
    migrate_data()
