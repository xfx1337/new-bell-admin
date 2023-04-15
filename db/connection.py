import sqlite3

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

def exists() -> bool:
    cursor.execute(f"""
    SELECT name FROM sqlite_master WHERE type='table' AND name='users';
    """)

    connection.commit()

    return bool(len(cursor.fetchall()))

def create_database():

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        username TEXT,
        password TEXT,
        privileges TEXT,
        school TEXT,
        cpu_temp TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    ) 
    """)

    connection.commit()

    cursor.execute(f"""
    INSERT INTO users (username, password, privileges) VALUES (?, ?, ?)
    """, ["newbell", "Zvonki2023", "owner"])
    connection.commit()

    cursor.execute(f""" 
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER,
        verified INTEGER,
        name TEXT,
        host TEXT,
        password TEXT,
        lastseen TEXT,
        region TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    )
    """)

    connection.commit()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER,
        username TEXT,
        token TEXT,
        expiration timestamp,
        PRIMARY KEY(id AUTOINCREMENT)
    )
    """)

    connection.commit()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS admin_events (
        id INTEGER,
        payload TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    )
    """)

    connection.commit()

