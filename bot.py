import time
import cfg
import control
import socket
import re
import screen
import threading
import random
import os


#THINGS TO DO:
#Make the input dict based on the incoming whitelist
#Reform the token detector
#make screen listeners

s = cfg.SOCKET

input_dict = dict(w=0, a=0, s=0, d=0, enter=0, escape=0, one=0, two=0, three=0, \
                  four=0, five=0, six=0, seven=0, eight=0, nine=0, ten=0, eleven=0, \
                  twelve = 0, space = 0)
meaning_dict = dict(w="Up", a="Left", s="Down", d="Right", \
                    enter="Enter", escape="Escape", \
                    one="The first card", two="The second card", \
                    three="The third card", four="The fourth card", \
                    five="The fifth card", six="The sixth card", \
                    seven="The seventh card", eight="The eighth card", \
                    nine="The ninth card", ten="The tenth card", \
                    eleven="The eleventh card", twelve="The twelveth card", space="pass")
hexcode_dict = dict(w=0x57, a=0x41, s=0x53, d=0x44, enter=0x0D, escape=0x1B)
number_dict = dict(one=1, two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10, eleven=11, twelve=12)


msg_buffer = []

full_count = threading.Semaphore(0)
empty_count = threading.Semaphore(cfg.BUFF - 1)

def chooseMax(whitelist):
    
    new_dict = {}
    
    for elt in whitelist :
        new_dict[elt] = input_dict[elt]
        
    
    highest = max(new_dict.values())
    if(highest == 0) :
        chat(s, "Nobody has voted! A move will be randomly chosen.")
        #return a randomly chosen move:
        return random.choice(list(new_dict.keys()))
    else :
        max_keys = [k for k, v in new_dict.items() if v == highest]
        index = random.randint(0, len(max_keys) - 1)
        return max_keys[index]
            

def resetDict():
    for elt in input_dict :
        input_dict[elt]= 0
        
        
MSG_ONLY=re.compile(r"\w+: ")

def parseInput(line):
    lines = [s.strip() for s in line.splitlines()]
    parsed = [parseLine(s) for s in lines]  
    messages = [re.sub(MSG_ONLY, "", s) for s in parsed]
    
    for cmd in messages :    
        if cmd[0] == "%" :
            print("New command: " + cmd[1:])
            insertCommand(cmd[1:])

    return parsed
  

def insertCommand(line):
    empty_count.acquire()
    msg_buffer.append(line)
    print(msg_buffer) 
    full_count.release()
    

def fileCommand():
    while True:
        full_count.acquire()
        cmd = msg_buffer[0]
        
        if cmd in input_dict :
            input_dict[cmd] += 1
        
        del msg_buffer[0]
        empty_count.release()
        

def matchVoteToAction(vote):
    return meaning_dict[vote]
              
def printMessageBuffer():
    while True:
        print(msg_buffer)
        time.sleep(2)

def controlGame(vote):  
    #shell = win32com.client.Dispatch("WScript.Shell")
    #shell.AppActivate("Notepad")
    hex_code = hexcode_dict[vote]
    control.PressKey(hex_code)
    time.sleep(0.1)
    control.ReleaseKey(hex_code)


# bot.py
def chat(sock, msg):
    sock.send("PRIVMSG {} : {}\r\n".format(cfg.CHAN, msg).encode("utf-8"))

def ban(sock, user):
    chat(sock, ".ban {}".format(user))

def timeout(sock, user, secs=600):
    chat(sock, ".timeout {}".format(user, secs))

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

def parseLine(line):   
    username = re.search(r"\w+", line).group(0) # return the entire match
    message = CHAT_MSG.sub("", line)
    
    return username + ": " + message

def clearMessages():   
    try:
        s.recv(1024).decode("utf-8")
    except socket.error:
        pass

#////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////

def freeControl():
    
    while True:
        t0 = time.time()
        t1 = t0
        vote_state = 0
        
        chat(s, "Voting for the next turn has begun!")
        while (t1 - t0) < 5 :
            
            try:
                response = s.recv(1024).decode("utf-8")
            except socket.error:
                response = ""
        
            if response == "PING :tmi.twitch.tv\r\n":
                s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            else:      
                parseInput(response)
            t1 = time.time()          
            #time.sleep(0.5)
            
        chat(s, "Voting has ended.")
        #this needs to become a semaphore that is locked until the consumer stops     
        while len(msg_buffer) > 0 :
            pass
        print(input_dict)
        time.sleep(0.5)
        
        #FIX TO ACOMMODATE FOR WHITELIST
        vote = chooseMax()
        chat(s, matchVoteToAction(vote) + " won the vote!")
        print("Winner of vote: " + matchVoteToAction(vote))
        #handle the vote here
        
        #this uses ctypes.windll to simulate keyboard presses as 
        #windows objects
        controlGame(vote)
         
        resetDict()
        time.sleep(1)
        try:
            s.recv(1024).decode("utf-8")
        except socket.error:
            pass


def pollChat(msg, whitelist, makeMove):
    
    clearMessages()
    
    t0 = time.time()
    t1 = t0
    
    chat(s, msg)
    while (t1 - t0) < 5 :
        
        try:
            response = s.recv(1024).decode("utf-8")
        except socket.error:
            response = ""
    
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:      
            parseInput(response)
        t1 = time.time()          
        #time.sleep(0.5)
        
    chat(s, "Voting has ended.")
    
    #this needs to become a semaphore that is locked until the consumer stops     
    while len(msg_buffer) > 0 :
        pass
    print(input_dict)
    
    time.sleep(0.5)
    
    vote = chooseMax(whitelist)
    chat(s, matchVoteToAction(vote) + " won the vote!")
    print("Winner of vote: " + matchVoteToAction(vote))
    #handle the vote here
    
    #this uses ctypes.windll to simulate keyboard presses as 
    #windows objects
    
    if makeMove :
        controlGame(vote)
    resetDict()
    time.sleep(1)
    clearMessages()
    
    return vote





        