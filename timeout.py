import time
class TimeoutError(Exception):
    pass

class Timer(object):
    def __init__(self, name='', maxTime=0.0):
        self.time = 0.0
        self.timeout = False
        self.name = name
        self.maxTime = maxTime
        self.active = False
    def time(self):
        return self.time
    def time(self, time):
        self.time = time
    def timeout(self):
        return self.timeout
    def name(self):
        return self.name
    def name(self, name):
        self.name = name
    def maxTime(self):
        return self.maxTime
    def maxTime(self, maxTime):
        self.maxTime = maxTime
    def start(self):
        self.time = time.time()
        self.active = True
    def start(self, maxTime):
        self.time = time.time()
        self.maxTime = maxTime
        self.active = False
    def hasTimedOut(self):
        self.timeout = (time.time() - self.time) >= self.maxTime
        return self.timeout and self.active
    def reset(self):
        self.time = 0.0
        self.active = False
