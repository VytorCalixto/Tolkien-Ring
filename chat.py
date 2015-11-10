#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import select
import argparse
import sys
import curses
import string
from connection import Connection
import message
import time
import datetime
import logging
import ast
logging.basicConfig(filename='tolkien.log', level=logging.DEBUG)

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

def printMessages(screen, messages):
    y = screen.getmaxyx()[0] - 2 #-2 pelas bordas
    i = 1
    for msg in messages[-y:]:
        screen.addstr(i, 1, msg[0], msg[1])
        i+=1

def printMachines(screen, machines):
    x = screen.getmaxyx()[1]
    title = "HOSTS"
    screen.addstr(1, (x - len(title))/2, title, curses.A_BOLD)
    i = 2
    for host, index in machines.items():
        screen.addstr(i, 1, "%s - %s" % (index, getMachineName(host[0])))
        i+=1
    #screen.addstr(i, 1, "%s" % str(machines))

def getMachineName(host):
    return socket.gethostbyaddr(host)[0].split('.')[0]

def connectToMachine(textbox):
    textbox.nodelay(False)
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
    textbox.clear()
    textbox.box()
    textbox.refresh()
    curses.noecho()
    textbox.nodelay(True)
    return (socket.gethostbyname(n), int(p, 10)) if n and p else False

def parseUserMessage(msg, messages, machines, host, connection, s, nextHost):
    s = ''.join(msg)
    s.strip(string.whitespace)
    if s[0] == '/':
        action = s[1:]
        if action == "quit":
            sys.exit(0)
        elif action == "token":
            pass
    try:
        delim_index = msg.index(':')
        machine_index = ''.join(msg[0:delim_index])
        machine_index.strip(string.whitespace)
        if machine_index != 0:
            m = message.Message()
            data = ''.join(msg[delim_index+1:])
            data.strip(string.whitespace)
            m.setData(data)
            m.setOrigin(machines[host])
            m.setDestiny(machine_index)
            messages.append(("Você para %s: %s" % (machine_index, m.getData()), curses.A_NORMAL))
            connection.put_message(s, m.getMessage(), nextHost)
    except Exception, e:
        messages.append(("ERRO: A mensagem deve ter o formato: <host>:<mensagem>\n%s"%e, curses.A_BOLD))
        logging.debug(e)
    finally:
        msg = []
    return msg

def main(stdscr, args):
    stdscr.nodelay(True)

    machines = {}
    messages = []
    msg = []
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    has_token = False
    quantum = 0.25

    if args.port == args.serverPort:
        # TODO: mostrar uma mensagem de erro melhor
        raise ValueError("O valor da porta de rede não pode ser igual ao do servidor de configuração")
        sys.exit(2)

    port = args.port
    serverPort = args.serverPort
    nextHost = (host, port)

    connection = Connection()
    s = connection.open_socket(host, port)
    confserver = connection.open_socket(host, serverPort)
    connection.input_sockets = [confserver,s]
    connection.output_sockets = [confserver,s]

    machines[(host, port)] = '1'
    printHeader(stdscr, hostname, host, "Desconectado")
    yx = stdscr.getmaxyx()

    chatscreen = stdscr.subpad(yx[0]-7, yx[1]-20, 4, 0)
    machinescreen = stdscr.subwin(yx[0]-7, 18, 4, yx[1]-19)
    textbox = stdscr.subwin(3, yx[1]-1, yx[0]-3, 0)

    textbox.nodelay(True)
    curses.curs_set(0)

    messages.append(("INFO: Você não está conectado", curses.A_BOLD))
    messages.append(("INFO: Aperte 'c' para se conectar a alguém", curses.A_BOLD))
    messages.append(("INFO: Aperte 'q' para sair", curses.A_BOLD))
    messages.append(("INFO: Durante o anel digite '/quit' para sair", curses.A_BOLD))
    messages.append(("INFO: Durante o anel digite '/token' para perder o bastão", curses.A_BOLD))
    messages.append(("INFO: Nome da máquina: %s" % hostname, curses.A_BOLD))
    messages.append(("INFO: Porta do servidor: %s" % serverPort, curses.A_BOLD))
    messages.append(("INFO: Porta da rede: %s" % port, curses.A_BOLD))

    curses.cbreak()

    t0 = 0.0
    while True:
        chatscreen.box()
        textbox.box()
        machinescreen.box()
        printMessages(chatscreen, messages)
        printMachines(machinescreen, machines)

        if len(machines) <= 1 or nextHost == (host, port):
            key = stdscr.getch()
            if key == ord('q'):
                sys.exit(0)
            elif key == ord('c'):
                # Pega informações do host
                nextHost = connectToMachine(textbox)
                # Send handshake
                if nextHost:
                    connection.send_handshake(confserver, nextHost, port)
                    messages.append(("INFO: Tentando conectar...", curses.A_BOLD))
                else:
                    nextHost = (host, port)
        else:
            key = textbox.getch()
            if key != -1:
                if (key == curses.KEY_BACKSPACE or key == 127) and msg:
                    msg.pop()
                else:
                    try:
                        c = chr(key)
                        if c == '\n':
                            msg = parseUserMessage(msg, messages, machines, (host, port), connection, s, nextHost)
                        elif c in string.printable:
                            msg.append(c)
                    except ValueError:
                        pass
            # textbox.clear()
            # textbox.box()
            textbox.addstr(1,1, ''.join(msg))
            textbox.noutrefresh()
            if has_token:
                if (time.time() - t0) >= quantum:
                    connection.send_token(s, nextHost)
                    has_token = False
                    printHeader(stdscr, hostname, host, "Conectado: Sem Token")

        ready_to_read,ready_to_write,in_error = connection.poll()

        for sock in ready_to_read:
            data, addr = sock.recvfrom(1024)
            if data:
                n = datetime.datetime.now()
                logging.debug("Data %d:%d:%d: %s" % (n.hour, n.minute, n.second, data))
                m = message.Message()
                m.setMessage(data)
                # if not m.isToken():
                    # messages.append(("data: %s" % m.getData(), curses.A_NORMAL))
                    # messages.append(("data raw: %s" % m.getReadableMessage(), curses.A_NORMAL))
            if sock is confserver:
                if m.isHandshake() and not m.isConfiguration():
                    if len(machines) < 4:
                        connection.ack_handshake(confserver, addr, nextHost)
                        nextHost = (addr[0], int(m.getData(), 10))
                        machines[nextHost] = str(len(machines) + 1)
                        messages.append(("INFO: %s se conectou" % getMachineName(addr[0]), curses.A_BOLD))
                        # Se só tem 2 máquinas, é a primeira conexão
                        if len(machines) == 2:
                            connection.send_token(s, nextHost)
                        conf = message.Message()
                        conf.setConfiguration()
                        conf.setOrigin(machines[(host, port)])
                        conf.setDestiny("5")
                        conf.setData(str(machines))
                        connection.put_message(confserver, conf.getMessage(), nextHost)
                elif m.isHandshake() and m.isConfiguration():
                    otherHost = m.getData()
                    delim_index = otherHost.index(':')
                    nextHost = (otherHost[0:delim_index], int(otherHost[delim_index+1:], 10))
                    messages.append(("INFO: Você se conectou a rede", curses.A_BOLD))
                    printHeader(stdscr, hostname, host, "Conectado")
            else:
                m.setReceived(machines[(host, port)])
                now = datetime.datetime.now()
                if m.isToken():
                    has_token = True
                    t0 = time.time()
                    printHeader(stdscr, hostname, host, "Conectado: Com token")
                elif m.isConfiguration():
                    machines = ast.literal_eval(m.getData())
                    logging.debug("Machines: %s" % str(machines))
                    if m.checkParity():
                        m.setRead(machines[(host, port)])
                else:
                    if m.getDestiny() == machines[(host, port)] or m.getDestiny() == "5":
                        hour = '{:%H:%M:%S}'.format(now)
                        messages.append(("%s-%s: %s" % (hour, getMachineName(addr[0]), m.getData()), curses.A_NORMAL))
                        if m.checkParity():
                            m.setRead(machines[(host, port)])
                if not m.isToken() and m.getOrigin() != machines[(host,port)]:
                    connection.put_message(s, m.getMessage(), nextHost)

        for sock in ready_to_write:
            if connection.has_message(sock):
                connection.send_message(sock)

        chatscreen.noutrefresh()
        machinescreen.noutrefresh()
        curses.doupdate()


if __name__ == "__main__":
    args = parseArgs()
    curses.wrapper(main, args)
