import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE: db.sqlite3")
print("=" * 60)
print("\nTABLES IN DATABASE:")
print("-" * 60)

for table in tables:
    table_name = table[0]
    print(f"\n📊 {table_name}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Rows: {count}")
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"   Columns: {', '.join([col[1] for col in columns])}")

conn.close()
print("\n" + "=" * 60)
