import sqlite3

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

def create_database():
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        username TEXT,
        password TEXT,
        privileges TEXT,
        school TEXT,
        cpu_temp
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