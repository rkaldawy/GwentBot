import cfg
import bot
import threading
import os
import gwent

threads = []

t = threading.Thread(target=bot.fileCommand)
threads.append(t)
t.start()

#establish a connection to twitch  
s = cfg.SOCKET
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

s.setblocking(False)

#move to setup function
os.chdir("C:\\Users\\Remy Kaldawy\\Pictures\\gwent_sources")

#introduce yourself
bot.chat(s, "I am a friendly bot! Don't mind me!")

#twitch chat polling code

gwent.playBotMatch()