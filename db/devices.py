import sqlite3
import threading

import user
from datetime import datetime
import db.tokens

from db.connection import valid_device_keys

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

lock = threading.Lock()

def get_info(db_id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices WHERE id = ?
        """, [db_id])
        content = cursor.fetchone()
        
        if content == None:
            return "Device not found", 0

        return 0, content

def get_info_json(db_id, fully=False):
    ret, data = get_info(db_id)
    if ret != 0:
        return ret, data
    if not fully:
        ret = {"verified": data[1], "name": data[2], "host": data[3], "token": db.tokens.get_token(db_id)}
    else:
        ret = {"verified": data[1], "name": data[2], "host": data[3], "password": data[4], "token": db.tokens.get_token(db_id), 
               "lastseen": data[5], "lastlogs": data[6], "lastupdate": data[7], "region": data[8], 
               'institution': data[9], "cpu_temp": data[10]}
    return 0, ret

def add_unverified(host, password):
    with lock:
        cursor.execute(f"""
        INSERT INTO devices (verified, host, password) VALUES (?, ?, ?)
        """, [0, host, password])
        db_id = cursor.lastrowid
        connection.commit()

        return db_id

def register(device):
    with lock:
        cursor.execute(f"""
        UPDATE devices SET name = ?, region = ?, institution = ? WHERE id = ?
        """, [device.name, device.region, device.institution, device.id])
        connection.commit()

        return 0

def login(data):
    content = None
    with lock:
        cursor.execute(f"""
            SELECT * FROM devices WHERE id = ?
            """, [data["device_id"]])

        content = cursor.fetchone()
        connection.commit()
        
    if content == None:
        return -1, "No device with this id"
    
    if content[4] != data["password"]:
        return -1, "Wrong password"
    return 0, db.tokens.get_token(data["device_id"])

def refresh(data):
    username = db.tokens.get_username(data['token'])
    data = data['user']
    with lock:
        cursor.execute(f"""
        UPDATE devices 
        SET lastseen=?,
        region=?
        WHERE name=?""", [datetime.strftime(datetime.now(), '%d.%M.%Y %H:%M'), data['region'], username])

        connection.commit()

def all():
    with lock:
        cursor.execute("SELECT * FROM devices")
        connection.commit()
        
        return [i.decode() if i is str else i for i in cursor.fetchall()]

def verify(id: int):
    with lock:
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
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices
        """)
        return cursor.fetchall()

def get_box_count_verified():
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices WHERE verified = ?
        """, [1])
        return len(cursor.fetchall())

def handle_info_update(data):
    valid_keys = []
    if "id" not in data:
        return -1

    for key in data.keys():
        if key in valid_device_keys:
            valid_keys.append(key)
    
    sql = "UPDATE devices SET "
    for key in valid_keys:
        sql = sql + key + "=\"" + str(data[key]) + "\", "
    
    sql = sql + "lastseen = " +  int(data["lastseen"])

    sql = sql + " WHERE id=" + str(data["id"])
    with lock:
        try:
            cursor.execute(sql)
            connection.commit()
        except Exception as e:
            print(e)