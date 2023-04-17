from singleton import singleton
import threading
import time

@singleton
class Stream:
    def __init__(self):
        self.queue = {}
        self.id = 0
        self.exit = False
        self.listeners_killer = threading.Thread(target=self._killer)
        self.listeners_killer.start()
        self.listeners = 0
        
    def add(self, data):
        self.id += 1
        self.queue[self.id] = {"viewed": 0, "data": data}
        return self.exit
    
    def add_multiple(self, data):
        
        for d in data:
            self.queue[self.id] = {"viewed": 0, "data": d}
            self.id += 1
        return self.exit

    def read(self, ids=[]):
        for i in range(len(ids)): # only like this!
            if ids[i] in self.queue.keys():
                self.queue[ids[i]]["viewed"] = self.queue[ids[i]]["viewed"] + 1
                if self.queue[ids[i]]["viewed"] == self.listeners:
                    time.sleep(1)
                    del self.queue[ids[i]]
        return self.exit
    
    def close(self):
        self.exit = True
    
    def get_stream(self):
        return self
    
    def connect(self):
        self.listeners += 1

    def disconnect(self):
        self.listeners -= 1
    
    def _killer(self):
        while self.close != True:
            time.sleep(20)
            if len(self.queue.keys()) != 0:
                if self.listeners != self.queue[self.id]:
                    self.listeners -= 1
                    for i in range(self.id-1):
                        if self.id in self.queue.keys():
                            del self.queue[self.id]
            