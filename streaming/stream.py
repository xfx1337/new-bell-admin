from singleton import singleton

@singleton
class Stream:
    def __init__(self):
        self.queue = []
        self.id = 0
        self.exit = False
        self.suspend = False
        
    def add(self, data):
        if self.suspend == True:
            return 2
        
        self.id += 1
        self.queue.append([self.id, data])
        return self.exit
    
    def add_multiple(self, data):
        if self.suspend == True:
            return 2
        
        for d in data:
            self.queue.append([self.id, d])
            self.id += 1
        return self.exit

    def read(self, num=1):
        if self.suspend == True:
            return 2
        
        for i in range(num): # only like this!
            del self.queue[0]
        return self.exit
    
    def close(self):
        self.close = True
    
    def reinit(self):
        self.query = []
        self.id = 0
        self.suspend = False
    
    def stop(self):
        self.suspend = True
    
    def get_stream(self):
        return self
