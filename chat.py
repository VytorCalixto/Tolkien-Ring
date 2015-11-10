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
from timeout import Timer

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
    lose_token = False
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
        s = ''.join(msg)
        s.strip(string.whitespace)
        if s[0] == '/':
            action = s[1:]
            if action == "quit":
                sys.exit(0)
            elif action == "token":
                lose_token = True
        else:
            messages.append(("ERRO: A mensagem deve ter o formato: <host>:<mensagem>\n%s"%e, curses.A_BOLD))
            logging.debug(e)
    finally:
        msg = []
    return (msg, lose_token)

def main(stdscr, args):
    stdscr.nodelay(True)

    connectionTimeout = Timer("conn", 5.0)
    tokenTimeout = Timer("token", 5.0)
    msgTimeout = Timer("msg", 1.5)
    timeouts = {"conn":connectionTimeout, "token":tokenTimeout, "msg":msgTimeout}

    machines = {}
    messages = []
    msg = []
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    has_msg_on_ring = False
    has_token = False
    lose_token = False
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
                    timeouts["conn"].start()
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
                            msg, lose_token = parseUserMessage(msg, messages, machines, (host, port), connection, s, nextHost)
                        elif c in string.printable and len(msg) <= message.maxSize:
                            msg.append(c)
                    except ValueError:
                        pass
            # textbox.clear()
            # textbox.box()
            textbox.addstr(1, 1, ''.join(msg[-(textbox.getmaxyx()[1]-2):]))
            textbox.noutrefresh()

            if has_token:
                if lose_token:
                    lose_token = False
                    has_token = False
                    logging.debug("Perdi o token")
                elif (time.time() - t0) >= quantum:
                    connection.send_token(s, nextHost)
                    has_token = False
                    timeouts["token"].start()
                    printHeader(stdscr, hostname, host, "Conectado: Sem Token")
                    logging.debug("Enviei o token")

        # Checa os timeouts
        for name, t in timeouts.items():
            if t.hasTimedOut():
                if t is connectionTimeout:
                    messages.append(("INFO: Não foi possível se conectar. Tente novamente.", curses.A_BOLD))
                    timeouts["conn"].reset()
                elif t is tokenTimeout:
                    messages.append(("INFO: Token Timeout", curses.A_BOLD))
                    connection.send_token(confserver, nextHost, True, machines[(host, port)])
                    timeouts["token"].start()
                elif t is msgTimeout:
                    messages.append(("INFO: A mensagem não chegou ao destino. Talvez haja um problema com a rede.", curses.A_BOLD))
                    timeouts["msg"].reset()

        ready_to_read,ready_to_write,in_error = connection.poll()

        for sock in ready_to_read:
            data, addr = sock.recvfrom(1024)
            if data:
                n = datetime.datetime.now()
                m = message.Message()
                m.setMessage(data)
                if not m.isToken():
                    logging.debug("Raw data: %s" % m.getReadableMessage())
                    messages.append(("Raw data: %s" % m.getReadableMessage(), curses.A_NORMAL))
            if sock is confserver:
                if m.isHandshake() and not m.isConfiguration():
                    if len(machines) < 4:
                        connection.ack_handshake(confserver, addr, nextHost)
                        nextHost = (addr[0], int(m.getData(), 10))
                        machines[nextHost] = str(len(machines) + 1)
                        messages.append(("INFO: %s se conectou" % getMachineName(addr[0]), curses.A_BOLD))
                        # Se só tem 2 máquinas, é a primeira conexão
                        if len(machines) == 2:
                            connection.send_token(confserver, nextHost)
                        conf = message.Message()
                        conf.setConfiguration()
                        conf.setOrigin(machines[(host, port)])
                        conf.setDestiny("5")
                        conf.setData(str(machines))
                        connection.put_message(confserver, conf.getMessage(), nextHost)
                elif m.isHandshake() and m.isConfiguration():
                    # Recebeu um ack_handshake
                    timeouts["conn"].reset()
                    otherHost = m.getData()
                    delim_index = otherHost.index(':')
                    nextHost = (otherHost[0:delim_index], int(otherHost[delim_index+1:], 10))
                    messages.append(("INFO: Você se conectou a rede", curses.A_BOLD))
                    printHeader(stdscr, hostname, host, "Conectado")
            else:
                m.setReceived(machines[(host, port)])
                now = datetime.datetime.now()
                is_received = False
                is_read = False
                is_owner = m.getOrigin() == machines[(host, port)]
                if is_owner:
                    timeouts["msg"].reset()
                    has_msg_on_ring = False
                    if m.getDestiny() == "5":
                        if m.getAllReceived(machines[(host, port)]) and m.getAllRead(machines[(host, port)]):
                            is_received = is_read = True
                    else:
                        is_received = m.getReceived(m.getOrigin())
                        is_read = m.getRead(m.getOrigin())
                    if not is_read or not is_received:
                        connection.put_message(s, m.getMessage(), nextHost)
                if m.isToken():
                    timeouts["token"].reset()
                    has_token = True
                    t0 = time.time()
                    printHeader(stdscr, hostname, host, "Conectado: Com token")
                    messages.append(("Token", curses.A_BOLD))
                    if m.isMonitor() and not is_owner:
                        connection.put_message(confserver, m.getMessage(), nextHost)
                elif m.isConfiguration():
                    if m.checkParity():
                        machines = ast.literal_eval(m.getData())
                        m.setRead(machines[(host, port)])
                        logging.debug("Machines: %s" % str(machines))
                else:
                    if m.getDestiny() == machines[(host, port)] or m.getDestiny() == "5":
                        if m.checkParity():
                            m.setRead(machines[(host, port)])
                            hour = '{:%H:%M:%S}'.format(now)
                            messages.append(("%s-%s: %s" % (hour, getMachineName(addr[0]), m.getData()), curses.A_NORMAL))
                if not m.isToken() and not is_owner:
                    connection.put_message(s, m.getMessage(), nextHost)

        for sock in ready_to_write:
            if sock is confserver or len(machines) < 2:
                if connection.has_message(sock):
                    connection.send_message(sock)
            elif has_token and not has_msg_on_ring:
                if connection.has_message(sock):
                    connection.send_message(sock)
                    has_msg_on_ring = True
                    timeouts["msg"].start()

        chatscreen.noutrefresh()
        machinescreen.noutrefresh()
        curses.doupdate()


if __name__ == "__main__":
    args = parseArgs()
    curses.wrapper(main, args)
