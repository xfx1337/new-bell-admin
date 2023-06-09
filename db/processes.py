import sqlite3
import threading

from datetime import datetime
import db.tokens

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

lock = threading.Lock()

def register(execution_id, ids, cmd, failsafe_mode, failsafe_timeout, wait_mode):
    with lock:
        cursor.execute(f"""
        INSERT INTO devices_processes (execution_id, ids, cmd, time, failsafe_mode, failsafe_timeout, wait_mode, status) VALUES (?,?,?,?,?,?,?,?)
        """, [execution_id, 
              str(ids).replace(", ", "").replace("[", "").replace("]", ""), 
              cmd, 
              int(datetime.now().timestamp()), 
              failsafe_mode, 
              str(failsafe_timeout),
              wait_mode, 
              "IN_PROGRESS"])
        connection.commit()
    return 0

def get_all():
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes
                       """)
        return cursor.fetchall()

def get_info(execution_id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes WHERE execution_id = ?
                       """, [execution_id])
        return cursor.fetchone()

def close(execution_id):
    with lock:
        cursor.execute(f"""
        DELETE FROM devices_processes WHERE execution_id = ?
                       """, [execution_id])
        connection.commit()
    with lock:
        cursor.execute(f"""
        DELETE FROM devices_processes_responses WHERE execution_id = ?
                       """, [execution_id])
        connection.commit()
    return 0

def interrupt(execution_id):
    with lock:
        cursor.execute(f"""
        UPDATE devices_processes SET status = ? WHERE execution_id = ?
                       """, ["DONE", execution_id])
        connection.commit()
    return 0

def response(execution_id, device_id, response, errors, response_time):
    with lock:
        cursor.execute(f"""
        INSERT INTO devices_processes_responses (execution_id, device_id, response, errors, response_time) VALUES (?,?,?,?,?)
                       """, [execution_id, device_id, response, errors, response_time])
        connection.commit()

    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes WHERE execution_id = ?
                        """, [execution_id])
        content = cursor.fetchone()

    if len(get_info(execution_id)[2].split()) >= len(content[2].split()): # if all responses got
            with lock:
                cursor.execute(f"""
                UPDATE devices_processes SET status = ? WHERE execution_id = ?
                            """, ["DONE", execution_id])
                connection.commit()
    return 0
    
def get_responses(execution_id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes_responses WHERE execution_id = ?
                       """, [execution_id])
        return cursor.fetchall()