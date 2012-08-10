#!/usr/bin/env python2
# coding: utf-8

import sys
import socket
import string
import urllib
import urllib2
import json
import time
import random

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

quiting=False
while not quiting:
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
                rnick=sline[0][1:].split("!")[0]
                if not rnick.endswith("bot"):
                    time.sleep(2)
                    s.send("PRIVMSG %s :%s: 欢迎加入 %s 频道，我是聊天机器人，和我聊天请加上“%s: ”\r\n" % (CHAN, rnick, CHAN, NICK))
            elif sline[1]=="PRIVMSG":
                rnick=sline[0][1:].split("!")[0]
                if line.find(" PRIVMSG %s :" % NICK)!=-1:
                    if line.split(" PRIVMSG %s :" % NICK)[1]=="Get out of this channel!": # A small hack
                        s.send("QUIT :Client Quit\r\n")
                        quiting=True
                    else:
                        s.send("PRIVMSG %s :%s: 我不接受私信哦，在聊天室里面用“%s: ”开头就可以联系我。\r\n" % (rnick, rnick, NICK))
                else:
                    if line.split(" PRIVMSG %s :" % CHAN)[1].startswith("%s:" % NICK):
                        opener=urllib2.build_opener()
                        opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.101")]

                        resp=opener.open("http://www.simsimi.com/func/req?%s" % urllib.urlencode({"lc": "zh", "msg": line.split(" PRIVMSG %s :%s:" % (CHAN, NICK))[1].lstrip()})).read()
                        if resp=="{}":
                            resp="我不明白你的意思。"
                        else:
                            resp=json.loads(resp)["response"].encode("utf-8").replace("\n", " ")
                        time.sleep(random.random()*2)
                        s.send("PRIVMSG %s :%s: %s\r\n" % (CHAN, rnick, resp))
        except:
            s.send("PRIVMSG %s :%s 出现了一点小故障，正在努力恢复工作。\r\n" % (CHAN, NICK))

# vim: et ft=python sts=4 sw=4 ts=4
