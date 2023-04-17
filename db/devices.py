import sqlite3

from streaming.stream import Stream

import user
from datetime import datetime
import db.tokens as tokens

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

def get_info(db_id):
    cursor.execute(f"""
    SELECT * FROM devices WHERE id = ?
    """, [db_id])
    content = cursor.fetchone()
    
    if content == None:
        return "Device not found", 0

    return 0, content

def get_info_json(db_id):
    ret, data = get_info(db_id)
    if ret != 0:
        return ret, data
    
    ret = {"verified": data[1], "name": data[2], "host": data[6]}
    return 0, ret

def add_unverified(host, password):
    cursor.execute(f"""
    INSERT INTO devices (verified, host, password) VALUES (?, ?, ?)
    """, [0, host, password])
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

def get_full_info():
    cursor.execute(f"""
    SELECT * FROM devices
    """)
    return cursor.fetchall()

def request(request):
    stream = Stream()
    stream.add(request.get_json())
    return "Added", 200