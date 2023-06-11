import json
import db.devices
import db.tokens
import db.processes

from datetime import datetime, timedelta
import time

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
            return ret, 404
        if data["verified"] == 1:
            exit = True
            return json.dumps(data, indent=4), 200
    
    return "Not verified", 403

def sync_processes(req):
    device_id = db.tokens.get_username(req.headers.get("Authorization").split()[1])
    processes = db.processes.sync_processes(device_id)
    to_send = []
    for p in processes:
        to_send.append({"execution_id": p[1], "cmd": p[3], "failsafe_mode": p[5], "failsafe_timeout": p[6], "wait_mode": p[7]})
    return {"processes": to_send}, 200