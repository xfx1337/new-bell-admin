from user import User
import db.tokens
import db.users
import db.devices
import db.admin_events

from streaming.stat_stream import StatStream

import json
from datetime import datetime, timedelta

def get_unverified_devices(req):
    return json.dumps(list(filter(lambda dev: dev[1] == 0, db.devices.all()) )), 200

def get_devices(req):
    return json.dumps(db.devices.all()), 200

def statistics_stream(req, token, breaktime):
    # eliminating best practices...
    
    info = db.devices.get_full_info()
    ret = {"devices": []}
    for device in info:
        ret["devices"].append({"id": device[0], "verified": device[1], "name": device[2], "host": device[3], "lastseen": device[5], "lastlogs": device[6], "lastupdate": device[7], "region": device[8]})
    yield json.dumps(ret, indent=4)

    username = db.tokens.get_username(token)

    stream = StatStream()
    stream.connect(username)

    yield "\n[StreamStart]"
    
    readids = [] # already read ids

    while stream.exit != True:
        if len(stream.queue.keys()) == 0:
           continue
        readed = stream.queue.copy()
        ret, ids = handle_stream_data(readed, readids)
        if ret != 0:
            stream.read(username, ids)
            yield ret

    yield "\n[StreamEnd]"
    stream.disconnect(username)

def handle_stream_data(queue, readids):
    data = {"data": []}
    ids = []
    for i in queue.keys():
        if i in readids:
            continue
        data["data"].append({"id": i, "content": queue[i]["data"]})
        ids.append(i)
        readids.append(i)
    if len(data["data"]) == 0:
        return 0, 0
    return f"\n[ResponseStart]" + json.dumps(data, indent=4) + "[ResponseEnd]", ids

def read_events(req):
    data = req.get_json()
    username = db.tokens.get_username(req.headers.get("Authorization"))
    if "ids" not in data:
        return "Bad request", 400
    ids = data["ids"]
    for id in ids:
        ret = db.admin_events.read(id, username)
        if ret != 0:
            return "Not found", 404
    return "Read", 200