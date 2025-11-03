import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get api_tournament columns
columns = [r[1] for r in cur.execute("PRAGMA table_info(api_tournament)").fetchall()]
print("api_tournament columns:")
for col in columns:
    print(f"  - {col}")

conn.close()
