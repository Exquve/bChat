import psycopg2

def create_db():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="4806"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('CREATE DATABASE chat_db;')
    cur.close()
    conn.close()

def create_table():
    conn = psycopg2.connect(
        host="localhost",
        database="chat_db",
        user="postgres",
        password="4806"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(50) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_db()
    create_table()