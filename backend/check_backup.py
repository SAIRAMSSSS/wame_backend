import sqlite3
import os

databases = [
    ('OLD_BACKUP', 'db.sqlite3.old_backup'),
    ('BACKUP', 'db.sqlite3.backup'),
    ('CURRENT', 'db.sqlite3')
]

for name, dbfile in databases:
    if not os.path.exists(dbfile):
        print(f"\n{name} database ({dbfile}) - NOT FOUND")
        continue
        
    print(f"\n{'='*60}")
    print(f"Checking {name} database ({dbfile})...")
    print('='*60)
    
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    
    # Get all tables
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print(f"\nTotal tables: {len(tables)}")
    
    # Show api_ tables and their row counts
    api_tables = [t for t in tables if t.startswith('api_')]
    print(f"\nAPI Tables ({len(api_tables)} total):\n")
    
    total_rows = 0
    for table in api_tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count > 0:
            print(f"  ✓ {table}: {count} rows")
            total_rows += count
        else:
            print(f"    {table}: {count} rows")
    
    print(f"\nTotal data rows: {total_rows}")
    
    conn.close()
