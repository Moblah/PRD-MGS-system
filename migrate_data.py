import sqlite3
import psycopg2

print("=== MIGRATING YOUR 3 TABLES TO POSTGRESQL ===")
print("Tables: abr, activities, users")

# Connect to databases
print("\n1. Connecting to databases...")
try:
    # SQLite connection
    sqlite_conn = sqlite3.connect('instance/app.db')
    sqlite_cur = sqlite_conn.cursor()
    print("   ✓ Connected to SQLite (instance/app.db)")
    
    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        'postgresql://prd_mgs_db_user:0JZw5TbA6M38n0NxVxaopmWsBd4o1hRc@dpg-d532seer433s73c30tng-a:5432/prd_mgs_db'
    )
    pg_cur = pg_conn.cursor()
    print("   ✓ Connected to PostgreSQL on Render")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    exit(1)

# List tables
tables = ['abr', 'activities', 'users']

print("\n2. Checking SQLite data...")
for table in tables:
    sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = sqlite_cur.fetchone()[0]
    print(f"   {table}: {count} rows")

print("\n3. Starting migration...")

for table in tables:
    print(f"\n   --- Migrating '{table}' table ---")
    
    # Get all data
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    
    if not rows:
        print(f"      Table is empty, skipping")
        continue
    
    # Get column info for CREATE TABLE
    sqlite_cur.execute(f"PRAGMA table_info({table})")
    columns = sqlite_cur.fetchall()
    
    # Build CREATE TABLE statement
    col_defs = []
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        
        # Map SQLite types to PostgreSQL
        col_type_upper = col_type.upper() if col_type else 'TEXT'
        
        if 'INT' in col_type_upper:
            pg_type = 'INTEGER'
        elif 'TEXT' in col_type_upper or 'CHAR' in col_type_upper:
            pg_type = 'TEXT'
        elif 'REAL' in col_type_upper or 'FLOAT' in col_type_upper or 'DOUBLE' in col_type_upper:
            pg_type = 'REAL'
        elif 'BOOL' in col_type_upper:
            pg_type = 'BOOLEAN'
        elif 'DATE' in col_type_upper or 'TIME' in col_type_upper:
            pg_type = 'TIMESTAMP'
        else:
            pg_type = 'TEXT'
        
        # Add PRIMARY KEY if needed
        if pk:
            pg_type += ' PRIMARY KEY'
        
        col_defs.append(f'"{col_name}" {pg_type}')
    
    # Create table in PostgreSQL
    try:
        pg_cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
        create_sql = f'CREATE TABLE "{table}" ({", ".join(col_defs)})'
        pg_cur.execute(create_sql)
        print(f"      Created table structure")
    except Exception as e:
        print(f"      Error creating table: {e}")
        continue
    
    # Insert data
    try:
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'
        pg_cur.executemany(insert_sql, rows)
        print(f"      ✓ Inserted {len(rows)} rows")
    except Exception as e:
        print(f"      ✗ Error inserting: {e}")

# Commit changes
pg_conn.commit()

print("\n4. Verifying migration...")

# Verify counts match
print("\n   Final counts:")
all_good = True
for table in tables:
    # Get PostgreSQL count
    pg_cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    pg_count = pg_cur.fetchone()[0]
    
    # Get SQLite count
    sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
    sqlite_count = sqlite_cur.fetchone()[0]
    
    status = "✓" if pg_count == sqlite_count else "✗"
    if pg_count != sqlite_count:
        all_good = False
    
    print(f"      {table}: {sqlite_count} → {pg_count} rows {status}")

# Cleanup
pg_conn.close()
sqlite_conn.close()

if all_good:
    print("\n✅ SUCCESS: All data migrated to PostgreSQL!")
    print("\nNext steps:")
    print("1. Update config.py to use PostgreSQL URL")
    print("2. Add psycopg2-binary to requirements.txt")
    print("3. Deploy to Render")
else:
    print("\n⚠️  WARNING: Some counts don't match. Check errors above.")

