valid_device_keys = ["host", "password", "lastupdate", "lastlogs", "cpu_temp", "institution"]

import sqlite3
import hashlib

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
        PRIMARY KEY(id AUTOINCREMENT)
    ) 
    """)

    connection.commit()

    cursor.execute(f"""
    INSERT INTO users (username, password, privileges) VALUES (?, ?, ?)
    """, ["newbell", hashlib.md5("Zvonki2023".encode("utf-8")).hexdigest(), "owner"])
    connection.commit()

    # dont forget to change valid_device_keys upper
    cursor.execute(f""" 
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER,
        verified INTEGER,
        name TEXT,
        host TEXT,
        password TEXT,
        lastseen TEXT,
        lastlogs TEXT,
        lastupdate TEXT,
        region TEXT,
        institution TEXT,
        cpu_temp TEXT,
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
        users_read TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    )
    """)

    connection.commit()

