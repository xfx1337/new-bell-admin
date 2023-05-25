import sqlite3
from datetime import datetime
import json
import threading 

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

lock = threading.Lock()

def add(evt):
    with lock:
        cursor.execute(f"""
        INSERT INTO admin_events (payload, users_read) VALUES (?, ?)
        """, [evt.toJSON(), ""]) # no users read already
        id = cursor.lastrowid
        connection.commit()
        return id

def read(id, username):
    with lock:
        cursor.execute(f"""
        SELECT * FROM admin_events WHERE id = ?
        """, [id])
        content = cursor.fetchone()
        if content == None:
            return -1
        
        users_read = content[-1].split()
        if username in users_read:
            return 0
        users_read.append(username)
        users_read = str(users_read).replace(", ", "").replace("[", "").replace("]", "")
        cursor.execute(f"""
        UPDATE admin_events SET users_read = ? WHERE id = ?
        """, [users_read, id])
        connection.commit()
    return close(id)
    
def close(id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM admin_events WHERE id = ?
        """, [id])
        content = cursor.fetchone()
        if content == None:
            return -1
        
        users_read = content[-1].split()

        cursor.execute(f"""
        SELECT * FROM users WHERE privileges in ("admin", "owner")
        """)
        if len(users_read) != len(cursor.fetchall()):
            return 0
        
        cursor.execute(f"""
            DELETE FROM admin_events WHERE id = ?
        """, [id])
        connection.commit()
        return 0
        #del self

def get_events():
    with lock:
        cursor.execute(f"""
        SELECT * FROM admin_events
        """)
        
        content = cursor.fetchall()
        return content

def get_events_json(username=""):
    events = get_events()
    
    data = {"events": []}

    for e in events:
        if username != "":
            if username in e[-1]:
                continue
        data["events"].append(json.loads(e[1]))
    
    return json.dumps(data, indent=4), 200