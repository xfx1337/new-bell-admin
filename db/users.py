import sqlite3
from db.connection import connection
from datetime import datetime
import user
import db.tokens as tokens

cursor = connection.cursor()

def register(user: user):
    cursor.execute(f"""
    SELECT username FROM users WHERE username = ?
    """, [user.username])
    content = cursor.fetchone()

    if content != None:
        return "User is already exists"
        
    cursor.execute(f"""
    INSERT INTO users (username, password, privileges) VALUES (?, ?, ?)
    """, [user.username, user.password, user.privileges])
    connection.commit()

    cursor.execute(f"""
    INSERT INTO devices (username, password, lastseen) VALUES(?, ?, ?)
    """, [user.username, user.password, datetime.strftime(datetime.now(), '%d.%M.%Y %H:%M')])
    connection.commit()

    return 0

def login(data):
    if "username" not in data:
        return "Invalid request", 0
    if "password" not in data:
        return "Invalid request", 0
    
    cursor.execute(f"""
    SELECT * FROM users WHERE username = ?
    """, [data["username"]])

    content = cursor.fetchone()
    connection.commit()
    
    if content == None:
        return "No user with username", 0

    if content[2] != data["password"]:
        return "Wrong password", 0
    
    return 0, tokens.get_token(data["username"])