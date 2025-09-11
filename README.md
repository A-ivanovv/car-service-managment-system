# MDB to PostgreSQL Data Migration

This project documents the successful extraction and migration of customer data from a Microsoft Access Database (MDB) file to PostgreSQL.

## Overview

**Source:** `inv97_be.mdb` - Microsoft Access Database containing customer information in Bulgarian  
**Target:** PostgreSQL 16 database with UTF-8 encoding  
**Records:** 6,670 customer records successfully migrated

## Problem Statement

The original MDB file contained customer data with Bulgarian text encoded in Windows-1251 (Cyrillic), which caused display issues when exported directly. The challenge was to:

1. Extract data from the MDB file
2. Fix the character encoding from Windows-1251 to UTF-8
3. Import the corrected data into a modern PostgreSQL database

## Tools Used

- **mdb-tools**: Command-line utilities for reading MDB files on macOS
- **Python 3**: For data processing and encoding conversion
- **Docker**: For running PostgreSQL in a containerized environment
- **PostgreSQL 16**: Target database system

## Step-by-Step Process

### 1. MDB File Analysis

First, we examined the structure of the MDB file:

```bash
# List all tables in the MDB file
mdb-tables inv97_be.mdb

# Get schema information
mdb-schema inv97_be.mdb
```

**Key Finding:** The file contained a `Customer` table with 6,670 records.

### 2. Data Extraction

Extracted the customer data to CSV format:

```bash
# Export customer table to CSV
mdb-export inv97_be.mdb Customer > customer_data_raw.csv
```

**Problem Encountered:** The exported CSV contained Bulgarian text encoded in Windows-1251, displaying as garbled characters.

### 3. Encoding Fix

Created a Python script to convert the encoding from Windows-1251 to UTF-8:

**File:** `fix_encoding.py`

```python
import pandas as pd
import sys

input_file = "customer_data_raw.csv"
output_file = "customer_data_fixed.csv"

try:
    # Read the CSV with Windows-1251 encoding
    df = pd.read_csv(input_file, encoding='windows-1251')
    
    # Save it back with UTF-8 encoding
    df.to_csv(output_file, encoding='utf-8', index=False)
    
    print(f"Processing customer data...")
    print(f"Fixed data saved to {output_file}")
    
    # Print first 5 lines of fixed data for verification
    with open(output_file, 'r', encoding='utf-8') as f:
        print("\nFirst 5 lines of fixed data:")
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(line.strip())

except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
```

**Result:** Successfully converted 6,670 records with proper Bulgarian text display.

### 4. PostgreSQL Database Setup

Created a PostgreSQL 16 container:

```bash
# Create PostgreSQL container
docker run --name postgres-business-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=business_db \
  -p 5433:5432 \
  -d postgres:16
```

### 5. Data Import Script

Created a comprehensive Python script for importing data into PostgreSQL:

**File:** `import_customers_postgres.py`

Key features:
- Handles column names with hyphens and spaces (quoted identifiers)
- Proper UTF-8 character set support
- Batch processing for large datasets
- Date parsing for various formats
- Boolean field conversion
- Error handling and rollback support

### 6. Database Schema

The final PostgreSQL schema includes:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    "Number" INTEGER,
    "Customer-Name" VARCHAR(255) NOT NULL,
    "Customer-Address-1" VARCHAR(255),
    "Customer-Address-2" VARCHAR(255),
    "Customer-MOL" VARCHAR(255),
    "Customer-Taxno" VARCHAR(20),
    "Customer-DocType" SMALLINT,
    "Receiver" VARCHAR(255),
    "Receiver Details" VARCHAR(255),
    "Customer-Bulstat" VARCHAR(11),
    "Telno" VARCHAR(50),
    "Faxno" VARCHAR(50),
    "E-mail" VARCHAR(50),
    "ResAddress1" VARCHAR(255),
    "ResAddress2" VARCHAR(255),
    eidate TIMESTAMP,
    "include" BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    customer BOOLEAN NOT NULL DEFAULT TRUE,
    supplier BOOLEAN NOT NULL DEFAULT FALSE,
    "Contact" VARCHAR(255),
    partida INTEGER,
    bulstatletter VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Final Results

### Database Connection Details
- **Host:** 127.0.0.1
- **Port:** 5433
- **Database:** business_db
- **Username:** postgres
- **Password:** password

### Data Statistics
- **Total customers:** 6,670
- **Active customers:** 6,666
- **Unique cities:** 136
- **Customers in Sofia:** 375
- **Character encoding:** UTF-8 (Bulgarian text displays correctly)

### Sample Data Verification

```sql
SELECT "Number", "Customer-Name", "Customer-Address-1", "Customer-Taxno" 
FROM customers 
WHERE "Customer-Name" LIKE '%СОФИЯ%' 
ORDER BY "Number" 
LIMIT 5;
```

**Result:**
```
 Number |          Customer-Name           | Customer-Address-1 | Customer-Taxno
--------+----------------------------------+--------------------+-----------------
     73 | ГА Б-Я СОФИЯ 1 ЗАПАД ЕООД        | СОФИЯ              | BG121886952
    915 | Б Д Ж - ПП ЕООД - ППП СОФИЯ      | София              | BG175405647
    932 | ПОДЕЛЕНИЕ-ТСВ СОФИЯ              | СОФИЯ              | BG1308471160048
    979 | ЕТ ДОК СТЕП-СОФИЯ                | СОФИЯ              | BG831143844
   1012 | СОФИЯ ЛИФТ-9  ЕООД               | СОФИЯ              | BG175015004
```

## Key Lessons Learned

1. **Character Encoding:** MDB files often use Windows-1251 encoding for Cyrillic text, requiring conversion to UTF-8 for modern databases.

2. **Column Names:** Access databases can have column names with spaces and hyphens, requiring quoted identifiers in PostgreSQL.

3. **Data Types:** Careful mapping of Access data types to PostgreSQL equivalents is crucial for data integrity.

4. **Batch Processing:** Large datasets benefit from batch processing to avoid memory issues and improve performance.

5. **Error Handling:** Robust error handling and rollback mechanisms ensure data consistency during migration.

## Files Created

- `fix_encoding.py` - Encoding conversion script
- `import_customers_postgres.py` - PostgreSQL import script
- `customer_data_fixed.csv` - UTF-8 encoded customer data
- `README.md` - This documentation

## Prerequisites

- macOS with Homebrew
- Docker
- Python 3 with pandas and psycopg2-binary
- mdb-tools (`brew install mdbtools`)

## Usage

1. Extract data from MDB:
   ```bash
   mdb-export inv97_be.mdb Customer > customer_data_raw.csv
   ```

2. Fix encoding:
   ```bash
   python fix_encoding.py
   ```

3. Start PostgreSQL container:
   ```bash
   docker run --name postgres-business-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=business_db -p 5433:5432 -d postgres:16
   ```

4. Import data:
   ```bash
   python import_customers_postgres.py
   ```

## Conclusion

The migration was successful, preserving all customer data with proper Bulgarian text encoding. The PostgreSQL database is now ready for use with modern database tools and applications.
