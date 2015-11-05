#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import argparse
import sys

def parseArgs():
    parser = argparse.ArgumentParser(description="TolkienRing: Chat em anel de até 4 máquinas", prog="chat")
    parser.add_argument("-p", "--port", type=int, help="Porta de comunicação", default=1337)
    parser.add_argument("-s", "--serverPort", type=int, help="Porta do servidor do anel", default=5050)
    parser.add_argument("-c", "--configurationServer", help="Inicia no modo de configuração", action="store_true")
    return parser.parse_args()


def main(args):
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    print "Você está na máquina %s, IP %s" % (hostname, host)
    if args.port == args.serverPort:
        # TODO: mostrar uma mensagem de erro melhor
        raise ValueError("O valor da porta de rede não pode ser igual ao do servidor de configuração")
        sys.exit(2)
    port = args.port
    serverPort = args.serverPort
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print "Servidor rodando na porta %d" % port
    if args.configurationServer:
        print "Você é o servidor de configuração"
        i = 0
        while(i<4):
            message, addr = s.recvfrom(1024)
            if message == "handshake":
                print addr, "conectou"
                s.sendto("servidor recebeu", addr)
    else:
        servername = raw_input("Digite o nome do servidor: ")
        serverip = socket.gethostbyname(servername)
        serverport = input("Digite a porta do servidor: ")
        # Esse não é o handshake, tem que definir direito as mensagens
        s.sendto("handshake", (serverip, serverport))
        while 1:
            message, addr = s.recvfrom(1024) # 1024 é o tamanho do buffer (talvez tenha que ser maior?)
            if message:
                print addr, ">:", message

if __name__ == "__main__":
    args = parseArgs()
    main(args)
