import os
import sys
import subprocess
import tempfile
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from dashboard.models import Customer, Car
import re
from datetime import datetime


class Command(BaseCommand):
    help = 'Migrate clients from MDB file to Django database with Individual/Company classification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mdb-file',
            type=str,
            default='archive/database_files/inv97_be.mdb',
            help='Path to the MDB file (relative to project root)'
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
        mdb_file = options['mdb_file']
        dry_run = options['dry_run']
        limit = options['limit']
        clear_existing = options['clear_existing']

        # Get absolute path to MDB file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        mdb_path = os.path.join(project_root, mdb_file)

        if not os.path.exists(mdb_path):
            raise CommandError(f'MDB file not found: {mdb_path}')

        self.stdout.write(f'Processing MDB file: {mdb_path}')

        try:
            # Extract data from MDB
            customers_data = self.extract_customer_data(mdb_path)
            
            if limit:
                customers_data = customers_data.head(limit)
                self.stdout.write(f'Limited to {limit} records for testing')

            # Classify customers
            classified_data = self.classify_customers(customers_data)
            
            # Show statistics
            self.show_migration_stats(classified_data)

            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - No data will be imported'))
                self.show_sample_data(classified_data)
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
            self.import_customers(classified_data)

        except Exception as e:
            raise CommandError(f'Migration failed: {str(e)}')

    def extract_customer_data(self, mdb_path):
        """Extract customer data from MDB file and fix encoding"""
        self.stdout.write('Extracting data from MDB file...')
        
        try:
            # Use mdb-export to extract data
            result = subprocess.run(
                ['mdb-export', mdb_path, 'Customer'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                # Try with different encoding if UTF-8 fails
                result = subprocess.run(
                    ['mdb-export', mdb_path, 'Customer'],
                    capture_output=True,
                    text=True,
                    encoding='windows-1251',
                    errors='replace'
                )
            
            if result.returncode != 0:
                raise CommandError(f'mdb-export failed: {result.stderr}')

            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
                f.write(result.stdout)
                temp_file = f.name

            # Read with pandas
            df = pd.read_csv(temp_file, encoding='utf-8')
            
            # Clean up temp file
            os.unlink(temp_file)
            
            self.stdout.write(f'Extracted {len(df)} customer records')
            return df

        except FileNotFoundError:
            raise CommandError('mdb-tools not found. Please install with: brew install mdbtools')
        except Exception as e:
            raise CommandError(f'Failed to extract data: {str(e)}')

    def classify_customers(self, df):
        """Classify customers as Individual or Company based on business fields"""
        self.stdout.write('Classifying customers...')
        
        # Clean the data
        df = df.fillna('')
        
        # Define business fields that indicate a company
        business_fields = ['Customer-Bulstat', 'Customer-MOL', 'Customer-Taxno']
        
        # Create classification
        def is_company(row):
            # Check if any business field has meaningful data
            for field in business_fields:
                value = str(row.get(field, '')).strip()
                if value and value not in ['0', 'NULL', 'null', '']:
                    return True
            return False
        
        df['customer_type'] = df.apply(is_company, axis=1)
        df['customer_type'] = df['customer_type'].map({True: 'company', False: 'individual'})
        
        # Count classifications
        company_count = (df['customer_type'] == 'company').sum()
        individual_count = (df['customer_type'] == 'individual').sum()
        
        self.stdout.write(f'Classified: {company_count} companies, {individual_count} individuals')
        
        return df

    def show_migration_stats(self, df):
        """Show migration statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MIGRATION STATISTICS')
        self.stdout.write('='*50)
        
        total = len(df)
        companies = (df['customer_type'] == 'company').sum()
        individuals = (df['customer_type'] == 'individual').sum()
        
        self.stdout.write(f'Total customers: {total}')
        self.stdout.write(f'Companies: {companies} ({companies/total*100:.1f}%)')
        self.stdout.write(f'Individuals: {individuals} ({individuals/total*100:.1f}%)')
        
        # Show sample of each type
        self.stdout.write('\nSample Companies:')
        company_samples = df[df['customer_type'] == 'company'].head(3)
        for _, row in company_samples.iterrows():
            name = str(row.get('Customer-Name', 'N/A'))[:50]
            bulstat = str(row.get('Customer-Bulstat', 'N/A'))
            self.stdout.write(f'  - {name} (BULSTAT: {bulstat})')
        
        self.stdout.write('\nSample Individuals:')
        individual_samples = df[df['customer_type'] == 'individual'].head(3)
        for _, row in individual_samples.iterrows():
            name = str(row.get('Customer-Name', 'N/A'))[:50]
            phone = str(row.get('Telno', 'N/A'))
            self.stdout.write(f'  - {name} (Phone: {phone})')

    def show_sample_data(self, df):
        """Show sample data for dry run"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SAMPLE DATA (DRY RUN)')
        self.stdout.write('='*50)
        
        # Show first few records
        sample = df.head(5)
        for idx, row in sample.iterrows():
            self.stdout.write(f'\nRecord {idx + 1}:')
            self.stdout.write(f'  Name: {row.get("Customer-Name", "N/A")}')
            self.stdout.write(f'  Type: {row.get("customer_type", "N/A")}')
            self.stdout.write(f'  Address: {row.get("Customer-Address-1", "N/A")}')
            self.stdout.write(f'  Phone: {row.get("Telno", "N/A")}')
            if row.get('customer_type') == 'company':
                self.stdout.write(f'  BULSTAT: {row.get("Customer-Bulstat", "N/A")}')
                self.stdout.write(f'  MOL: {row.get("Customer-MOL", "N/A")}')

    def import_customers(self, df):
        """Import customers into Django database"""
        self.stdout.write('\nImporting customers...')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # Get or create customer
                    customer, created = self.create_customer_from_row(row)
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    if (idx + 1) % 100 == 0:
                        self.stdout.write(f'Processed {idx + 1}/{len(df)} customers...')
                        
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

    def create_customer_from_row(self, row):
        """Create or update a Customer object from a data row"""
        # Extract and clean data
        customer_number = self.clean_number(row.get('Number'))
        customer_name = self.clean_string(row.get('Customer-Name', ''))
        address = self.clean_string(row.get('Customer-Address-1', ''))
        phone = self.clean_string(row.get('Telno', ''))
        customer_type = row.get('customer_type', 'individual')
        
        # Company-specific fields
        mol = self.clean_string(row.get('Customer-MOL', '')) if customer_type == 'company' else ''
        taxno = self.clean_string(row.get('Customer-Taxno', '')) if customer_type == 'company' else ''
        bulstat = self.clean_string(row.get('Customer-Bulstat', '')) if customer_type == 'company' else ''
        
        # Additional fields
        email = self.clean_string(row.get('E-mail', ''))
        fax = self.clean_string(row.get('Faxno', ''))
        supplier = bool(row.get('supplier', False))
        active = bool(row.get('active', True))
        
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
        if pd.isna(value) or value is None:
            return ''
        return str(value).strip()

    def clean_number(self, value):
        """Clean number values"""
        if pd.isna(value) or value is None:
            return None
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None
