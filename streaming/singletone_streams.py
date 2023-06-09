from streaming.stream import Stream
from singleton import singleton

import db.processes

@singleton
class DeviceRefreshingStream(Stream):
    pass

@singleton
class DeviceRequestStream(Stream):
    def check(self, id):
        request = self.queue[id]
        if request["type"] == "execute":
            try:
                db.processes.register(request["content"]["execution_id"], 
                                  request["ids"], request["content"]["cmd"], 
                                  request["content"]["failsafe_mode"], 
                                  request["content"]["failsafe_timeout"], 
                                  request["content"]["wait_mode"])
            except:
                return -1, "Failed to add to db"
        
        if request["type"] == "close_process":
            try:
                if request["execution_id"] == "all":
                    return 0, "DB_REQUEST_INTERRUPT_RESPONSE_ADMIN"
                
                info = db.processes.get_info(request["execution_id"])
                if info[-1] == "IN_PROGRESS":
                    return 0, "DB_REQUEST_INTERRUPT_RESPONSE_ADMIN"
                else: 
                    db.processes.close(request["execution_id"])
                    return 0, "RESPONSE_ADMIN"
            except:
                return -1, "Failed to close"

        if request["type"] == "interrupt":
            return 0, "DB_REQUEST_INTERRUPT"

        return 0, "Nothing to do with db"
            

@singleton
class DeviceResponseStream(Stream):
    def check(self, id):
        request = self.queue[id]
        if request["type"] == "device_response":
            try: db.processes.response(request["execution_id"], request["id"], request["response"], request["errors"], request["time"])
            except: return -1, "Failed to add to db"
        return 0, "DONE"