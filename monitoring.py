from singleton import singleton

from streaming.singletone_streams import DeviceRefreshingStream, DeviceRequestStream, DeviceResponseStream

import db.tokens
import db.devices
import db.processes

from flask import Flask, current_app
from flask_socketio import emit

from datetime import datetime

@singleton
class Monitoring: # skin for StatStream
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.packets_sent = 0

        self.ref_stream = DeviceRefreshingStream()
        self.req_stream = DeviceRequestStream()
        self.res_stream = DeviceResponseStream()

        self.ref_stream.set_callback(self._ref_callback)
        self.req_stream.set_callback(self._req_callback)
        self.res_stream.set_callback(self._res_callback)
        
    def _ref_callback(self, data, id):
        data["lastseen"] = int(datetime.timestamp(datetime.now()))
        data["id"] = int(db.tokens.get_username(data["token"]))
        with self.app.app_context():
            self.socketio.emit('update', data, namespace="/mainIO")
            #self.socketio.emit('response', {'data': 'got'}, namespace="/refreshing")
        self.packets_sent += 1
        db.devices.handle_info_update(data)
        self.ref_stream.read(id)

    def _req_callback(self, data, id):
        with self.app.app_context():
            if data["type"] == "execute":
                self.socketio.emit('request', data, namespace="/refreshing")
            ret, text = self.req_stream.check(id) # if it is process - use processes db
            if ret != 0:
                self.socketio.emit('request_error', {"data": text}, namespace="/mainIO")
            else:

                if text == "DB_REQUEST_INTERRUPT_RESPONSE_ADMIN":
                    if data["execution_id"] == "all":
                        ids = "all"
                    else:
                        ids = db.processes.get_info(data["execution_id"])[2]
                        ids = list(map(int, ids.split()))
                    self.socketio.emit("request", {"type": "interrupt", 
                                                   "execution_id": data["execution_id"], 
                                                   "ids": ids}, 
                                                   namespace="/refreshing")
                    
                    self.socketio.emit("device_response_status", 
                                       {"data": "Process interruption started. You can close process after it will be completely terminated.", 
                                        "execution_id": data["execution_id"]}, 
                                        namespace="/mainIO")
                    
                elif text == "DB_REQUEST_INTERRUPT":
                    ids = db.processes.get_info(data["execution_id"])[2]
                    if ids != "all":
                        ids = list(map(int, ids.split()))
                    self.socketio.emit("request", {"type": "interrupt", 
                                                   "execution_id": data["execution_id"], 
                                                   "ids": ids}, 
                                                   namespace="/refreshing")
                
                elif text == "RESPONSE_ADMIN":
                    self.socketio.emit("device_response_status", {"data": "Closed", "execution_id": data["execution_id"]}, namespace="/mainIO")
        
        self.req_stream.read(id)

    def _res_callback(self, data, id):
        data["id"] = int(db.tokens.get_username(data["token"]))
        data["time"] = int(datetime.timestamp(datetime.now()))
        with self.app.app_context():
            self.socketio.emit('response', {'content': data}, namespace="/mainIO")
        ret, text = self.res_stream.check(id)
        if ret != 0:
            self.socketio.emit('device_response_error', {"data": text}, namespace="/mainIO")
        self.res_stream.read(id)