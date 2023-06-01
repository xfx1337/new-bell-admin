from user import User
import db.tokens
import db.users
import db.devices
import db.admin_events

from streaming.stat_stream import StatStream

import json
from datetime import datetime, timedelta

def get_unverified_devices():
    return json.dumps(list(filter(lambda dev: dev[1] == 0, db.devices.all()) )), 200

def get_devices():
    return json.dumps(db.devices.all()), 200

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