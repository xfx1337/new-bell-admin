from user import User
from device import Device
import db.tokens
import db.users
import db.devices
import db.admin_events
from Events import *
import json


def register_user(request):
    if request.method == "POST":
        data = request.get_json()
        
        if "user" not in data:
            return "Invalid request", 400
        
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
    else:
        return "Invalid request", 400

def login_user(request):
    data = request.get_json()
    ret, token = db.users.login(data)
    if ret == -1:
        return "Invalid user creditionals", 400
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
        return "Invalid device information", 400
    
    ret = db.devices.register(device)
    if ret != 0:
        return "Internal server error", 500
    

    ret = db.tokens.register(device.id)
    ret = {"token": ret}
    return json.dumps(ret, indent=4), 200
