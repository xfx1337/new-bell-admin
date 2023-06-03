from singleton import singleton

from streaming.singletone_streams import DeviceRefreshingStream, DeviceRequestStream, DeviceResponseStream

import db.tokens
import db.devices

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
        with self.app.app_context():
            self.socketio.emit('update', data, namespace="/monitoring")
            self.socketio.emit('response', {'data': 'got'}, namespace="/refreshing")
        self.packets_sent += 1
        db.devices.handle_info_update(data)
        self.ref_stream.read(id)

    def _req_callback(self, data, id):
        with self.app.app_context():
            self.socketio.emit('request', data, namespace="/refreshing")
        self.packets_sent += 1
        self.req_stream.read(id)
    
    def _res_callback(self, data, id):
        with self.app.app_context():
            self.socketio.emit('response', {'id': id, 'content': data}, namespace="/monitoring")
        self.res_stream.read(id)