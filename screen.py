from PIL import ImageGrab
from PIL import Image
from PIL import ImageChops
import os
import time
import numpy as np

TOKEN_COORDS = (130, 470, 280, 610) 
HAND_COUNT_COORDS = (430, 1010, 480, 1050)
QUIT_BTTN_COORDS = (915, 990, 1005, 1030)
MULL_BTTN_COORDS = (805, 1020, 980, 1055)
EXIT_BTTN_COORDS = (975, 1000, 1065, 1043)

BLUE_RGB = (0, 0, 255)
RED_RGB = (255, 0, 0)
GRAY = [90, 101, 107]


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
    
    

