import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]

print("\nAll tables in database:")
print("="*50)
for table in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] if not table.startswith('sqlite_') else 0
    if count > 0:
        print(f"✓ {table}: {count} rows")
    else:
        print(f"  {table}: {count} rows")

conn.close()

# Check what tournament tables are missing
required_tables = [
    'api_tournament', 'api_team', 'api_player', 'api_match', 
    'api_field', 'api_spiritscore', 'api_attendance',
    'api_tournamentannouncement', 'api_visitorregistration'
]

missing = [t for t in required_tables if t not in tables]
if missing:
    print("\n❌ Missing tournament tables:")
    for t in missing:
        print(f"   - {t}")
else:
    print("\n✅ All tournament tables exist!")
