# -*- coding:utf-8 -*-
import socket

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
print "Você está na máquina %s, IP %s" % (hostname, host)
port = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
print "Servidor rodando na porta %d" % port

nextHostname = raw_input("Em qual máquina você quer se conectar?\n")
nextHost = socket.gethostbyname(nextHostname)
print nextHost

while 1:
    message, addr = s.recvfrom(1024) # 1024 é o tamanho do buffer
    if message:
        print addr, ">:", message
        #s.sendto(hostname + " responde: " + message, addr) # replica a mensagem
