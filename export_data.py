import sqlite3
import json
import csv

print("Exporting SQLite data...")

# Connect to SQLite
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print(f"Found tables: {tables}")

# Export each table
for table in tables:
    print(f"\nExporting {table}...")
    
    # Get data
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Export to CSV
    with open(f'{table}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)
    
    # Export to JSON
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))
    
    with open(f'{table}.json', 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)
    
    print(f"  Exported {len(rows)} rows to {table}.csv and {table}.json")

conn.close()
print("\n✅ Export complete! Files created:")
for table in tables:
    print(f"  - {table}.csv")
    print(f"  - {table}.json")
