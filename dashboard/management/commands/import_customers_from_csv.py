import csv
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from dashboard.models import Customer
import re
from datetime import datetime


class Command(BaseCommand):
    help = 'Import clients from CSV file with Individual/Company classification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='customer_data_fixed.csv',
            help='Path to the CSV file (relative to project root)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of records to import (for testing)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing customers before import (DANGEROUS!)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        limit = options['limit']
        clear_existing = options['clear_existing']

        # Get absolute path to CSV file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        csv_path = os.path.join(project_root, csv_file)

        if not os.path.exists(csv_path):
            raise CommandError(f'CSV file not found: {csv_path}')

        self.stdout.write(f'Processing CSV file: {csv_path}')

        try:
            # Read and process CSV data
            customers_data = self.read_csv_data(csv_path)
            
            if limit:
                customers_data = customers_data[:limit]
                self.stdout.write(f'Limited to {limit} records for testing')

            # Show statistics
            self.show_migration_stats(customers_data)

            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - No data will be imported'))
                self.show_sample_data(customers_data)
                return

            # Clear existing data if requested
            if clear_existing:
                if input('Are you sure you want to clear all existing customers? (yes/no): ').lower() == 'yes':
                    Customer.objects.all().delete()
                    self.stdout.write(self.style.WARNING('Cleared all existing customers'))
                else:
                    self.stdout.write('Migration cancelled')
                    return

            # Import data
            self.import_customers(customers_data)

        except Exception as e:
            raise CommandError(f'Migration failed: {str(e)}')

    def read_csv_data(self, csv_path):
        """Read CSV data and handle encoding"""
        self.stdout.write('Reading CSV data...')
        
        customers = []
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'windows-1251', 'cp1251', 'latin1']
            
            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding, errors='replace') as infile:
                        reader = csv.DictReader(infile)
                        customers = list(reader)
                    self.stdout.write(f'Successfully read with {encoding} encoding')
                    break
                except UnicodeDecodeError:
                    continue
            
            if not customers:
                raise CommandError('Could not read CSV file with any supported encoding')
            
            # Process and classify customers
            self.stdout.write('Processing and classifying customers...')
            
            for customer in customers:
                # Clean string values
                for key, value in customer.items():
                    if value is None:
                        customer[key] = ''
                    else:
                        customer[key] = str(value).strip()
                        if customer[key] in ['nan', 'NULL', 'null']:
                            customer[key] = ''
                
                # Classify as company or individual
                business_fields = ['Customer-Bulstat', 'Customer-MOL', 'Customer-Taxno']
                is_company = False
                
                for field in business_fields:
                    value = customer.get(field, '').strip()
                    if value and value not in ['0', 'NULL', 'null', '', 'nan']:
                        is_company = True
                        break
                
                customer['customer_type'] = 'company' if is_company else 'individual'
            
            self.stdout.write(f'Processed {len(customers)} customer records')
            return customers
            
        except Exception as e:
            raise CommandError(f'Failed to read CSV file: {str(e)}')

    def show_migration_stats(self, customers):
        """Show migration statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MIGRATION STATISTICS')
        self.stdout.write('='*50)
        
        total = len(customers)
        companies = sum(1 for c in customers if c.get('customer_type') == 'company')
        individuals = sum(1 for c in customers if c.get('customer_type') == 'individual')
        
        self.stdout.write(f'Total customers: {total}')
        self.stdout.write(f'Companies: {companies} ({companies/total*100:.1f}%)')
        self.stdout.write(f'Individuals: {individuals} ({individuals/total*100:.1f}%)')
        
        # Show sample of each type
        self.stdout.write('\nSample Companies:')
        company_samples = [c for c in customers if c.get('customer_type') == 'company'][:3]
        for customer in company_samples:
            name = customer.get('Customer-Name', 'N/A')[:50]
            bulstat = customer.get('Customer-Bulstat', 'N/A')
            self.stdout.write(f'  - {name} (BULSTAT: {bulstat})')
        
        self.stdout.write('\nSample Individuals:')
        individual_samples = [c for c in customers if c.get('customer_type') == 'individual'][:3]
        for customer in individual_samples:
            name = customer.get('Customer-Name', 'N/A')[:50]
            phone = customer.get('Telno', 'N/A')
            self.stdout.write(f'  - {name} (Phone: {phone})')

    def show_sample_data(self, customers):
        """Show sample data for dry run"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SAMPLE DATA (DRY RUN)')
        self.stdout.write('='*50)
        
        # Show first few records
        sample = customers[:5]
        for idx, customer in enumerate(sample):
            self.stdout.write(f'\nRecord {idx + 1}:')
            self.stdout.write(f'  Name: {customer.get("Customer-Name", "N/A")}')
            self.stdout.write(f'  Type: {customer.get("customer_type", "N/A")}')
            self.stdout.write(f'  Address: {customer.get("Customer-Address-1", "N/A")}')
            self.stdout.write(f'  Phone: {customer.get("Telno", "N/A")}')
            if customer.get('customer_type') == 'company':
                self.stdout.write(f'  BULSTAT: {customer.get("Customer-Bulstat", "N/A")}')
                self.stdout.write(f'  MOL: {customer.get("Customer-MOL", "N/A")}')

    def import_customers(self, customers):
        """Import customers into Django database"""
        self.stdout.write('\nImporting customers...')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        with transaction.atomic():
            for idx, customer_data in enumerate(customers):
                try:
                    # Get or create customer
                    customer, created = self.create_customer_from_data(customer_data)
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    if (idx + 1) % 100 == 0:
                        self.stdout.write(f'Processed {idx + 1}/{len(customers)} customers...')
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row {idx + 1}: {str(e)}')
                    )
                    continue
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('IMPORT COMPLETED')
        self.stdout.write('='*50)
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        self.stdout.write(f'Errors: {error_count}')
        self.stdout.write(f'Total processed: {created_count + updated_count}')

    def create_customer_from_data(self, data):
        """Create or update a Customer object from data"""
        # Extract and clean data
        customer_number = self.clean_number(data.get('Number'))
        customer_name = self.clean_string(data.get('Customer-Name', ''))
        address = self.clean_string(data.get('Customer-Address-1', ''))
        phone = self.clean_string(data.get('Telno', ''))
        customer_type = data.get('customer_type', 'individual')
        
        # Company-specific fields
        mol = self.clean_string(data.get('Customer-MOL', '')) if customer_type == 'company' else ''
        taxno = self.clean_string(data.get('Customer-Taxno', '')) if customer_type == 'company' else ''
        bulstat = self.clean_string(data.get('Customer-Bulstat', '')) if customer_type == 'company' else ''
        
        # Additional fields
        email = self.clean_string(data.get('E-mail', ''))
        fax = self.clean_string(data.get('Faxno', ''))
        supplier = self.clean_boolean(data.get('supplier', False))
        active = self.clean_boolean(data.get('active', True))
        
        # Create or get customer
        customer, created = Customer.objects.get_or_create(
            number=customer_number,
            defaults={
                'customer_name': customer_name,
                'customer_address_1': address,
                'customer_mol': mol,
                'customer_taxno': taxno,
                'customer_bulstat': bulstat,
                'telno': phone,
                'email': email,
                'faxno': fax,
                'supplier': supplier,
                'active': active,
            }
        )
        
        # Update existing customer if not created
        if not created:
            customer.customer_name = customer_name
            customer.customer_address_1 = address
            customer.customer_mol = mol
            customer.customer_taxno = taxno
            customer.customer_bulstat = bulstat
            customer.telno = phone
            customer.email = email
            customer.faxno = fax
            customer.supplier = supplier
            customer.active = active
            customer.save()
        
        return customer, created

    def clean_string(self, value):
        """Clean string values"""
        if value is None:
            return ''
        return str(value).strip()

    def clean_number(self, value):
        """Clean number values"""
        if value is None or value == '':
            return None
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None

    def clean_boolean(self, value):
        """Clean boolean values"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        if isinstance(value, (int, float)):
            return bool(value)
        return False
