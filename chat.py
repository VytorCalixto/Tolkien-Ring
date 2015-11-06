#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import argparse
import sys
import curses

def parseArgs():
    parser = argparse.ArgumentParser(description="TolkienRing: Chat em anel de até 4 máquinas", prog="chat")
    parser.add_argument("-p", "--port", type=int, help="Porta de comunicação", default=1337)
    parser.add_argument("-s", "--serverPort", type=int, help="Porta do servidor do anel", default=5050)
    parser.add_argument("-c", "--configurationServer", help="Inicia no modo de configuração", action="store_true")
    return parser.parse_args()

def printHeader(screen, hostname, ip, status):
    screen.clear()
    screen.addstr(0, 0, "Máquina: %s" % hostname)
    screen.addstr(1, 0, "IP: %s" % ip)
    screen.addstr(2, 0, "Status: %s" % status)
    x = screen.getmaxyx()[1]
    title = "### TolkienRing ###"
    screen.addstr(3, (x - len(title))/2, title, curses.A_REVERSE)
    screen.refresh()

def printMessages(screen, messages):
    yx = screen.getmaxyx()
    topRange = len(messages) if ((yx[0]-2) > len(messages)) else (yx[0]-2)
    for i in range(0, topRange):
        screen.addstr(i+1, 1, messages[i][0], messages[i][1])

def main(stdscr, args):
    stdscr.nodelay(True)

    machines = []
    messages = []
    nextHost = (0,0)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)

    if args.port == args.serverPort:
        # TODO: mostrar uma mensagem de erro melhor
        raise ValueError("O valor da porta de rede não pode ser igual ao do servidor de configuração")
        sys.exit(2)

    port = args.port
    serverPort = args.serverPort
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    confserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    s.setblocking(False)
    confserver.bind((host, serverPort))
    confserver.setblocking(False)

    machines.append((host, port, serverPort))
    printHeader(stdscr, hostname, host, "Desconectado")
    yx = stdscr.getmaxyx()

    chatscreen = stdscr.subwin(yx[0]-7, yx[1]-1, 4, 0)
    textbox = stdscr.subwin(3, yx[1]-1, yx[0]-3, 0)
    stdscr.nodelay(True)
    chatscreen.nodelay(True)
    
    close = False
    curses.curs_set(0)
    messages.append(("INFO: Você não está conectado", curses.A_BOLD))
    messages.append(("INFO: Aperte 'c' para se conectar a alguém", curses.A_BOLD))
    messages.append(("INFO: Nome da máquina: %s" % hostname, curses.A_BOLD))
    messages.append(("INFO: Porta do servidor: %s" % serverPort, curses.A_BOLD))
    messages.append(("INFO: Porta da rede: %s" % port, curses.A_BOLD))
   
    while not close:
        chatscreen.box()
        textbox.box()
        printMessages(chatscreen, messages)        
        if(len(machines) <= 1):
            c = chatscreen.getch()
            if c == ord('c'):
                # Pega informações do host
                curses.curs_set(1)
                curses.echo()
                textbox.addstr(0, 1, "Digite o nome da máquina:")
                textbox.refresh()
                n = textbox.getstr(1, 1)
                textbox.clear()
                textbox.box()
                textbox.refresh()
                textbox.addstr(0, 1, "Digite a porta (a porta padrão é 5050):")
                textbox.refresh()
                p = textbox.getstr(1, 1)
                nextHost = (socket.gethostbyname(n), int(p))
                textbox.clear()
                textbox.box()
                textbox.refresh()
                curses.curs_set(0)
                curses.noecho()
                # manda handshake
                try:
                    confserver.sendto("handshake", nextHost)
                    messages.append(("INFO: Tentando conectar...", curses.A_BOLD))
                except socket.error:
                    pass
                # espera resposta
            # espera alguém tentar conectar
            try:
                data, addr = confserver.recvfrom(1024)
            except socket.error:
                pass
            else:
                if data:
                    messages.append(("data: %s" % data, curses.A_NORMAL))
                if data == "handshake":
                    try:
                        confserver.sendto("ok", addr)
                        machines.append(addr)
                        messages.append(("INFO: máquina %s se conectou" % addr[0], curses.A_BOLD))
                    except socket.error:
                        pass
                elif data == "ok":
                    nextHost = (nextHost[0], port)
                    machines.append(addr)
                    messages.append(("INFO: você se conectou a rede", curses.A_BOLD))

        chatscreen.refresh()
        textbox.refresh()


if __name__ == "__main__":
    args = parseArgs()
    curses.wrapper(main, args)
