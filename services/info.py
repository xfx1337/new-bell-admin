from user import User
import db.tokens
import db.users
import db.devices

from streaming.stream import Stream
from streaming.stream_connection import stream

import json
from datetime import datetime, timedelta

def get_unverified_devices(req):
    return json.dumps(list(filter(lambda dev: dev[1] == 0, db.devices.all()) )), 200

def get_devices(req):
    return json.dumps(db.devices.all()), 200

def statistics_stream(req, breaktime):
    # eliminating best practices...
    
    info = db.devices.get_full_info()
    ret = {"devices": []}
    for device in info:
        ret["devices"].append({"id": device[0], "verified": device[1], "name": device[2], "host": device[3], "lastseen": device[5], "lastlogs": device[6], "lastupdate": device[7], "region": device[8]})
        yield json.dumps(ret, indent=4)

    stream = Stream()
    stream.connect()

    yield "\n[StreamStart]"
    
    readids = [] # already read ids

    while stream.exit != True:
        if len(stream.queue.keys()) == 0:
           continue
        readed = stream.queue.copy()
        ret, ids = handle_stream_data(readed, readids)
        if ret != 0:
            stream.read(ids)
            yield ret

    yield "\n[StreamEnd]"
    stream.disconnect()

def handle_stream_data(queue, readids):
    data = {"data": []}
    ids = []
    for i in queue.keys():
        if i in readids:
            continue
        data["data"].append({"id": i, "content": queue[i]})
        ids.append(i)
        readids.append(i)
    if len(data["data"]) == 0:
        return 0, 0
    return f"\n[ResponseStart]" + json.dumps(data, indent=4) + "[ReponseEnd]", ids