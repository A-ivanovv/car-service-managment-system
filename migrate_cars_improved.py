#!/usr/bin/env python3
"""
Improved migration script to import car data and match with existing customers
Handles duplicate VINs properly by deduplicating cars per customer
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_service.settings')
django.setup()

from dashboard.models import Customer, Car

def analyze_data():
    """Analyze the data before migration"""
    print("🔍 ANALYZING DATA FOR MIGRATION")
    print("=" * 50)
    
    # Load car data
    car_df = pd.read_csv('complete_car_records.csv')
    print(f"📊 Car records loaded: {len(car_df)}")
    
    # Load customer data
    customer_df = pd.read_csv('customer_data_fixed.csv')
    print(f"👥 Customer records loaded: {len(customer_df)}")
    
    # Check current database
    db_customers = Customer.objects.count()
    db_cars = Car.objects.count()
    print(f"🗄️  Current DB - Customers: {db_customers}, Cars: {db_cars}")
    
    # Analyze matching potential
    car_customer_ids = set(car_df['Customer-ID'].dropna().astype(int))
    customer_numbers = set(customer_df['Number'].dropna().astype(int))
    
    matching_ids = car_customer_ids.intersection(customer_numbers)
    print(f"🔗 Matching Customer-IDs: {len(matching_ids)}")
    print(f"   Car records with matching customers: {len(car_df[car_df['Customer-ID'].isin(matching_ids)])}")
    
    # Sample matches
    print("\n📋 SAMPLE MATCHES:")
    sample_matches = list(matching_ids)[:5]
    for customer_id in sample_matches:
        customer = customer_df[customer_df['Number'] == customer_id].iloc[0]
        car_count = len(car_df[car_df['Customer-ID'] == customer_id])
        print(f"   Customer {customer_id}: {customer['Customer-Name']} - {car_count} cars")
    
    return car_df, customer_df, matching_ids

def get_latest_mileage(car_group):
    """Get the latest mileage for a car from its records"""
    # Filter out invalid mileage values
    valid_mileage = car_group[
        (car_group['totkm'].notna()) & 
        (car_group['totkm'] != '') & 
        (car_group['totkm'] != 'nan') &
        (car_group['totkm'] > 0)
    ]['totkm']
    
    if len(valid_mileage) > 0:
        # Return the maximum mileage (latest)
        return int(valid_mileage.max())
    
    return None

def deduplicate_cars(car_df, matching_ids):
    """Deduplicate cars by customer and VIN/plate number, including latest mileage"""
    print("\n🔄 DEDUPLICATING CARS")
    print("=" * 30)
    
    # Filter to matching customers only
    matching_cars = car_df[car_df['Customer-ID'].isin(matching_ids)].copy()
    
    # Clean the data
    matching_cars['Car'] = matching_cars['Car'].fillna('').astype(str).str.strip()
    matching_cars['DKNo'] = matching_cars['DKNo'].fillna('').astype(str).str.strip()
    matching_cars['Chasis'] = matching_cars['Chasis'].fillna('').astype(str).str.strip()
    
    # Remove empty records
    matching_cars = matching_cars[
        (matching_cars['Car'] != '') | 
        (matching_cars['DKNo'] != '') | 
        (matching_cars['Chasis'] != '')
    ]
    
    print(f"📊 After cleaning: {len(matching_cars)} records")
    
    # Group by customer and create unique cars
    unique_cars = []
    
    for customer_id in matching_ids:
        customer_cars = matching_cars[matching_cars['Customer-ID'] == customer_id]
        
        # Group by VIN first (most unique identifier)
        vin_groups = customer_cars.groupby('Chasis')
        
        for vin, vin_group in vin_groups:
            if vin and vin != 'nan' and vin != '':
                # Take the first record with this VIN
                car_record = vin_group.iloc[0]
                
                # Calculate latest mileage for this car
                latest_mileage = get_latest_mileage(vin_group)
                
                unique_cars.append({
                    'customer_id': int(customer_id),
                    'brand_model': car_record['Car'],
                    'plate_number': car_record['DKNo'],
                    'vin': vin,
                    'current_mileage': latest_mileage,
                    'record_count': len(vin_group)
                })
        
        # For cars without VIN, group by plate number
        no_vin_cars = customer_cars[
            (customer_cars['Chasis'] == '') | 
            (customer_cars['Chasis'] == 'nan') |
            (customer_cars['Chasis'].isna())
        ]
        
        if len(no_vin_cars) > 0:
            plate_groups = no_vin_cars.groupby('DKNo')
            
            for plate, plate_group in plate_groups:
                if plate and plate != 'nan' and plate != '':
                    # Take the first record with this plate
                    car_record = plate_group.iloc[0]
                    
                    # Calculate latest mileage for this car
                    latest_mileage = get_latest_mileage(plate_group)
                    
                    unique_cars.append({
                        'customer_id': int(customer_id),
                        'brand_model': car_record['Car'],
                        'plate_number': plate,
                        'vin': '',
                        'current_mileage': latest_mileage,
                        'record_count': len(plate_group)
                    })
    
    print(f"✅ Unique cars identified: {len(unique_cars)}")
    
    # Show statistics
    with_vin = len([c for c in unique_cars if c['vin']])
    with_plate = len([c for c in unique_cars if c['plate_number']])
    with_mileage = len([c for c in unique_cars if c['current_mileage'] is not None])
    print(f"   Cars with VIN: {with_vin}")
    print(f"   Cars with plate: {with_plate}")
    print(f"   Cars with mileage: {with_mileage}")
    
    return unique_cars

def migrate_cars(unique_cars, customer_df):
    """Migrate unique cars to Django database"""
    print("\n🚀 STARTING CAR MIGRATION")
    print("=" * 40)
    
    # Create customer lookup dictionary
    customer_lookup = {}
    for _, customer in customer_df.iterrows():
        customer_lookup[int(customer['Number'])] = customer
    
    # Track statistics
    stats = {
        'processed': 0,
        'created': 0,
        'skipped': 0,
        'errors': 0,
        'customers_with_cars': set()
    }
    
    # Process each unique car
    for car_data in unique_cars:
        try:
            stats['processed'] += 1
            
            customer_id = car_data['customer_id']
            
            # Find customer in Django
            try:
                customer = Customer.objects.get(number=customer_id)
            except Customer.DoesNotExist:
                print(f"⚠️  Customer {customer_id} not found in Django DB, skipping car")
                stats['skipped'] += 1
                continue
            
            # Check if car already exists
            existing_car = None
            
            # First check by VIN (if available)
            if car_data['vin']:
                existing_car = Car.objects.filter(
                    customer=customer,
                    vin=car_data['vin']
                ).first()
            
            # If not found by VIN, check by plate number
            if not existing_car and car_data['plate_number']:
                existing_car = Car.objects.filter(
                    customer=customer,
                    plate_number=car_data['plate_number']
                ).first()
            
            if existing_car:
                # Update existing car with mileage data if we have it
                if car_data['current_mileage'] and existing_car.current_mileage != car_data['current_mileage']:
                    existing_car.current_mileage = car_data['current_mileage']
                    existing_car.save()
                    stats['updated'] = stats.get('updated', 0) + 1
                else:
                    stats['skipped'] += 1
                continue
            
            # Create new car
            car = Car.objects.create(
                customer=customer,
                brand_model=car_data['brand_model'],
                plate_number=car_data['plate_number'] if car_data['plate_number'] else '',
                vin=car_data['vin'] if car_data['vin'] else '',
                year=None,
                color='',
                engine_number='',
                current_mileage=car_data['current_mileage'],
                is_active=True,
            )
            
            stats['created'] += 1
            stats['customers_with_cars'].add(customer_id)
            
            # Progress update
            if stats['processed'] % 1000 == 0:
                updated_count = stats.get('updated', 0)
                print(f"   Processed: {stats['processed']}, Created: {stats['created']}, Updated: {updated_count}")
                
        except Exception as e:
            stats['errors'] += 1
            print(f"❌ Error processing car: {e}")
            continue
    
    return stats

def generate_report(stats, unique_cars):
    """Generate migration report"""
    print("\n📊 MIGRATION REPORT")
    print("=" * 30)
    
    print(f"✅ Unique cars processed: {stats['processed']}")
    print(f"✅ Cars created: {stats['created']}")
    print(f"🔄 Cars updated: {stats.get('updated', 0)}")
    print(f"⚠️  Cars skipped: {stats['skipped']}")
    print(f"❌ Errors: {stats['errors']}")
    print(f"👥 Customers with cars: {len(stats['customers_with_cars'])}")
    
    # Calculate percentages
    if stats['processed'] > 0:
        total_processed = stats['created'] + stats.get('updated', 0)
        success_rate = (total_processed / stats['processed']) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Show some examples
    print("\n🎯 SAMPLE CREATED CARS:")
    recent_cars = Car.objects.filter(customer__number__in=list(stats['customers_with_cars'])[:10])
    for car in recent_cars:
        print(f"   {car.customer.customer_name} - {car.brand_model} ({car.plate_number})")

def main():
    """Main migration function"""
    print("🚗 IMPROVED CAR MIGRATION TOOL")
    print("=" * 50)
    print("This script will deduplicate and import unique cars from PO records")
    print()
    
    # Check if files exist
    if not os.path.exists('complete_car_records.csv'):
        print("❌ complete_car_records.csv not found!")
        return False
    
    if not os.path.exists('customer_data_fixed.csv'):
        print("❌ customer_data_fixed.csv not found!")
        return False
    
    try:
        # Analyze data
        car_df, customer_df, matching_ids = analyze_data()
        
        # Deduplicate cars
        unique_cars = deduplicate_cars(car_df, matching_ids)
        
        # Confirm migration
        print(f"\n⚠️  READY TO MIGRATE {len(unique_cars)} UNIQUE CARS")
        print("This will create new Car records in the database.")
        print("Auto-proceeding with migration...")
        
        # Migrate cars
        stats = migrate_cars(unique_cars, customer_df)
        
        # Generate report
        generate_report(stats, unique_cars)
        
        print("\n✅ MIGRATION COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
