import time
import cfg
import control
import socket
import re
import screen
import threading
import random
import os
#import win32com.client

#THINGS TO DO:
#Make the input dict based on the incoming whitelist

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

def checkForMulligan() :
    img = screen.grabButton(screen.MULL_BTTN_COORDS)
    if (screen.testSimilar(img, "mull_btn.png")) :
        time.sleep(1)
        return True
            
    else : 
        time.sleep(1)
        return False

def checkToken() :
    img = screen.grabToken()
    if (screen.checkTokenColor(img) == 1) :
        time.sleep(1)
        return 1
    elif (screen.checkTokenColor(img) == 0) :    
        time.sleep(1)
        return 0
    else :
        time.sleep(1)
        return -1




   
def playBotMatch():
    
    isMulligan = False
    isMyTurn = False
    selectedFromHand = False
    hasNotPassed = True    
    
        #wait until we know we are mulliganing
    while True:
        isMulligan = checkForMulligan()
        if isMulligan :
            break
        
    while isMulligan :
        msg = "Time to mulligan. Choose either left or right, enter to select, or escape to leave the mulligan."
        key_whitelist = ("a", "d", "enter", "escape")           
        #create a polling function designed to take the exact desired data
        
        vote = pollChat(msg, key_whitelist, True)
        print(vote)
        #add check for enters 
        if (vote == "escape") :
            #perform an enter and exit to the round screen
            controlGame("enter")
            isMulligan = False
    
    while hasNotPassed :    
        
        while True :
            check = checkToken()
            if check == 1 :
                isMyTurn = True
                break 

        while isMyTurn :
            
            check = checkToken()
            if check == 0 :
                isMyTurn = False
                selectedFromHand = False
                break 
        
            if (not selectedFromHand) :
                msg = "Choose a card to play."
                key_whitelist = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")
                
                control.PressKey(0x41)
                time.sleep(3)
                control.ReleaseKey(0x41)
                
                vote = pollChat(msg, key_whitelist, False)
                shift_count = number_dict[vote]
                
                for i in range(1, shift_count) :
                    controlGame("d")
                    time.sleep(0.1)
                controlGame("enter")
                #run the card selection stuff
                selectedFromHand = True
            
            else :
                msg = "Time to play the card."
                key_whitelist = ("w", "a", "s", "d", "enter", "space") 
                
                vote = pollChat(msg, key_whitelist, True)
                
                if vote == "space" :
                    control.PressKey(0x20)
                    time.sleep(3)
                    control.ReleaseKey(0x20)
                    hasNotPassed = False
            
            time.sleep(3)
            
    print("Finished!")    
        
        #while isMyTurn :
            #special code counting goes here
            
    #wait for mulligan screen
    #after three selects or escape, wait until token is a color
    #if the token is ever red, dp nothing until you see blue (unless you have passed)
    #if the token is blue, if you have not already passed, try to select a card from hand, ...
        #do not end turn until a red is seen.
    #if a mulligan screen shows up, reset pass metrics and mulligan again


#set up a child thread to run operations for us
threads = []

t = threading.Thread(target=fileCommand)
threads.append(t)
t.start()

#establish a connection to twitch  
s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

s.setblocking(False)

#move to setup function
os.chdir("C:\\Users\\Remy Kaldawy\\Pictures\\gwent_sources")

#introduce yourself
chat(s, "I am a friendly bot! Don't mind me!")

#twitch chat polling code

playBotMatch()

#CODE FOR GENERIC CONTROL
'''
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

'''






        