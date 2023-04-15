from user import User
import db.tokens
import db.users
import db.devices
import json

def unverified_devices(req):
    return json.dumps(list(filter(lambda dev: dev[1] == 0, db.devices.all()) )), 200

def devices(req):
    return json.dumps(db.devices.all()), 200