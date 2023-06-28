from datetime import datetime
import json

class Event:
    def __init__(self, time=datetime.now()):
        self.time = int(round(time.timestamp()))
        self.type = "Event"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class DeviceRegisterEvent(Event):
    def __init__(self, host, id, time=datetime.now()):
        super().__init__(time)
        self.type = "DeviceRegisterEvent"
        self.host = host
        self.device_id = id

class AdminEvent(Event):
    def __init__(self, status, message, time=datetime.now()):
        super().__init__(time)
        self.type = "AdminEvent"
        self.status = status
        self.message = message