import screen
import time
from bot import *

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
        if vote == "escape" :
            #perform an enter and exit to the round screen
            controlGame("enter")
            isMulligan = False
        elif vote == "enter" :
            time.sleep(2)
            check = checkToken()
            if check == 1 :
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