# 🚀 Data Migration Guide - SQLite to PostgreSQL

This guide will help you migrate your existing data from SQLite to PostgreSQL.

## 📊 Current Data Status

Your SQLite database contains:
- **6,673 customers** 
- **2 cars**
- **1 employee**
- **11 sklad items**
- **4 orders**
- **9 order items**
- **3 invoices**
- Plus events, days off, and import logs

## 🛠️ Migration Options

### Option 1: Automated Setup (Recommended)

Run the complete setup script that will:
1. Start PostgreSQL container
2. Run Django migrations
3. Migrate all data from SQLite to PostgreSQL

```bash
cd /private/var/www/deyanski/Programa
./setup-with-migration.sh
```

### Option 2: Manual Step-by-Step

1. **Start the containers:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for PostgreSQL to be ready:**
   ```bash
   sleep 15
   ```

3. **Run Django migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Migrate the data:**
   ```bash
   docker-compose exec web python migrate_data.py
   ```

### Option 3: Interactive Migration

Run the interactive migration script:
```bash
docker-compose exec web python manual_migration.py
```

## 🔍 Verification

After migration, verify the data:

```bash
# Check PostgreSQL data
docker-compose exec web python manage.py shell -c "
from dashboard.models import Customer, Car, Employee, Sklad, Order;
print(f'Customers: {Customer.objects.count()}');
print(f'Cars: {Car.objects.count()}');
print(f'Employees: {Employee.objects.count()}');
print(f'Sklad: {Sklad.objects.count()}');
print(f'Orders: {Order.objects.count()}');
"
```

## 🎯 Expected Results

After successful migration, you should see:
- **6,673 customers** in PostgreSQL
- **2 cars** in PostgreSQL
- **1 employee** in PostgreSQL
- **11 sklad items** in PostgreSQL
- **4 orders** in PostgreSQL
- **9 order items** in PostgreSQL
- **3 invoices** in PostgreSQL
- All other data migrated successfully

## 🚨 Troubleshooting

### If migration fails:

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose ps
   ```

2. **Check PostgreSQL logs:**
   ```bash
   docker-compose logs db
   ```

3. **Check web container logs:**
   ```bash
   docker-compose logs web
   ```

4. **Reset and try again:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### If data doesn't match:

1. **Check SQLite data:**
   ```bash
   sqlite3 db.sqlite3 "SELECT COUNT(*) FROM dashboard_customer;"
   ```

2. **Check PostgreSQL data:**
   ```bash
   docker-compose exec web python manage.py shell -c "from dashboard.models import Customer; print(Customer.objects.count())"
   ```

## 🎉 Success!

Once migration is complete:
- Your application will run on PostgreSQL
- All 6,673+ records will be available
- You can access the application at http://localhost:8000
- PostgreSQL will be available at localhost:5432

## 📝 Next Steps

After successful migration:
1. Test the application thoroughly
2. Create a superuser account
3. Import any additional data if needed
4. Set up regular backups
5. Consider switching to production configuration
