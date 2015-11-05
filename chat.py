# -*- coding:utf-8 -*-
import socket
import curses
import curses.textpad
import traceback

def printMessages(screen, messages):
    yx = screen.getmaxyx()
    topRange = len(messages) if ((yx[0]-2) > len(messages)) else (yx[0]-2)
    for i in range(0, topRange):
        screen.addstr(i+1, 1, messages[i])

def main(stdscr):
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    port = 1337

    stdscr.nodelay(1)
    stdscr.addstr(0, 0, "Máquina: %s" % (hostname))
    stdscr.addstr(1, 0, "IP: %s" % (host))
    stdscr.addstr(2, 0, "Status: Conectando...")
    stdscr.refresh()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    
    stdscr.clear()
    yx = stdscr.getmaxyx()
    stdscr.addstr(0, 0, "Máquina: %s" % (hostname))
    stdscr.addstr(1, 0, "IP: %s:%d" % (host, port))
    stdscr.addstr(2, 0, "Status: Conectado")
    title = "### TOLKIEN RING ###"
    stdscr.addstr(3, (yx[1] - len(title))/2, title, curses.A_REVERSE)
    stdscr.refresh()
    
    # subscreen do chat
    subscreen = stdscr.subwin(yx[0]-6, yx[1]-1, 4, 0)
    subscreen.box()
    subscreen.refresh()

    messages = []

    while True:
        message, addr = s.recvfrom(1024) # 1024 é o tamanho do buffer
        if message:
            name = socket.gethostbyaddr(addr[0])[0].split('.')[0]
            messages.append("%s: %s" % (name, message))
            printMessages(subscreen, messages)       
            subscreen.box()
            subscreen.refresh()
        

if __name__=='__main__':
    curses.wrapper(main)
