"""
Django management command to update customer temp_id field with original Customer-ID values
Usage: python manage.py update_customer_temp_ids
"""

import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import Customer

class Command(BaseCommand):
    help = 'Update customer temp_id field with original Customer-ID values from CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-file',
            type=str,
            default='/private/var/www/deyanski/archive/csv_files/customer_data_fixed.csv',
            help='Path to customer CSV file with original Customer-ID numbers'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any database changes'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔄 Updating Customer temp_id with original Customer-ID values"))
        self.stdout.write("="*70)
        
        customer_file = options['customer_file']
        
        if not os.path.exists(customer_file):
            self.stdout.write(self.style.ERROR(f"Customer file not found: {customer_file}"))
            return
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No database changes will be made"))
        
        try:
            # Read customer data
            self.stdout.write(f"📖 Reading customer data from {customer_file}...")
            
            with open(customer_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                customer_rows = list(reader)
            
            self.stdout.write(f"📊 Found {len(customer_rows)} customers in CSV file")
            
            # Get current customers from database
            self.stdout.write("📋 Loading existing customers from database...")
            existing_customers = {}
            
            for customer in Customer.objects.all():
                # Match by customer number (which should be the same as original Number field)
                existing_customers[customer.number] = customer
            
            self.stdout.write(f"👥 Found {len(existing_customers)} customers in database")
            
            # Update customers with temp_id
            updated_count = 0
            not_found_count = 0
            already_set_count = 0
            
            with transaction.atomic():
                for i, row in enumerate(customer_rows, 1):
                    if i % 500 == 0:
                        self.stdout.write(f"  Processed {i}/{len(customer_rows)} customers...")
                    
                    try:
                        # Extract original Customer-ID and Number
                        original_customer_id = row.get('Number', '').strip()
                        customer_name = row.get('Customer-Name', '').strip()
                        
                        if not original_customer_id:
                            continue
                        
                        original_customer_id = int(original_customer_id)
                        
                        # Find customer in database by number field
                        if original_customer_id in existing_customers:
                            customer = existing_customers[original_customer_id]
                            
                            # Check if temp_id is already set
                            if customer.temp_id is not None:
                                already_set_count += 1
                                continue
                            
                            # Update temp_id
                            if not options['dry_run']:
                                customer.temp_id = original_customer_id
                                customer.save(update_fields=['temp_id'])
                            else:
                                self.stdout.write(f"Would update customer {customer.customer_name} with temp_id={original_customer_id}")
                            
                            updated_count += 1
                            
                        else:
                            not_found_count += 1
                            if not_found_count <= 10:  # Only show first 10 not found
                                self.stdout.write(self.style.WARNING(f"Customer {original_customer_id} ({customer_name}) not found in database"))
                    
                    except (ValueError, TypeError) as e:
                        self.stdout.write(self.style.WARNING(f"Error processing customer row {i}: {e}"))
                        continue
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Unexpected error processing customer {original_customer_id}: {e}"))
                        continue
            
            # Show results
            self.stdout.write("\n" + "="*60)
            self.stdout.write("📈 UPDATE RESULTS")
            self.stdout.write("="*60)
            self.stdout.write(f"✅ Customers updated: {updated_count}")
            self.stdout.write(f"ℹ️  Already had temp_id: {already_set_count}")
            self.stdout.write(f"❌ Not found in database: {not_found_count}")
            self.stdout.write("="*60)
            
            if options['dry_run']:
                self.stdout.write(self.style.SUCCESS("\n✅ DRY RUN COMPLETED - No changes were made"))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n✅ TEMP_ID UPDATE COMPLETED!"))
                self.stdout.write(f"🎯 {updated_count} customers now have temp_id mapping")
                self.stdout.write(f"🔗 Ready for PO orders migration!")
            
            # Show sample mappings
            if not options['dry_run'] and updated_count > 0:
                self.stdout.write(f"\n🔍 Sample temp_id mappings:")
                sample_customers = Customer.objects.filter(temp_id__isnull=False)[:5]
                for customer in sample_customers:
                    self.stdout.write(f"  - Django ID {customer.id} → temp_id {customer.temp_id} ({customer.customer_name})")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"UPDATE FAILED: {e}"))
            import traceback
            traceback.print_exc()
