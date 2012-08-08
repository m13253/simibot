#!/usr/bin/env python2
# coding: utf-8

import sys
import socket
import string
import urllib
import json

HOST="irc.freenode.net"
PORT=6667
NICK="simibot"
IDENT="simibot"
REALNAME="simibot"
CHAN="#Orz"

readbuffer=""
s=socket.socket()
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN :%s\r\n" % CHAN)

while 1:
    readbuffer=readbuffer+s.recv(1024)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()
    for line in temp:
        try:
            print line
            line=string.rstrip(line)
            sline=string.split(line)
            if sline[0]=="PING":
                s.send("PONG %s\r\n" % sline[1])
            elif sline[1]=="JOIN":
                s.send("PRIVMSG %s :欢迎加入 %s 频道，我是聊天机器人，和我聊天请加上“%s: ”\r\n" % (CHAN, CHAN, NICK))
            elif sline[1]=="PRIVMSG":
                rnick=sline[0][1:].split("!")[0]
                if line.split(" PRIVMSG %s :" % CHAN)[1].split(":")[0]==NICK:
                    resp=urllib.urlopen("http://www.simsimi.com/func/req?%s" % urllib.urlencode({"lc": "zh", "msg": line.split(" PRIVMSG %s :%s:" % (CHAN, NICK))[1].lstrip()})).read()
                    if resp=="{}":
                        resp="我不明白你的意思，我可能不够聪明。"
                    else:
                        resp=json.loads(resp)["response"].encode("utf-8")
                    s.send("PRIVMSG %s :%s: %s\r\n" % (CHAN, rnick, resp))
        except:
            s.send("PRIVMSG %s :貌似我出了故障，可能会运行不稳定，请重新启动。\r\n" % CHAN)

# vim: et ft=python sts=4 sw=4 ts=4
