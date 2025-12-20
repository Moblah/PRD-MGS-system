import os
import psycopg2
import csv
import json

print("Importing data to PostgreSQL on Render...")

# Get PostgreSQL URL from environment (Render provides this)
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set in environment")
    exit(1)

# Fix URL format if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

print(f"Connecting to: {DATABASE_URL.split('@')[1]}")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL")
    
    # Tables to import
    tables = ['abr', 'activities', 'users']
    
    for table in tables:
        csv_file = f'{table}.csv'
        
        if not os.path.exists(csv_file):
            print(f"⚠️  {csv_file} not found, skipping {table}")
            continue
        
        print(f"\nImporting {table}...")
        
        # Read CSV
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            columns = next(reader)  # Header row
            rows = list(reader)
        
        print(f"  Found {len(rows)} rows, {len(columns)} columns")
        
        # Create table if not exists (simple version)
        placeholders = ', '.join(['%s'] * len(columns))
        column_defs = ', '.join([f'"{col}" TEXT' for col in columns])
        
        # Drop and create table
        cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
        cursor.execute(f'CREATE TABLE "{table}" ({column_defs})')
        
        # Insert data
        insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'
        cursor.executemany(insert_sql, rows)
        
        print(f"  ✅ Imported {len(rows)} rows into {table}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 IMPORT COMPLETE!")
    print("All data has been imported to PostgreSQL on Render.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
