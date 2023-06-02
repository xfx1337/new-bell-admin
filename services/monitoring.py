from singleton import singleton

from streaming.stat_stream import StatStream
import db.tokens

from flask_socketio import Namespace

@singleton
class Monitoring: # skin for StatStream
    def __init__(self, sockets_callback):
        self.stat_stream = StatStream()
        self.stat_stream.set_monitoring_callback(self._callback)
        self.sockets_callback = sockets_callback

    def connect_user(self, token):
        username = db.tokens.get_username(token)
        self.stat_stream.connect(username)

    def disconnect(self, token):
        username = db.tokens.get_username(token)
        self.stat_stream.disconnect(username)
    
    def _callback(self, data):
        self.sockets_callback(data)