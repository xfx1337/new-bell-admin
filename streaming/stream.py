import threading
import time
import db.devices
import uuid

class Stream:
    def __init__(self):
        self.queue = {}
        self.id = 0
        self.exit = False
        self.lock = threading.Lock()
        self._enable_callback = False
        self._callback = None

    def add(self, data):
        with self.lock:
            self.id = uuid.uuid4().hex.upper()
            self.queue[self.id] = data

        if self._enable_callback:
            self._callback(data, self.id)

        return self.exit
    
    def read(self, id):
        with self.lock:
            try: del self.queue[id]
            except: pass

    def close(self):
        self.exit = True

    def set_callback(self, callback):
        self._callback = callback
        self._enable_callback = True