from PIL import ImageGrab
from PIL import Image
from PIL import ImageChops
import os
import time
import numpy as np
import threading
import cfg
from abc import ABCMeta, abstractmethod

TOKEN_COORDS = (130, 470, 280, 610) 
HAND_COUNT_COORDS = (430, 1010, 480, 1050)
QUIT_BTTN_COORDS = (915, 990, 1005, 1030)
MULL_BTTN_COORDS = (805, 1020, 980, 1055)
EXIT_BTTN_COORDS = (975, 1000, 1065, 1043)

BLUE_RGB = (0, 0, 255)
RED_RGB = (255, 0, 0)
GRAY = [90, 101, 107]


## abstract listener class
class ScreenListener(object):
    """ A listener which acquires an area of a screen and tests what is there
    
    Attributes:
        box: The rectangular coordinates of the part of the screen to be sampled.
        thread: the threading object associated with the listener
        semaphore: the semaphore associated with the listener (controlled when the listener finds what it is looking for)
        path: The name of the reference picture the scanner will compare to (null if not applicable)
        
    """
    
    __metaclass__ = ABCMeta
    
    def __init__(self, box, path):
        self.box = box
        self.path = path
        self.thread = threading.Thread(target=self.scanForItem)
        self.semaphore = threading.Semaphore()
        self.foundTarget = 0
    
    
    def grabImage(self):
        return grabArea(self.box)
    
    def freezeListener(self):
        self.semaphore.acquire()
        
    def playListener(self):
        self.semaphore.release()
        
    def startThread(self):
        self.thread.start()
    
    @abstractmethod    
    def scanForItem(self):
        pass    


##button Listener
class TokenListener(ScreenListener):
    
    def scanForItem(self):
        while True:
            self.semaphore.acquire()
            img = self.grabImage()
            arr = np.array(img)
            avg = np.average(arr, axis=(0, 1)) * [2, 1, 2]
        
            if (avg[0] < 100 and avg[2] > 100) :
                self.foundTarget = 1
            elif (avg[0] > 100 and avg[2] < 100) :
                self.foundTarget = 0
            else :
                self.foundTarget = -1
            self.semaphore.release()
            time.sleep(0.5)
    
class ButtonListener(ScreenListener):
    
    def scanForItem(self):
        while True:
            self.semaphore.acquire()
            img = self.grabImage()
            target = Image.open(self.path)
            arr = np.array(ImageChops.difference(img, target))
            if np.amax(arr) <= 10 :
                self.foundTarget = 1
            else :
                self.foundTarget = 0
            self.semaphore.release()
            time.sleep(0.5)

def initListeners():
    threads = cfg.THREADS
    listeners = cfg.LISTENERS
    
    MulliganButtonListener = ButtonListener(MULL_BTTN_COORDS, "mull_btn.png")
    threads.append(MulliganButtonListener.thread)
    #comment the following line to have the listener start on
    listeners["MulliganButtonListener"] = MulliganButtonListener
    MulliganButtonListener.freezeListener()
    MulliganButtonListener.startThread()
    
    TurnTokenListener = TokenListener(TOKEN_COORDS, "")
    threads.append(TurnTokenListener.thread)
    #comment the following line to have the listener start on
    listeners["TurnTokenListener"] = TurnTokenListener
    TurnTokenListener.freezeListener()
    TurnTokenListener.startThread()
    

def saveImage(img):
    #os.chdir("C:\\Users\\Remy Kaldawy\\Pictures\\")
    img.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')    
    
def grabToken():
    box = TOKEN_COORDS
    im = ImageGrab.grab(box)
    
    return im
   
def grabHandCards():    
    box = HAND_COUNT_COORDS
    im = ImageGrab.grab(box)
    
    return im

def grabButton(coords):
    box = coords
    im = ImageGrab.grab(box)
    
    return im

def grabArea(coords):
    box = coords
    im = ImageGrab.grab(box)
    
    return im

def testSimilar(img, path):  
    quitBttn = Image.open(path)
    arr = np.array(ImageChops.difference(img, quitBttn))
    return np.amax(arr) <= 10
    
def checkTokenColor(img):
    
    arr = np.array(img)
    avg = np.average(arr, axis=(0, 1)) * [2, 1, 2]
    
    if (avg[0] < 100 and avg[2] > 100) :
        return 1
    elif (avg[0] > 100 and avg[2] < 100) :
        return 0
    else :
        return -1
     
def numberAnalysis(img):
    arr = np.array(img)
    
    for x in range(arr.shape[0]):
        for y in range(arr.shape[1]):
            if np.array_equal(arr[x, y], GRAY) :
                arr[x, y] = [255, 255, 255]
            else :
                arr[x, y] = [0, 0, 0]
    
    new_img = Image.fromarray(arr, "RGB")
    saveImage(new_img)
    
#TESTING THE OBJECTS
#make sure to remove when done testing
#os.chdir("C:\\Users\\Remy Kaldawy\\Pictures\\gwent_sources")
#initListeners()
