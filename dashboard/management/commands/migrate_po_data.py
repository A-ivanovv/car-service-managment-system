"""
Django management command to migrate historical PO orders and items
Usage: python manage.py migrate_po_data
"""

import csv
import os
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import Customer, Car, Order, OrderItem, Employee

class Command(BaseCommand):
    help = 'Migrate historical PO orders and items to Django system'
    
    def __init__(self):
        super().__init__()
        self.stats = {
            'cars_created': 0,
            'cars_matched': 0,
            'orders_created': 0,
            'order_items_created': 0,
            'errors': 0,
            'skipped': 0
        }
        self.employees_map = {}
        self.customer_cache = {}
        self.car_cache = {}
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--po-file',
            type=str,
            default='/private/var/www/deyanski/archive/database_files/po_data_final_bulgarian.csv',
            help='Path to PO data CSV file'
        )
        parser.add_argument(
            '--poitems-file',
            type=str,
            default='/private/var/www/deyanski/archive/database_files/poitems_bulgarian_final.csv',
            help='Path to POitems data CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any database changes'
        )
    
    def get_or_create_employee(self, author_name):
        """Get or create employee from author name"""
        if not author_name or author_name.strip() == '':
            return None
            
        author_name = author_name.strip()
        
        # Check cache first
        if author_name in self.employees_map:
            return self.employees_map[author_name]
        
        # Try to find existing employee
        name_parts = author_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
            
            if not self.options['dry_run']:
                employee, created = Employee.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={'is_active': True}
                )
            else:
                # Dry run - just simulate
                try:
                    employee = Employee.objects.get(first_name=first_name, last_name=last_name)
                    created = False
                except Employee.DoesNotExist:
                    employee = None
                    created = True
            
            if created and not self.options['dry_run']:
                self.stdout.write(f"✨ Created employee: {first_name} {last_name}")
            
            self.employees_map[author_name] = employee
            return employee
        
        return None
    
    def get_customer(self, customer_id):
        """Get customer by old Customer-ID number using temp_id field"""
        if customer_id in self.customer_cache:
            return self.customer_cache[customer_id]
        
        try:
            # Use temp_id field which contains the original Customer-ID from old system
            customer = Customer.objects.get(temp_id=int(customer_id))
            self.customer_cache[customer_id] = customer
            return customer
        except (Customer.DoesNotExist, ValueError):
            self.stdout.write(self.style.WARNING(f"Customer with temp_id {customer_id} not found"))
            return None
    
    def get_or_create_car(self, customer, vin, car_model, plate_number):
        """Get or create car for customer"""
        if not customer:
            return None
        
        # Create cache key
        cache_key = f"{customer.id}_{vin}_{plate_number}"
        if cache_key in self.car_cache:
            return self.car_cache[cache_key]
        
        # Try to find existing car by VIN first
        car = None
        if vin and vin.strip():
            try:
                car = Car.objects.filter(
                    customer=customer,
                    vin=vin.strip()
                ).first()
            except:
                pass
        
        # If not found by VIN, try by plate number
        if not car and plate_number and plate_number.strip():
            try:
                car = Car.objects.filter(
                    customer=customer,
                    plate_number=plate_number.strip()
                ).first()
            except:
                pass
        
        # If still not found, create new car
        if not car:
            car_data = {
                'customer': customer,
                'brand_model': car_model.strip() if car_model else 'Неизвестен модел',
                'vin': vin.strip() if vin else None,
                'plate_number': plate_number.strip() if plate_number else None,
                'is_active': True
            }
            
            if not self.options['dry_run']:
                try:
                    car = Car.objects.create(**car_data)
                    self.stats['cars_created'] += 1
                    self.stdout.write(f"🚗 Created car: {car}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating car: {e}"))
                    return None
            else:
                # Dry run simulation
                self.stats['cars_created'] += 1
                self.stdout.write(f"🚗 Would create car: {car_data['brand_model']} - {car_data['plate_number']}")
                car = None  # Simulate car creation
        else:
            self.stats['cars_matched'] += 1
        
        self.car_cache[cache_key] = car
        return car
    
    def parse_date(self, date_str):
        """Parse date string to Python date"""
        if not date_str:
            return None
        
        try:
            # Try MM/DD/YY HH:MM:SS format
            dt = datetime.strptime(date_str, '%m/%d/%y %H:%M:%S')
            return dt.date()
        except ValueError:
            try:
                # Try MM/DD/YYYY HH:MM:SS format
                dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
                return dt.date()
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Could not parse date: {date_str}"))
                return None
    
    def migrate_po_data(self, po_file_path):
        """Migrate PO orders data"""
        self.stdout.write(f"📖 Reading PO data from {po_file_path}...")
        
        with open(po_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            po_rows = list(reader)
        
        self.stdout.write(f"📊 Processing {len(po_rows)} PO records...")
        
        with transaction.atomic():
            for i, row in enumerate(po_rows, 1):
                if i % 1000 == 0:
                    self.stdout.write(f"  Processed {i}/{len(po_rows)} orders...")
                
                try:
                    # Extract data from row
                    po_number = row.get('PO', '').strip()
                    customer_id = row.get('Customer-ID', '').strip()
                    po_date_str = row.get('PODate', '').strip()
                    author = row.get('Author', '').strip()
                    vin = row.get('Chasis', '').strip()
                    car_model = row.get('Car', '').strip()
                    plate_number = row.get('DKNo', '').strip()
                    mileage_str = row.get('totkm', '').strip()
                    notes = row.get('Note', '').strip()
                    
                    # Skip if no PO number
                    if not po_number:
                        self.stats['skipped'] += 1
                        continue
                    
                    # Check if order already exists
                    if Order.objects.filter(order_number=po_number).exists():
                        continue  # Skip duplicate
                    
                    # Get customer
                    customer = self.get_customer(customer_id)
                    if not customer:
                        self.stdout.write(self.style.ERROR(f"No customer found for PO {po_number}, Customer-ID {customer_id}"))
                        self.stats['errors'] += 1
                        continue
                    
                    # Parse date
                    order_date = self.parse_date(po_date_str)
                    if not order_date:
                        self.stdout.write(self.style.ERROR(f"No valid date for PO {po_number}"))
                        self.stats['errors'] += 1
                        continue
                    
                    # Get or create car
                    car = self.get_or_create_car(customer, vin, car_model, plate_number)
                    
                    # Parse mileage
                    mileage = None
                    if mileage_str:
                        try:
                            mileage = int(float(mileage_str))
                        except ValueError:
                            pass
                    
                    # Get employee
                    employee = self.get_or_create_employee(author)
                    
                    # Create order
                    order_data = {
                        'order_number': po_number,
                        'order_date': order_date,
                        'client': customer,
                        'status': 'order',  # Historical orders are completed
                        'notes': f"Мигрирана поръчка от стара система. Автор: {author}" + (f"\nБележки: {notes}" if notes else "")
                    }
                    
                    # Add car information
                    if car:
                        order_data['car'] = car
                        if mileage:
                            order_data['car_mileage'] = mileage
                    else:
                        # Add standalone car info if no car object
                        order_data['car_brand_model'] = car_model if car_model else 'Неизвестен модел'
                        order_data['car_vin'] = vin if vin else None
                        order_data['car_plate_number'] = plate_number if plate_number else None
                        order_data['car_mileage'] = mileage
                    
                    # Create the order
                    if not self.options['dry_run']:
                        order = Order.objects.create(**order_data)
                        
                        # Add employee if found
                        if employee:
                            order.employees.add(employee)
                    else:
                        self.stdout.write(f"📋 Would create order: {po_number} for {customer.customer_name}")
                    
                    self.stats['orders_created'] += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing PO {po_number}: {e}"))
                    self.stats['errors'] += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS("✅ PO migration completed!"))
    
    def migrate_poitems_data(self, poitems_file_path):
        """Migrate POitems data to OrderItem objects"""
        self.stdout.write(f"📖 Reading POitems data from {poitems_file_path}...")
        
        with open(poitems_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            poitems_rows = list(reader)
        
        self.stdout.write(f"📊 Processing {len(poitems_rows)} POitems records...")
        
        with transaction.atomic():
            for i, row in enumerate(poitems_rows, 1):
                if i % 5000 == 0:
                    self.stdout.write(f"  Processed {i}/{len(poitems_rows)} items...")
                
                try:
                    # Extract data from row
                    po_id = row.get('POID', '').strip()
                    item_name = row.get('Item-Name', '').strip()
                    item_measure = row.get('Item-Measure', '').strip()
                    item_qty_str = row.get('Item-Qty', '').strip()
                    item_price_str = row.get('Item-Price-Each', '').strip()
                    item_total_str = row.get('Item-total', '').strip()
                    
                    # Skip if no essential data
                    if not po_id or not item_name:
                        self.stats['skipped'] += 1
                        continue
                    
                    # Find the order
                    try:
                        if not self.options['dry_run']:
                            order = Order.objects.get(order_number=po_id)
                        else:
                            # Simulate for dry run
                            order = None
                    except Order.DoesNotExist:
                        # Order not found, skip this item
                        continue
                    
                    # Parse numeric values
                    try:
                        quantity = Decimal(str(item_qty_str)) if item_qty_str else Decimal('1')
                    except:
                        quantity = Decimal('1')
                    
                    try:
                        # This should be price without VAT
                        price_each = Decimal(str(item_price_str)) if item_price_str else Decimal('0')
                    except:
                        price_each = Decimal('0')
                    
                    try:
                        total_price = Decimal(str(item_total_str)) if item_total_str else Decimal('0')
                    except:
                        total_price = Decimal('0')
                    
                    # Calculate price with VAT (assuming Item-total includes VAT)
                    # If total_price > price_each * quantity, then total includes VAT
                    calculated_total_without_vat = price_each * quantity
                    if total_price > calculated_total_without_vat:
                        # Total price includes VAT, so Item-Price-Each might be without VAT
                        price_with_vat = total_price / quantity if quantity > 0 else total_price
                        include_vat = True
                    else:
                        # Total price doesn't include VAT
                        price_with_vat = None
                        include_vat = False
                    
                    # Create order item
                    order_item_data = {
                        'order': order,
                        'name': item_name[:255],  # Truncate if too long
                        'unit': item_measure[:20] if item_measure else 'бр',
                        'quantity': quantity,
                        'purchase_price': price_each,
                        'price_with_vat': price_with_vat,
                        'include_vat': include_vat,
                        'is_labor': False  # Assume parts unless specified
                    }
                    
                    # Check if this is labor (труд) based on unit or name
                    if any(word in item_name.lower() for word in ['труд', 'работа', 'услуга', 'монтаж']):
                        order_item_data['is_labor'] = True
                    elif item_measure and any(word in item_measure.lower() for word in ['норма', 'час', 'мин']):
                        order_item_data['is_labor'] = True
                    
                    if not self.options['dry_run']:
                        OrderItem.objects.create(**order_item_data)
                    else:
                        self.stdout.write(f"📦 Would create item: {item_name} x {quantity} for PO {po_id}")
                    
                    self.stats['order_items_created'] += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing POitem for PO {po_id}: {e}"))
                    self.stats['errors'] += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS("✅ POitems migration completed!"))
    
    def print_statistics(self):
        """Print migration statistics"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📈 MIGRATION STATISTICS")
        self.stdout.write("="*60)
        self.stdout.write(f"🚗 Cars created: {self.stats['cars_created']}")
        self.stdout.write(f"🔗 Cars matched: {self.stats['cars_matched']}")
        self.stdout.write(f"📋 Orders created: {self.stats['orders_created']}")
        self.stdout.write(f"📦 Order items created: {self.stats['order_items_created']}")
        self.stdout.write(f"❌ Errors: {self.stats['errors']}")
        self.stdout.write(f"⏭️  Skipped: {self.stats['skipped']}")
        self.stdout.write("="*60)
        
        # Additional stats
        total_customers = Customer.objects.count()
        total_cars = Car.objects.count()
        total_orders = Order.objects.count()
        total_order_items = OrderItem.objects.count()
        
        self.stdout.write(f"\n📊 DATABASE TOTALS:")
        self.stdout.write(f"👥 Total customers: {total_customers}")
        self.stdout.write(f"🚗 Total cars: {total_cars}")
        self.stdout.write(f"📋 Total orders: {total_orders}")
        self.stdout.write(f"📦 Total order items: {total_order_items}")
    
    def handle(self, *args, **options):
        self.options = options
        
        self.stdout.write(self.style.SUCCESS("🚀 Starting PO Orders Migration to Django System"))
        self.stdout.write("="*60)
        
        # Check files exist
        po_file = options['po_file']
        poitems_file = options['poitems_file']
        
        if not os.path.exists(po_file):
            self.stdout.write(self.style.ERROR(f"PO file not found: {po_file}"))
            return
        
        if not os.path.exists(poitems_file):
            self.stdout.write(self.style.ERROR(f"POitems file not found: {poitems_file}"))
            return
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No database changes will be made"))
        
        try:
            # Migrate PO data first
            self.stdout.write("\n🔄 Phase 1: Migrating PO Orders...")
            self.migrate_po_data(po_file)
            
            # Then migrate POitems
            self.stdout.write("\n🔄 Phase 2: Migrating PO Items...")
            self.migrate_poitems_data(poitems_file)
            
            # Print final statistics
            self.print_statistics()
            
            if options['dry_run']:
                self.stdout.write(self.style.SUCCESS("\n✅ DRY RUN COMPLETED - No changes were made to the database"))
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ MIGRATION COMPLETED SUCCESSFULLY!"))
                self.stdout.write(self.style.SUCCESS("🎉 All historical PO data has been imported into your Django system!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"MIGRATION FAILED: {e}"))
            import traceback
            traceback.print_exc()
