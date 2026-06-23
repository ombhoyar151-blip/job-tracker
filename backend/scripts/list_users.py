import sqlite3

conn = sqlite3.connect('job_tracker.db')
cur = conn.cursor()
try:
    cur.execute("SELECT id, email, password_hash FROM users")
    rows = cur.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print('ERROR', e)
finally:
    conn.close()
