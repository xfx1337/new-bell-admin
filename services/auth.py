from user import User
from device import Device
import db.tokens
import db.users
import db.devices
import db.admin_events
from Events import *
import json


def register_user(request):
    data = request.get_json()
    
    if "user" not in data:
        return "Invalid request", 400

    if db.users.get_privileges(db.tokens.get_username(request.headers.get('Authorization'))[1]) != 'owner':
        return "Permission denied", 403

    user = User()
    ret = user.init_by_json(data["user"])
    if ret != 0:
        return "Invalid user creditionals", 400
    
    ret = db.users.register(user)
    if ret != 0:
        return "User is already exists", 400
    ret = db.tokens.register(user.username)
    ret = {"token": ret}
    return json.dumps(ret, indent=4), 200

def delete_user(request):
    data = request.get_json()

    if "username" not in data:
        return "No username provided"
    

    ret, priv = db.users.get_privileges(db.tokens.get_username(request.headers.get('Authorization'))[1])
    if ret != 0:
        return "Wrong request", 400
    if priv != "owner":
        return "Permission denied", 403

    ret, message = db.users.delete_user(data["username"])
    if ret != 0:
        return ret, 400
    else:
        return "User deleted", 200



def login_user(request):
    data = request.get_json()
    if "username" not in data and "device_id" not in data:
        return 0, "Invalid request"
    if "password" not in data:
        return 0, "Invalid request"
    if "username" in data:
        ret, token = db.users.login(data)
    else:
        ret, token = db.devices.login(data)

    if ret != 0:
        return token, 400
    ret = {"token": token}
    return json.dumps(ret, indent=4), 200

def register_device(request):
    data = request.get_json()
    if "password" not in data:
        return "Password not provided", 400

    db_id = db.devices.add_unverified(request.remote_addr, data["password"])

    db.admin_events.add(DeviceRegisterEvent(request.remote_addr, db_id))

    ret = {"id": db_id}
    return json.dumps(ret, indent=4), 200

def approve_device(request):
    data = request.get_json()

    if "device" not in data:
        return "Invalid request", 400

    device = Device()
    ret = device.init_by_json(data["device"])
    if ret != 0:
        return ret, 400
    
    ret = db.devices.register(device)
    if ret != 0:
        return "Internal server error", 500
    

    ret = db.tokens.get_token(device.id)
    ret = db.devices.verify(device.id)
    return "Device added", 200