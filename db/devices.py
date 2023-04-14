import sqlite3
from db.connection import connection

import user
from datetime import datetime
import db.tokens as tokens

cursor = connection.cursor()

def refresh(data):
    username = tokens.get_username(data['token'])
    data = data['user']

    cursor.execute(f"""
    UPDATE devices 
    SET lastseen=?,
    region=?
    WHERE name=?""", [datetime.strftime(datetime.now(), '%d.%M.%Y %H:%M'), data['region'], username])

    connection.commit()