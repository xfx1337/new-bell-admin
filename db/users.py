import sqlite3
import threading

from datetime import datetime
import user
import db.tokens

lock = threading.Lock()

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

def register(user: user):
    with lock:
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
        return 0

def login(data):
    content = None
    with lock:
        cursor.execute(f"""
        SELECT * FROM users WHERE username = ?
        """, [data["username"]])

        content = cursor.fetchone()
        connection.commit()
        
    if content == None:
        return -1, "No user with username", 
        
    if content[2] != data["password"]:
        return -1, "Wrong password"
    return 0, db.tokens.get_token(data["username"])

def delete_user(username):
    with lock:
        cursor.execute(f"""
        SELECT * FROM users WHERE username = ?
        """, [username])

        content = cursor.fetchone()
        
        if content == None:
            return "No such user", 0
        cursor.execute(f"""
        DELETE FROM users WHERE username = ?
        """, [username])
        connection.commit()

    ret, message = db.tokens.remove_token(username)
    return 0, 200



def get_privileges(username):
    with lock:
        cursor.execute(f"""
        SELECT * FROM users where username = ?
        """, [username])

        content = cursor.fetchone()

        if content == None:
            return "No user with username", 0
        
        return content[3]