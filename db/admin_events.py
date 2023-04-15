import sqlite3
from db.connection import connection
from datetime import datetime
import json

cursor = connection.cursor()

def add(evt):
    cursor.execute(f"""
    INSERT INTO admin_events (payload) VALUES (?)
    """, [evt.toJSON()])
    id = cursor.lastrowid
    connection.commit()
    return id

def close(id):
    cursor.execute(f"""
        DELETE FROM admin_events WHERE id = ?
    """, id)
    connection.commit()

    #del self

def get_events():
    cursor.execute(f"""
    SELECT * FROM admin_events
    """)
    
    content = cursor.fetchall()
    return content

def get_events_json():
    events = get_events()
    
    data = {"events": []}

    for e in events:
        data["events"].append(json.loads(e[1]))
    
    return json.dumps(data, indent=4), 200