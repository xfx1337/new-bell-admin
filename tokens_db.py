import sqlite3
from db_connection import connection

from uuid import uuid4
from datetime import datetime, timedelta

cursor = connection.cursor()

def register(username):
    rand_token = str(uuid4())
    expiration = datetime.now() + timedelta(hours=12)

    cursor.execute(f"""
    INSERT INTO tokens (username, token, expiration) VALUES (?, ?, ?)
    """, [username, rand_token, int(round(expiration.timestamp()))])
    connection.commit()

    return rand_token

def validate_token(req):
    if "token" not in req:
        return -1
    
    cursor.execute(f"""
    SELECT username FROM tokens WHERE token = ?
    """, [req["token"]])    
    
    data = cursor.fetchone()
    if data == None:
        return -1

    return 0