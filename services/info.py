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

def statistics_stream(req):
    # eliminating best practices...

    breaktime = datetime.now() + timedelta(minutes=5)

    # if req.method == 'POST':
    #     data = req.get_json()

    #     if "breaktime" not in data:
    #         breaktime = datetime.now() + timedelta(minutes=5)
    #     else:
    #         breaktime = datetime.now() + data["breaktime"]
    
    info = db.devices.get_full_info()
    ret = {"devices": []}
    for device in info:
        ret["devices"].append({"id": device[0], "verified": device[1], "name": device[2], "host": device[3], "lastseen": device[5], "lastlogs": device[6], "lastupdate": device[7], "region": device[8]})
    #yield json.dumps(ret, indent=4)

    print('fuckup')

    stream = Stream()
    stream.reinit()
    i = 0
    while stream.exit != True:
        #if len(stream.queue) == 0:
        #    continue
        yield str(i)
        i += 1
        #readed = len(stream.queue)
        #yield handle_stream_data(stream.queue.copy(), readed)
        #stream.read(readed)

    stream.stop()
    yield "[StreamEnd]"

def handle_stream_data(queue, readed):
    data = {"data": []}
    for i in range(readed):
        data["data"].append({"id": queue[i][0], "query": queue[i][1]})
    return f"[ResponseStart]" + json.dumps(data, indent=4) + "[ReponseEnd]"