#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import select
import argparse
import sys
import curses
import string
from connection import Connection

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

def printMachines(screen, machines):
    x = screen.getmaxyx()[1]
    title = "HOSTS"
    screen.addstr(1, (x - len(title))/2, title, curses.A_BOLD)
    for i in range(0, len(machines)):
        host = machines[i][0]
        screen.addstr(i+2, 1, "%d - %s" % (i, getMachineName(host)) )

def getMachineName(host):
    return socket.gethostbyaddr(host)[0].split('.')[0]

def main(stdscr, args):
    stdscr.nodelay(1)

    machines = []
    messages = []
    msg = []
    nextHost = (0,0)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)

    if args.port == args.serverPort:
        # TODO: mostrar uma mensagem de erro melhor
        raise ValueError("O valor da porta de rede não pode ser igual ao do servidor de configuração")
        sys.exit(2)

    port = args.port
    serverPort = args.serverPort

    connection = Connection()
    s = connection.open_socket(host, port)
    confserver = connection.open_socket(host, serverPort)
    print("before")
    connection.input_sockets = [s,confserver]
    connection.output_sockets = [s,confserver]
    print("after")

    machines.append((host, port, serverPort))
    printHeader(stdscr, hostname, host, "Desconectado")
    yx = stdscr.getmaxyx()

    chatscreen = stdscr.subwin(yx[0]-7, yx[1]-20, 4, 0)
    machinescreen = stdscr.subwin(yx[0]-7, 18, 4, yx[1]-19)
    textbox = stdscr.subwin(3, yx[1]-1, yx[0]-3, 0)
    chatscreen.nodelay(True)

    curses.curs_set(0)
    messages.append(("INFO: Você não está conectado", curses.A_BOLD))
    messages.append(("INFO: Aperte 'c' para se conectar a alguém", curses.A_BOLD))
    messages.append(("INFO: Nome da máquina: %s" % hostname, curses.A_BOLD))
    messages.append(("INFO: Porta do servidor: %s" % serverPort, curses.A_BOLD))
    messages.append(("INFO: Porta da rede: %s" % port, curses.A_BOLD))

    while True:
        chatscreen.box()
        textbox.box()
        machinescreen.box()
        printMessages(chatscreen, messages)
        printMachines(machinescreen, machines)
        key = chatscreen.getch()
        # ESC key
        if key == 27:
            if chatscreen.getch() == -1:
                break
        if(len(machines) <= 1):
            if key == ord('c'):
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
                # Send handshake
                connection.send_handshake(confserver,nextHost)
                messages.append(("INFO: Tentando conectar...", curses.A_BOLD))
        else:
            if key != -1:
                try:
                    c = chr(key)
                    if c == '\n':
                        messages.append(("você: %s" % ''.join(msg), curses.A_NORMAL))
                        try:
                            delim_index = msg.index(':')
                            machine_index = int(''.join(msg[0:delim_index]))
                            msg_str = ''.join(msg[delim_index+2:])
                            connection.put_message(s,msg_str,machines[machine_index])
                        except Exception, e:
                            messages.append(("ERRO: A mensagem deve ter o formato: <maquina>: <mensagem>", curses.A_BOLD))
                        finally:
                            msg = []
                            textbox.clear()
                            textbox.box()
                            textbox.refresh()
                    elif c in string.printable:
                        msg.append(c)
                        textbox.clear()
                        textbox.box()
                        textbox.addstr(1, 1, string.join(msg, ''))
                        textbox.refresh()
                except ValueError:
                    pass

        ready_to_read,ready_to_write,in_error = connection.poll()

        for sock in ready_to_read:
            data, addr = sock.recvfrom(1024)
            if data:
                messages.append(("data: %s" % data, curses.A_NORMAL))
            if sock is confserver:
                if data == "handshake":
                    connection.ack_handshake(confserver,addr)
                    machines.append(addr)
                    messages.append(("INFO: %s se conectou" % getMachineName(addr[0]), curses.A_BOLD))
                elif data == "ok":
                    machines.append(addr)
                    messages.append(("INFO: Você se conectou a rede", curses.A_BOLD))
            else:
                # Treat message
                pass

        for sock in ready_to_write:
            if connection.has_message(sock):
                connection.send_message(sock)

        chatscreen.refresh()
        textbox.refresh()
        machinescreen.refresh()


if __name__ == "__main__":
    args = parseArgs()
    curses.wrapper(main, args)
