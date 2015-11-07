class Message(object):
    def __init__(self):
        self.control = ''
        self.origin = ''
        self.destiny = ''
        self.size = 0
        self.data = ''
        self.parity = ''
        self.response = chr(0)
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
        self.response = chr(response)
    def setReceived(self, machine):
        # machine é o número da máquina no anel (0, 3)
        # O bit mais a esquerda diz que a msg foi recebida
        # O bit mais a direita diz que a msg foi aceita
        # |Resposta|
        # |AABBCCDD|
        response = list(self.getResponse())
        response[machine*2] = '1'
        self.response = chr(int(''.join(response), 2))
    def setRead(self, machine):
        response = list(self.getResponse())
        response[machine*2 + 1] = '1'
        self.response = chr(int(''.join(response), 2))
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
    def checkParity(self);
        # TODO: checar paridade
        pass
    def getResponse(self):
        return '{0:08b}'.format(ord(self.response))
    def makeHandshake(self, origin, destiny, port):
        self.origin = origin
        self.destiny = destiny
        self.data = port
        self.calcParity()

