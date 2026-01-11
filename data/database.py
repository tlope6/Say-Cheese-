import sqlite3

conn = sqlite3.connect("interactions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS INTERACTION (
    id INTEGER PRIMARY KEY, 
    action TEXT, 
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

def log_action(action) :
    cursor.execute("INSERT INTO interactions (action) VALUES (?)", (action,))
    conn.commit()
