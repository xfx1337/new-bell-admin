import sqlite3
from db.connection import connection

import user
from datetime import datetime
import db.tokens as tokens

cursor = connection.cursor()


def add_unverified(host, password):
    cursor.execute(f"""
    INSERT INTO devices (host, password) VALUES (?, ?)
    """, [host, password])
    db_id = cursor.lastrowid
    connection.commit()

    return db_id

def register(device):

    cursor.execute(f"""
    UPDATE devices SET name = ?, region = ? WHERE id = ?
    """, [device.name, device.region, device.id])
    connection.commit()

    return 0

def refresh(data):
    username = tokens.get_username(data['token'])
    data = data['user']

    cursor.execute(f"""
    UPDATE devices 
    SET lastseen=?,
    region=?
    WHERE name=?""", [datetime.strftime(datetime.now(), '%d.%M.%Y %H:%M'), data['region'], username])

    connection.commit()

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