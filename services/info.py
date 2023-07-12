from user import User
import db.tokens
import db.users
import db.devices
import db.admin_events
import db.processes
import db.connection

import Events

import json
from datetime import datetime, timedelta

def get_unverified_devices():
    return json.dumps(list(filter(lambda dev: dev[1] == 0, db.devices.all()) )), 200

def get_devices():
    data = db.devices.all()
    for i in range(len(data)):
        data[i] = data[i][0:4] + data[i][5:] # password deletion

    return json.dumps(data), 200

def get_user_info(req):
    data = req.get_json()
    if "username" not in data:
        return "Bad request", 400
    
    return {"privileges": db.users.get_privileges(data["username"])[1]}, 200

def list_users(req):
    users = db.users.get_all()
    out = []
    for u in users:
        out.append({"username": u[1], "privileges": u[3]})
    return {"data": out}, 200


def get_device_info_json(req):
    data = req.get_json()
    if "id" not in data:
        return "Bad request", 400
    return db.devices.get_info_json(data["id"], True)[1], 200

def get_sql(req):
    data = req.get_json()
    if "query" not in data:
        return "Bad request", 400
    
    out = None
    try:
        out = db.connection.sql_get(data["query"])
    except:
        return "Couldn't execute sql", 500

    return {"data": out}, 200

def get_processes(req):
    data = db.processes.get_all()
    send = {"data": []}
    for p in data:
        send["data"].append({"execution_id": p[1], 
                     "ids": list(map(int, p[2].split())),
                     "cmd": p[3],
                     "time": p[4],
                     "failsafe_mode": bool(p[5]),
                     "failafe_timeout": float(p[6]),
                     "wait_mode": bool(p[7]),
                     "status": p[8]})
    return send, 200

def get_process_info(req):
    if "execution_id" not in req.get_json():
        return "Bad request", 400
    try:
        p = db.processes.get_info(req.get_json()["execution_id"])
        return {"data": {"execution_id": p[1], 
                     "ids": list(map(int, p[2].split())),
                     "cmd": p[3],
                     "time": p[4],
                     "failsafe_mode": bool(p[5]),
                     "failsafe_timeout": float(p[6]),
                     "wait_mode": bool(p[7]),
                     "status": p[8]}}, 200
    except:
        return "Wrong execution_id", 400

def get_process_responses(req):
    if "execution_id" not in req.get_json():
        return "Bad request", 400
    try:
        responses = db.processes.get_responses(req.get_json()["execution_id"])
        data = {"data": []}
        for r in responses:
            data["data"].append({"content": {"id": r[2], "response": r[3], "errors": r[4], "time": r[5]}})
        return data, 200
    except:
        return "Wrong execution_id", 400

def read_events(req):
    data = req.get_json()
    if "ids" not in data:
        return "Bad request", 400
    for id in data["ids"]:
        db.admin_events.close(id)

    return "Read", 200

def create_event(req):
    data = req.get_json()
    try: 
        ret = db.admin_events.add(Events.AdminEvent(data["status"], data["message"]))
        return {"id": ret}, 200

    except: return "Someting went wrong", 500