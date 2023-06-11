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
                return 1
    return 0
    
def get_responses(execution_id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes_responses WHERE execution_id = ?
                       """, [execution_id])
        return cursor.fetchall()
    
def close_done():
    with lock:
        cursor.execute(f"""
        SELECT execution_id FROM devices_processes WHERE status = ?
                       """, ["DONE"])
        content = cursor.fetchall()
    if len(content) != 0:
        with lock:
            cursor.execute(f"""
            DELETE FROM devices_processes WHERE status = ?
                        """, ["DONE"])
            connection.commit()
        
        delete_ids = []
        for id in content:
            delete_ids.append([id[0]])

        with lock:
            cursor.executemany(f"""DELETE FROM devices_processes_responses WHERE execution_id = ?""", delete_ids)
            connection.commit()

def sync_processes(device_id):
    with lock:
        cursor.execute(f"""
        SELECT * FROM devices_processes WHERE status = 'IN_PROGRESS' AND ids LIKE ?
                       """, ["%" + str(device_id) + "%"])
        processes = cursor.fetchall()
    
    select_ids = []
    for id in processes:
        select_ids.append(id[1])
    
    with lock:
        cursor.execute(f"""
        SELECT execution_id FROM devices_processes_responses WHERE device_id = {device_id} AND execution_id IN ({str(select_ids).replace("[", "").replace("]", "")})
                       """)
        content = cursor.fetchall()

    real_ids = []
    for id in content:
        real_ids.append(id[1])

    to_sync = []

    for p in processes:
        if p[1] not in real_ids:
            to_sync.append(p)
    
    return to_sync