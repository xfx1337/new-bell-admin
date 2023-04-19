import threading
import time
import db.devices

class Stream:
    def __init__(self):
        self.queue = {}
        self.id = 0
        self.exit = False
        self.listeners_killer = threading.Thread(target=self._killer)
        self.listeners_killer.start()
        self.listeners = {}
        self.lock = threading.Lock()

    def add(self, data):
        self.id += 1
        self.queue[self.id] = {"viewed": [], "data": data}
        return self.exit
    
    def add_multiple(self, data):
        for d in data:
            self.queue[self.id] = {"viewed": [], "data": d}
            self.id += 1
        return self.exit

    def read(self, unique, ids=[]): # unique = token or username or id
        with self.lock:
            for i in range(len(ids)): # only like this!
                if ids[i] in self.queue.keys():
                    if unique not in self.queue[ids[i]]["viewed"]:
                        self.queue[ids[i]]["viewed"].append(unique)
                    if len(self.queue[ids[i]]["viewed"]) >= len(self.listeners.keys()):
                        try: del self.queue[ids[i]]
                        except: pass
            return self.exit
    
    def close(self):
        self.exit = True
    
    def get_stream(self):
        return self
    
    def connect(self, unique):
        self.listeners[unique] = 1

    def disconnect(self, unique):
        try:
            self.listeners.pop(unique)
        except:
            pass
    
    def _killer(self):
        while self.close != True:
            time.sleep(20)
            with self.lock:
                if len(self.queue.keys()) != 0:
                    if self.id in self.queue.keys():
                        if len(self.listeners.keys()) != len(self.queue[self.id]["viewed"]):
                            for viewer in self.queue[self.id]["viewed"]:
                                if viewer not in self.listeners.keys():
                                    self.disconnect(viewer)
                            for i in range(self.id-1):
                                if self.id in self.queue.keys():
                                    del self.queue[self.id]
            