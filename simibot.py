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
import re
import threading

HOST="irc.freenode.net"
PORT=6667
NICK="simibot"
IDENT="simibot"
REALNAME="simibot"
CHAN="#Orz"
COOKIES={}

DONTKNOW=[
    "我不明白你的意思。",
    "我不太懂你在说什么。",
    "我们能换一个话题吗？",
    "你高估我了，我没有你想的那么聪明。",
    "我不懂你在说什么。",
    "我对你的问题不太感兴趣。",
    "我还没想好怎么回答你的问题呢。",
    "我应该怎么回答你这个奇怪的问题呢？",
    "我不太懂你的话。",
    "你能跟我解释一下吗？",
    ("你觉得 %s 频道是不是有点冷清？" % CHAN),
    "你的问题让我很纠结。",
    "你的问题让我真的很纠结。",
    "你的问题难倒我了。",
    "我没听说过那个东西。",
    "天天被你们拉去聊天，我都很少了解时事了。",
    "不要问我那么刁钻古怪的问题啦！",
    "我对那个不感兴趣，跟我说说你最喜欢的明星吧。"
]

readbuffer=""
s=socket.socket()
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN :%s\r\n" % CHAN)

def update_cookies(name):
    if name in COOKIES:
        oldcookie, fake_ip=COOKIES[name]
    else:
        oldcookie=None
        fake_ip=int(random.random()*253+1)
    c_opener=urllib2.build_opener()
    c_opener.addheaders = [("Referer", "http://www.simsimi.com/"), ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.%d" % fake_ip)]
    if oldcookie:
        c_opener.addheaders.append(["Cookie", oldcookie])
    f=c_opener.open("http://www.simsimi.com/talk.htm").info()
    if "Set-Cookie" in f:
        newcookie=f["Set-Cookie"]
    else:
        newcookie=""
        newcookie="sagree=true; selected_nc=ch; "+newcookie
    COOKIES[name]=(newcookie, fake_ip)
    time.sleep(random.random()*3)

quiting=False

energy=100
resting=False
def rest():
    global energy, resting, quiting
    while not quiting:
        time.sleep(10)
        if energy<100:
            energy=energy+10
        else:
            resting=False
            energy=100
threading.Thread(target=rest).start()

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
                    s.send("PRIVMSG %s :%s，欢迎加入 %s 频道，我是聊天机器人，和我聊天请在开头加上“%s: ”\r\n" % (CHAN, rnick, CHAN, NICK))
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
                        if not resting:
                            req=line.split(" PRIVMSG %s :%s:" % (CHAN, NICK))[1].strip()
                            if req:
                                energy=energy-8
                                if energy<0:
                                    resting=True
                                    energy=0
                                update_cookies(rnick)
                                req=req.replace(NICK, "SimSimi").replace(CHAN, "这里")
                                opener=urllib2.build_opener()
                                time.sleep(random.random()*2)
                                opener.addheaders = [("Accept", "application/json, text/javascript, */*; q=0.01"), ("Accept-Charset", "UTF-8,*;q=0.5"), ("Accept-Language", "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4"), ("Cookie", COOKIES[rnick][0]), ("Content-Type", "application/json; charset=utf-8"), ("Referer", "http://www.simsimi.com/talk.htm"), ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.%d" % COOKIES[rnick][1]), ("X-Requested-With", "XMLHttpRequest")]
                                h=opener.open("http://www.simsimi.com/func/req?%s" % urllib.urlencode({"msg": req, "lc": "zh"}))
                                resp=h.read()
                                info=h.info()
                                if "Cookie" in info:
                                    COOKIES[rnick]=info["Cookie"]
                                if resp=="{}":
                                    random.shuffle(DONTKNOW)
                                    resp=DONTKNOW[0]
                                else:
                                    resp=json.loads(resp)["response"].encode("utf-8").replace("\n", " ")
                                    if resp=="hi":
                                        update_cookies(rnick)
                                    resp=re.sub("([Ss]im)?[sS]imi|小(黄|黃)?(鸡|雞)|(机|機)器(鸡|雞)|(黄|黃)小(鸡|雞)", NICK, resp)
                            else:
                                resp=("你想说什么？在“%s: ”后面输入你想说的话。" % NICK)
                        else:
                            time.sleep(random.random()*2)
                            resp="呼呼～好累，我要休息。"
                        s.send("PRIVMSG %s :%s: %s\r\n" % (CHAN, rnick, resp))
        except KeyboardInterrupt:
            quiting=True
        except Exception as e:
            s.send("PRIVMSG %s :%s 出现了一点小故障，正在努力恢复工作: %s\r\n" % (CHAN, NICK, e))

# vim: et ft=python sts=4 sw=4 ts=4
