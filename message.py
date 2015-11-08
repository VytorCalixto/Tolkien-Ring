
# Converte um caracter em uma lista que representa o valor binário
def chrToBitList(c):
    return list('{0:08b}'.format(ord(c)))

def chrToBitString(c):
    return '{0:08b}'.format(ord(c))

# Converte uma lista para um caracter
def bitListToChar(l):
    return chr(int(''.join(l), 2))

def bitStringToChr(s):
    return chr(int(s, 2))

def setBitOneFromChr(c, i):
    l = chrToBitList(c)
    l[i] = '1'
    return bitListToChar(l)

class Message(object):
    def __init__(self):
        # |TMCHRRRR|
        # T = token, M = monitor, C = configuração, H = handshake, R = reservado
        self.control = ''
        self.origin = ''
        self.destiny = ''
        self.size = 0
        self.data = ''
        self.parity = ''
        self.response = chr(0)

    def setControl(self, control):
        self.control = bitStringToChr(control)

    def setToken(self):
        setBitOneFromChr(self.control, 0)

    def setMonitor(self):
        setBitOneFromChr(self.control, 1)

    def setConfiguration(self):
        setBitOneFromChr(self.control, 2)

    def setHandshake(self):
        setBitOneFromChr(self.control, 3)

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
        setBitOneFromChr(self.response, machine * 2)
    def setRead(self, machine):
        setBitOneFromChr(self.response, machine * 2 + 1)

    def getControl(self):
        return self.control

    def isToken(self):
        return chrToBitString(self.control)[0] == '1'

    def isMonitor(self):
        return chrToBitString(self.control)[1] == '1'

    def isConfiguration(self):
        return chrToBitString(self.control)[2] == '1'

    def isHandshake(self):
        return chrToBitString(self.control)[3] == '1'

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

    def checkParity(self):
        # TODO: checar paridade
        pass

    def getResponse(self):
        return self.response

    def getMessage(sef):
        m.calcParity()
        m = [self.control, self.origin, self.destiny, self.size, self.data, self.parity, self.response]
        return ''.join(m)

def makeHandshake(port):
    data = str(port)
    m = Message()
    m.setHandshake()
    m.setSize(len(data))
    m.setData(data)
    return m

def makeAckHandshake(host, port):
    data = "%s:%s" % (host, str(port))
    m = Message()
    m.setConfiguration()
    m.setHandshake()
    m.setSize(len(data))
    m.setData(data)
    return m

def makeToken():
    m = Message()
    m.setToken()
    return m

def makeMonitor():
    m = Message()
    m.setToken()
    m.setMonitor()
    return m

def makeMessage(message):
    m = Message()
    m.setSize(len(message))
    m.setData(message)
    return m
