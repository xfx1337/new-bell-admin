from singleton import singleton
from streaming.stream import Stream
import time

import threading

@singleton
class ExecStream(Stream):
    def __init__(self, get_box_count_verified):
        super().__init__()
        self.get_box_count_verified = get_box_count_verified
        self.box_count = get_box_count_verified()

    def add(self, data):
        self.id += 1
        if "ids" in data:
            should_listen = data["ids"]
            del data["ids"]
            self.queue[self.id] = {"data": data, "ids": should_listen}
        else:
            self.queue[self.id] = {"data": data, "viewed": []}
        return self.exit

    def read(self, unique, ids=[]):
        self.box_count = self.get_box_count_verified()
        with self.lock:
            for i in range(len(ids)): # only like this!
                if ids[i] in self.queue.keys():
                    if "ids" in self.queue[ids[i]]:
                        if unique in self.queue[ids[i]]["ids"]:
                            try: 
                                self.queue[ids[i]]["ids"].remove(unique)
                            except: pass
                            if len(self.queue[ids[i]]["ids"]) == 0:
                                try:
                                    del self.queue[ids[i]]
                                except:
                                    pass
                    else:
                        if unique not in self.queue[ids[i]]["viewed"]:
                            self.queue[ids[i]]["viewed"].append(unique)
                        if len(self.queue[ids[i]]["viewed"]) >= self.box_count:
                            try: del self.queue[ids[i]]
                            except: pass
            return self.exit
    
    def _killer(self):
        while self.close != True:
            time.sleep(20)
            self.box_count = self.get_box_count_verified()
            with self.lock:
                if len(self.queue.keys()) != 0:
                    if self.id in self.queue.keys():
                        if "viewed" in self.queue[self.id]:
                            if self.box_count != len(self.queue[self.id]["viewed"]):
                                for viewer in self.queue[self.id]["viewed"]:
                                    if viewer not in self.listeners.keys():
                                        self.disconnect(viewer)
                                for i in range(self.id-1):
                                    if i in self.queue.keys():
                                        if "viewed" in self.queue[i]:
                                            try: del self.queue[i]
                                            except: pass
                        else:
                            pass