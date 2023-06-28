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
        INSERT INTO admin_events (payload) VALUES (?)
        """, [evt.toJSON()]) # no users read already
        id = cursor.lastrowid
        connection.commit()
        return id

def close(id):
    with lock:
        if id == "all":
            cursor.execute(f"""
            DELETE FROM admin_events
            """)
            connection.commit()
            return 0

        cursor.execute(f"""
        SELECT * FROM admin_events WHERE id = ?
        """, [id])
        content = cursor.fetchone()
        if content == None:
            return -1
        
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
        data["events"].append(json.loads(e[1]))
        data["events"][-1]["event_id"] = e[0]
    
    return json.dumps(data, indent=4), 200