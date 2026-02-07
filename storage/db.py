
import sqlite3
conn=sqlite3.connect("metrics.db",check_same_thread=False)
cur=conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS dau(region TEXT,value INT,event_ts INT,processed_ts INT)")
cur.execute("CREATE TABLE IF NOT EXISTS trade(region TEXT,count INT,volume REAL,event_ts INT,processed_ts INT)")
cur.execute("CREATE TABLE IF NOT EXISTS completeness(region TEXT,expected INT,observed INT,ratio REAL,event_ts INT,processed_ts INT)")
cur.execute("CREATE TABLE IF NOT EXISTS ai(severity TEXT,confidence REAL,nl TEXT,impact TEXT,actions TEXT,ts INT)")
conn.commit()

def insert(t, row_tuple):
    cur.execute(f"INSERT INTO {t} VALUES ({','.join('?'*len(row_tuple))})", row_tuple)
    conn.commit()

def fetch(t, limit=20):
    return cur.execute(f"SELECT * FROM {t} ORDER BY rowid DESC LIMIT {limit}").fetchall()
