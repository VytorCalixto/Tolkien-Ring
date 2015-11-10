# -*- coding:utf-8 -*-
from binascii import crc32

maxSize = 4095

# Converte um caracter em uma lista que representa o valor binário
def chrToBitList(c):
    return list('{0:08b}'.format(ord(c)))

def intToBitList(i):
    return list('{0:08b}'.format(i))

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
        # Controle: |TMCHRRRR|
        # T = token, M = monitor, C = configuração, H = handshake, R = reservado
        self.control = chr(0)
        self.origin = '0'
        self.destiny = '0'
        # 3 bytes
        self.size = '0'
        self.data = '0'
        # 4 bytes
        self.parity = chr(0)
        self.response = chr(0)

    def setControl(self, control):
        self.control = bitStringToChr(control)

    def setToken(self):
        self.control = setBitOneFromChr(self.control, 0)

    def setMonitor(self):
        self.control = setBitOneFromChr(self.control, 1)

    def setConfiguration(self):
        self.control = setBitOneFromChr(self.control, 2)

    def setHandshake(self):
        self.control = setBitOneFromChr(self.control, 3)

    def setOrigin(self, origin):
        self.origin = origin

    def setDestiny(self, destiny):
        self.destiny = destiny

    def setSize(self, size):
        if size <= maxSize:
            self.size = '{0:03x}'.format(size)
        else:
            # Throw error
            pass

    def setData(self, data):
        if len(data) <= maxSize:
            self.data = data
            self.setSize(len(data))
        else:
            # Throw error
            pass

    def calcParity(self):
        data = self.getMessageWithoutParity()
        parity = crc32(data) & 0xffffffff
        bitList = intToBitList(parity)
        chrList = [bitListToChar(bitList[0:8]), bitListToChar(bitList[8:16]), bitListToChar(bitList[16:24]), bitListToChar(bitList[24:32])]
        self.parity = ''.join(chrList)

    def setResponse(self, response):
        self.response = chr(response)

    def setReceived(self, machine):
        i = int(machine, 10) - 1
        # machine é o número da máquina no anel (0, 3)
        # O bit mais a esquerda diz que a msg foi recebida
        # O bit mais a direita diz que a msg foi aceita
        # |Resposta|
        # |AABBCCDD|
        self.response = setBitOneFromChr(self.response, i * 2)

    def setRead(self, machine):
        i = int(machine, 10) - 1
        self.response = setBitOneFromChr(self.response, i * 2 + 1)

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
        return int(self.size, 16)

    def getData(self):
        return self.data

    def getParity(self):
        return self.parity

    def checkParity(self):
        data = self.getMessageWithoutParity()
        parity = crc32(data) & 0xffffffff
        bitList = intToBitList(parity)
        chrList = [bitListToChar(bitList[0:8]), bitListToChar(bitList[8:16]), bitListToChar(bitList[16:24]), bitListToChar(bitList[24:32])]
        return (''.join(chrList) == self.parity)

    def getResponse(self):
        return self.response

    def getReceived(self, machine):
        i = int(machine, 10) - 1
        return chrToBitString(self.response)[i*2] == "1"

    def getAllReceived(self, machine):
        # machine é a máquina que enviou
        i = int(machine, 10) - 1
        m = [0, 1, 2, 3]
        del m[i]
        response = chrToBitString(self.response)
        for r in m:
            if response[r*2] == "0":
                return False
        return True


    def getRead(self, machine):
        i = int(machine, 10) - 1
        return chrToBitString(self.response)[i*2 + 1] == "1"

    def getAllRead(self, machine):
        # machine é a máquina que enviou
        i = int(machine, 10) - 1
        m = [0, 1, 2, 3]
        del m[i]
        response = chrToBitString(self.response)
        for r in m:
            if response[r*2 + 1] == "0":
                return False
        return True

    def setMessage(self, message):
        msgSize = len(message)
        self.control = message[0]
        self.origin = message[1]
        self.destiny = message[2]
        self.size = message[3:6]
        self.data = message[6:-5]
        self.parity = message[-5:-1]
        self.response = message[-1]

    def getMessage(self):
        self.calcParity()
        m = [self.control, self.origin, self.destiny, self.size, self.data, self.parity, self.response]
        return ''.join(m)

    def getMessageWithoutParity(self):
        m = [self.control, self.origin, self.destiny, self.size, self.data]
        return ''.join(m)

    def getReadableMessage(self):
        m = ['{0:08b}'.format(ord(self.control)), self.origin, self.destiny, self.size, self.data]
        return '|'.join(m)

def makeHandshake(port):
    data = str(port)
    m = Message()
    m.setHandshake()
    m.setData(data)
    return m

def makeAckHandshake(host):
    data = "%s:%s" % (host[0], str(host[1]))
    m = Message()
    m.setConfiguration()
    m.setHandshake()
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
    m.setData(message)
    return m
