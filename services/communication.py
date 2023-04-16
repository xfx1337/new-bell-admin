import json
import db.devices
import db.tokens
from datetime import datetime, timedelta
import time

def refresh(req):
    validation_results = db.tokens.valid(req.get_json())
    if validation_results != 0:
        return validation_results, 400
    
    db.devices.refresh(req.get_json())
    return 'Ok', 300

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