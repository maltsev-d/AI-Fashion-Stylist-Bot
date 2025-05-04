import psycopg2
import config

conn = psycopg2.connect(
    config.DATABASE_URL
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
