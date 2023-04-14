import sqlite3

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

def create_db():
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        username TEXT,
        pass_md5 TEXT,
        privileges TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    ) 
    """)

    connection.commit()

    cursor.execute(f""" 
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER,
        name TEXT,
        host TEXT,
        username TEXT,
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