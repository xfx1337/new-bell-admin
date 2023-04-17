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
    stream.reinit()
    yield "\n[StreamStart]"

    while stream.exit != True:
        if len(stream.queue) == 0:
           continue
        readed = len(stream.queue)
        yield handle_stream_data(stream.queue.copy(), readed)
        stream.read(readed)

    stream.stop()
    yield "\n[StreamEnd]"

def handle_stream_data(queue, readed):
    data = {"data": []}
    for i in range(readed):
        data["data"].append({"id": queue[i][0], "query": queue[i][1]})
    return f"\n[ResponseStart]" + json.dumps(data, indent=4) + "[ReponseEnd]"