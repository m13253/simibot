#!/usr/bin/env python2
# coding: utf-8

import os
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

import libirc

HOST="irc.freenode.net"
PORT=6667
NICK="simibot"
IDENT="simibot"
REALNAME="simibot"
CHANS=["#Orz"]
COOKIES={}

DONTKNOW=[
    u"我不明白你的意思。",
    u"我不太懂你在说什么。",
    u"我们能换一个话题吗？",
    u"你高估我了，我没有你想的那么聪明。",
    u"我不懂你在说什么。",
    u"我对你的问题不太感兴趣。",
    u"我还没想好怎么回答你的问题呢。",
    u"我应该怎么回答你这个奇怪的问题呢？",
    u"我不太懂你的话。",
    u"你能跟我解释一下吗？",
    u"你的问题让我很纠结。",
    u"你的问题让我真的很纠结。",
    u"你的问题难倒我了。",
    u"我没听说过那个东西。",
    u"天天被你们拉去聊天，我都很少了解时事了。",
    u"不要问我那么刁钻古怪的问题啦！",
    u"我对那个不感兴趣，跟我说说你最喜欢的明星吧。",
    u"我不关心那个，跟我说说你最喜欢的明星吧。",
    u"我对那个不感兴趣，跟我说说最近的新闻吧。",
    u"我不关心那个，跟我说说最近的新闻吧。"
]

try:
    c=libirc.IRCConnection()
    c.connect(HOST, PORT)
    c.setnick(NICK)
    c.setuser(IDENT, REALNAME)
    for CHAN in CHANS:
        c.join(CHAN)
except:
    time.sleep(10)
    sys.stderr.write("Restarting...\n")
    os.execlp("python2", "python2", __file__)
    raise
CHAN=CHANS[0]

def update_cookies(name):
    if name in COOKIES:
        fake_ip=COOKIES[name][1]
    else:
        fake_ip=int(random.random()*253+1)
    c_opener=urllib2.build_opener()
    c_opener.addheaders = [("Referer", "http://www.simsimi.com/"), ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.%d" % fake_ip)]
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
    if not c.sock:
        quiting=True
        time.sleep(10)
        sys.stderr.write("Restarting...\n")
        os.execlp("python2", "python2", __file__)
        break
    try:
        line=c.recvline(block=True)
        if not line:
            continue
        sys.stderr.write("%s\n" % line.encode('utf-8', 'replace'))
        line=c.parse(line=line)
        if line:
            if line["cmd"]=="JOIN":
                if line["nick"] and not line["nick"].endswith("bot"):
                    time.sleep(2)
                    c.say(line["dest"], u"%s，欢迎加入 %s 频道，我是聊天机器人，和我聊天请在开头加上“%s: ”" % (line["nick"], line["dest"], NICK))
            elif line["cmd"]=="PRIVMSG":
                if line["dest"]==NICK and line["msg"]:
                    if line["msg"]==u"Get out of this channel!": # A small hack
                        c.quit(u"%s asked to leave." % line["nick"])
                        quiting=True
                    elif not line["msg"].startswith(u"\x01"):
                        c.say(line["nick"], u"%s: 我不接受私信哦，在聊天室里面用“%s: ”开头就可以联系我。" % (line["nick"], NICK))
                else:
                    if line["msg"] and line["msg"].startswith(u"%s:" % NICK):
                        if not resting:
                            req=line["msg"].split(u"%s:" % NICK, 1)[1].strip()
                            if req and req.find(u"欢迎加入")==-1:
                                energy=energy-20
                                if energy<0:
                                    resting=True
                                    energy=0
                                if line["nick"]:
                                    rnick=line["nick"]
                                else:
                                    rnick=""
                                if line["dest"]:
                                    CHAN=line["dest"]
                                if not (rnick in COOKIES):
                                    update_cookies(rnick)
                                req=req.replace(NICK, "SimSimi").replace(CHAN+u" 频道", u"这里").replace(CHAN, u"这里").encode('utf-8', 'replace')
                                opener=urllib2.build_opener()
                                time.sleep(random.random()*2)
                                opener.addheaders = [("Accept", "application/json, text/javascript, */*; q=0.01"), ("Accept-Charset", "UTF-8,*;q=0.5"), ("Accept-Language", "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4"), ("Cookie", COOKIES[rnick][0]), ("Content-Type", "application/json; charset=utf-8"), ("Referer", "http://www.simsimi.com/talk.htm"), ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.%d" % COOKIES[rnick][1]), ("X-Requested-With", "XMLHttpRequest")]
                                h=opener.open("http://www.simsimi.com/func/req?%s" % urllib.urlencode({"msg": req, "lc": "zh"}))
                                resp=h.read()
                                info=h.info()
                                if "Set-Cookie" in info:
                                    COOKIES[rnick]=(info["Set-Cookie"], COOKIES[rnick][1])
                                if resp=="{}":
                                    random.shuffle(DONTKNOW)
                                    resp=DONTKNOW[0]
                                else:
                                    resp=json.loads(resp)["response"].replace(u"\n", u" ")
                                    if resp==u"hi":
                                        update_cookies(rnick)
                                    resp=re.sub(u"([Ss]im)?[sS]imi|小(黄|黃)?(鸡|雞)|(机|機)器(鸡|雞)|(黄|黃)小(鸡|雞)", NICK, resp)
                            else:
                                resp=(u"你想说什么？在“%s: ”后面输入你想说的话。" % NICK)
                        else:
                            time.sleep(random.random()*2)
                            resp=u"呼呼～好累，我要休息。"
                        c.say(CHAN, u"%s: %s" % (rnick, resp))
    except KeyboardInterrupt:
        quiting=True
    except Exception as e:
        try:
            c.say(CHAN, u"%s 出现了一点小故障，正在努力恢复工作: %s" % (NICK, e))
        except:
            pass
    except socket.error as e:
        sys.stderr.write("Error: %s\n", e)
        c.quit("Network error.")

# vim: et ft=python sts=4 sw=4 ts=4
