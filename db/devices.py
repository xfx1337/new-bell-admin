import sqlite3
from db.connection import connection

import user
from datetime import datetime
import db.tokens as tokens

cursor = connection.cursor()

def refresh(data):
    username = tokens.get_username(data['token'])
    data = data['user']

    cursor.execute(f"""
    UPDATE devices 
    SET lastseen=?,
    region=?
    WHERE name=?""", [datetime.strftime(datetime.now(), '%d.%M.%Y %H:%M'), data['region'], username])

    connection.commit()

def add_unverified(name: str = None, host: str = None, password: str = None, lastseen: str = None, region: str = None):
    cursor.execute(f"""
    INSERT INTO devices (name, host, password, lastseen, region, verified) VALUES (?, ?, ?, ?, ?, ?)
    """, [name, host, password, lastseen, region, False])

    connection.commit()

    cursor.execute(f"""SELECT ID FROM devices WHERE host=?""", [host])
    connection.commit()

    return len(cursor.fetchall())

def all():
    cursor.execute("SELECT * FROM devices")
    connection.commit()
    
    return [i.decode() if i is str else i for i in cursor.fetchall()]

def verify(id: int):
    cursor.execute(f"""
    UPDATE devices 
    SET verified=1
    WHERE id=?
    """, [id])

    connection.commit()

    cursor.execute(f"""SELECT ID FROM devices WHERE id=?""", [id])
    connection.commit()

    return len(cursor.fetchall())