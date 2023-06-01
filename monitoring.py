from singleton import singleton

from streaming.stat_stream import StatStream
import db.tokens

from flask import Flask, current_app
from flask_socketio import emit

@singleton
class Monitoring: # skin for StatStream
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.packets_sent = 0
        self.stat_stream = StatStream()
        self.stat_stream.set_monitoring_callback(self._callback)

    def connect_user(self, token):
        username = db.tokens.get_username(token)
        self.stat_stream.connect(username)

    def disconnect(self, token):
        username = db.tokens.get_username(token)
        self.stat_stream.disconnect(username)
    
    def _callback(self, data, id):
        with self.app.app_context():
            self.socketio.emit('update', data)
        self.packets_sent += 1
        self.stat_stream.force_read(id)