class Message(object):
    def __init__(self):
        self.control = ""
        self.origin = ""
        self.destiny = ""
        self.size = 0
        self.data = ""
        self.parity = ""
        self.response = str(chr(0))
    def setControl(self, control):
        self.control = control
    def setOrigin(self, origin):
        self.origin = origin
    def setDestiny(self, destiny):
        self.destiny = destiny
    def setSize(self, size):
        self.size = size
    def setData(self, data):
        self.data = data
    def calcParity(self, data):
        pass # TODO: calcular paridade
    def setResponse(self, response):
        self.response = str(chr(response))
    def getControl(self):
        return self.control
    def getOrigin(self):
        return self.origin
    def getDestiny(self):
        return self.destiny
    def getSize(self):
        return self.size
    def getData(self):
        return self.data
    def getParity(self):
        return self.parity
    def getResponse(self):
        return ord(self.response)
    def makeHandshake(self, origin, destiny, port):
        self.origin = origin
        self.destiny = destiny
        self.data = port
        self.calcParity()

