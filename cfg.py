import socket

HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "Scoot_Poot"            # your Twitch username, lowercase
PASS = "oauth:kj3l7m3whdla4vnvnpzhe0c4em4b2j" # your Twitch OAuth token
CHAN = "#scoot_poot"
RATE = (20/30)  
BUFF = 10

SOCKET = socket.socket()