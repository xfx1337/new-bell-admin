import json
import db.devices
import db.tokens
from datetime import datetime, timedelta
import time

from streaming.exec_stream import ExecStream
from streaming.stat_stream import StatStream

def response(req, token):
    
    username = int(db.tokens.get_username(token))

    data = req.get_json()

    if "data" not in data:
        return "Invalid request", 400

    ids = []
    responses = []

    for res in data["data"]:
        ids.append(int(res["id"]))
        responses.append(res)

    stream = ExecStream(db.devices.get_box_count_verified)
    stream.read(username, ids)

    stat_stream = StatStream()
    stat_stream.add(responses)

    return "Readed", 200

def refresh(req, token):
    time_start = datetime.now()
    exit = False

    data = req.get_json()
    username = int(db.tokens.get_username(token))
    data["id"] = username
    stat_stream = StatStream()
    stat_stream.add(data)
    db.devices.handle_info_update(data)


    stream = ExecStream(db.devices.get_box_count_verified)
    stream.connect(username)
    readids = [] # already read ids


    while datetime.now() < time_start + timedelta(minutes=1) and exit == False and stream.exit != True:
        time.sleep(5)

        if len(stream.queue.keys()) == 0:
            continue
        readed = stream.queue.copy()
        ret, ids = handle_stream_data(readed, readids, username)
        if ret != 0:
            #stream.read(username, ids)
            stream.disconnect(username)
            return ret, 200

    return 'Reconnect please', 200

def handle_stream_data(queue, readids, username):
    data = {"data": []}
    ids = []
    for i in queue.keys():
        if i in readids:
            continue
        if "ids" in queue[i]:
            if username not in queue[i]["ids"]:
                continue
        else:
            if username in queue[i]["viewed"]:
                continue
                
        data["data"].append({"id": i, "content": queue[i]["data"]})
        ids.append(i)
        readids.append(i)
    if len(data["data"]) == 0:
        return 0, 0
    return json.dumps(data, indent=4), ids

def request(req):
    return db.devices.request(req)

def device_wait_for_registration(req):
    time_start = datetime.now()
    exit = False

    data = req.get_json()

    if "id" not in data:
        return "Invalid request", 400

    db_id = data["id"]

    while datetime.now() < time_start + timedelta(minutes=2) and exit == False:
        time.sleep(5)

        ret, data = db.devices.get_info_json(db_id)
        if ret != 0:
            return data, 400
        if data["verified"] == 1:
            exit = True
            return json.dumps(data, indent=4), 200
    
    return "Not verified", 403