import sqlite3
from db.connection import connection

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
    SELECT * FROM tokens WHERE token = ?
    """, [req["token"]])    
    
    content = cursor.fetchone()
    if content == None:
        return "Token not exists"

    if datetime.now().timestamp() > content[3]:
        return "Token expired"

    return 0

def get_token(username):
    cursor.execute(f"""
    SELECT * FROM tokens WHERE username = ?
    """, [username])
    content = cursor.fetchone()

    if content == None:
        return register(username)


    if datetime.now().timestamp() > content[3]:
        cursor.execute(f""""
        DELETE * FROM tokens WHERE token = ?
        """, [content[2]])
        connection.commit()
        return register(username)

    renew_token(username)
    return content[2]

def get_username(token):
    cursor.execute(f"""
    SELECT username FROM tokens
    WHERE TOKEN=?
    """, [token])
    connection.commit()

    return cursor.fetchone()[0]

def renew_token(username):
    cursor.execute(f"""
    SELECT token FROM tokens WHERE username = ?
    """, [username])
    content = cursor.fetchone()

    if content == None:
        return register(username)
    
    expiration = datetime.now() + timedelta(hours=12)

    cursor.execute(f"""
    UPDATE tokens SET expiration = ? WHERE username = ?
    """, [int(round(expiration.timestamp())), username])
    connection.commit()
    
    return 0