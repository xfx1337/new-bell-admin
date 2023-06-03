from user import User
import db.tokens
import db.users
import db.devices
import db.admin_events
import db.connection

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