import sqlite3
from db_connection import connection

import user_class

cursor = connection.cursor()

def register(user: user_class):
    cursor.execute(f"""
    SELECT username FROM users WHERE username = ?
    """, [user.username])
    data = cursor.fetchall()

    if len(data) != 0:
        return -1, "User is already exists"
        
    cursor.execute(f"""
    INSERT INTO users (username, pass_md5, privileges) VALUES (?, ?, ?)
    """, [user.username, user.pass_md5, user.privileges])
    connection.commit()

    return 0

def login(data):
    if "username" not in data:
        return -1
    if "password" not in data:
        return -1
    