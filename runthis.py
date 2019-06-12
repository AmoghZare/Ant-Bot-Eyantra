'''
* Team Id : <1539>
* Author List : <Manish Dsilva, Amogh Zare, Pritam Mane, Kimaya Desai>
* Filename: task-4-main.py>
* Theme: <Theme name -- Specific to eYRC / eYRCPlus >
* Functions: <Comma separated list of Functions defined in this file>
* Global Variables: <List of global variables defined in this file, none if no global * variables>
'''




import array
import copy
import sys
import time
import RPi.GPIO as GPIO               #Necessary Imports                 
import numpy as np
import cv2
import cv2.aruco as aruco
import os
import aruco_lib as arl
import csv
import picamera
import serial
import operator
from operator import itemgetter

from picamera.array import PiRGBArray
from picamera import PiCamera
import threading

'''

#################################################### SHAPE/COLOUR DETECTION, ARUCO IDS DECODING,shrubs in SA ####################################################################################################
##GLOBAL VARIABLES:
'''
decoded = []
GPIO.cleanup()          #Cleaning up Assigned Pins on RPi
GPIO.setwarnings(False)                         
GPIO.setmode(GPIO.BOARD)   #Following RPi Board Numbering
 
ForwardL = 36           # Setting up Pins on RPi
BackwardL= 38                                  
Motor1E = 40  
ForwardR= 35  
BackwardR = 33  
Motor2E = 37 

redpin   = 11
greenpin = 15
bluepin  = 13 

GPIO.setup(ForwardL,GPIO.OUT)               
GPIO.setup(BackwardL,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)
GPIO.setup(ForwardR,GPIO.OUT)   #Assigning Pins as OUT/PWM
GPIO.setup(BackwardR,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)
left = GPIO.PWM(Motor1E, 1000) 
right = GPIO.PWM(Motor2E, 1000)

GPIO.setup(redpin, GPIO.OUT)
GPIO.setup(greenpin, GPIO.OUT)
GPIO.setup(bluepin, GPIO.OUT)
freq= 100
R_LED=GPIO.PWM(11,freq)
B_LED=GPIO.PWM(15,freq)
G_LED=GPIO.PWM(13,freq)

R_Up = "a"
R_Down = "b"
L_Up = "c"
L_Down = "d"

AH = [['W','T'],['W','L'],['T','H'],['H','L'],[1]]
AH_intermediate = [['S','T'],['S','S'],['T','S'],['S','S'],[1]]
SAH = [['S','T'],['S','S'],['S','T'],['S','S'],[1]]
QAH = AH[4][0]

position = previous_current =current =spos1 =spos2 =arm = para = arm2 = 4
position = 5
arm = arm2 = 0
para = 0

##GLOBAL VARIABLES END
##### RGB LED FUNCTIONS:
def LEDSetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    #time.sleep(1)
    turnoff()
  
def glowLED_RED():
    R_LED.start(1)
    B_LED.start(100)
    G_LED.start(100)
    time.sleep(1)
    turnoff()
    LEDSetup()

def glowLED_BLUE():
    R_LED.start(100)
    B_LED.start(1)
    G_LED.start(100)
    time.sleep(1)
    turnoff()
    LEDSetup()

def glowLED_GREEN():
    R_LED.start(100)
    B_LED.start(100)
    G_LED.start(1)
    time.sleep(1)
    turnoff()
    LEDSetup()

def glowLED_YELLOW():
    R_LED.start(0.01)
    B_LED.start(100)
    G_LED.start(0.01)
    time.sleep(1)
    turnoff()
    LEDSetup()

def turnoff():
    GPIO.setmode(GPIO.BOARD)   
    GPIO.output(11, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)

####################################################################

camera = picamera.PiCamera()   #Uncomment

def camera_capture(imagenumber):
    global camera
    ard = 0
    camera.resolution = (800, 600)
    camera.awb_mode = 'auto'
    camera.start_preview()
    time.sleep(5)
    
    if(imagenumber == 11):     
        image = camera.capture("/home/pi/Aruco1.jpg", resize=(640, 480))
        ard = aruco_detect("/home/pi/Aruco1.jpg")
    
    elif(imagenumber == 12):
        image = camera.capture("/home/pi/Aruco2.jpg", resize=(640, 480))
        ard = aruco_detect("/home/pi/Aruco2.jpg")
        
    elif(imagenumber == 13):
        image = camera.capture("/home/pi/Aruco3.jpg", resize=(640, 480))
        ard = aruco_detect("/home/pi/Aruco3.jpg")
        
    elif(imagenumber == 14):
        image = camera.capture("/home/pi/Aruco4.jpg", resize=(640, 480))
        ard = aruco_detect("/home/pi/Aruco4.jpg")
        
    elif(imagenumber == 6):
        image = camera.capture("/home/pi/Shrub6.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs6.jpg")
        
    elif(imagenumber == 5):
        image = camera.capture("/home/pi/Shrub5.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs5.jpg")
        
    elif(imagenumber == 4):
        image = camera.capture("/home/pi/Shrub4.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs4.jpg")
        
    elif(imagenumber == 3):
        image = camera.capture("/home/pi/Shrub3.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs3.jpg")

    elif(imagenumber == 2):
        image = camera.capture("/home/pi/Shrub2.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs2.jpg")

    elif(imagenumber == 1):
        image = camera.capture("/home/pi/Shrub1.jpg", resize=(640, 480))
        color_detect("/home/pi/Shrubs1.jpg")    
        
    camera.stop_preview()
    return ard

def shrubcam():
        global camera
        camera.resolution = (800, 600)
        camera.awb_mode = 'auto'
        camera.start_preview()
        time.sleep(5)
        image = camera.capture("/home/pi/Sh.jpg", resize=(640, 480))
        color_detect("/home/pi/Sh.jpg")

SA_123 = list()
SA_456 = list()
SA123_sorted = list()
SA456_sorted = list()
SA = list()

##Add SA
imgno = 5
#########################################################
def color_detect(feed):
    global SA,imgno
    img = cv2.imread(feed)
    cv2.imwrite("hi.jpg",img)
    LEDSetup()

    #converting frame(img) from BGR (Blue-Green-Red) to HSV (hue-saturation-value)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imwrite("/home/pi/color.jpg",img)  
    #Red
    lower_1=np.array([0,70,50],np.uint8)  ## 0 70 50
    upper_1=np.array([10,255,255],np.uint8)

    lower_1a=np.array([170,70,50],np.uint8)
    upper_1a=np.array([180,255,255],np.uint8)
    #Blue
    lower_2=np.array([100,100,80],np.uint8)  ## 101 50 38
    upper_2=np.array([110,255,255],np.uint8) ## 110 255 255
    #Green
    lower_3=np.array([60,50,70],np.uint8)
    upper_3=np.array([80,255,255],np.uint8)

    mask_1 = cv2.inRange(hsv, lower_1, upper_1)
    mask_1a= cv2.inRange(hsv,lower_1a,upper_1a)
    red=  cv2.bitwise_or(mask_1,mask_1a)
    blue = cv2.inRange(hsv, lower_2, upper_2)
    green = cv2.inRange(hsv, lower_3, upper_3)
    
    color_block = 'X'
    
    (_,contoursr,hierarchy)=cv2.findContours(red,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    (_,contoursg,hierarchy)=cv2.findContours(green,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    (_,contoursb,hierarchy)=cv2.findContours(blue,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
   
   
    for pic, contour in enumerate(contoursg):

            area = cv2.contourArea(contour)
            if(area>4000):
                print(area)
                M = cv2.moments(contour)
                if M["m00"] != 0:
                  cX = int(M["m10"] / M["m00"])
                  cY = int(M["m01"] / M["m00"])
                else:
                  cX, cY = 0, 0
                img =cv2.drawContours(img,contour,-1,(0,255,0),15)
                print("Green Square has been detected")
                color_block = 'L'
                
                #print("X Coordinate of Green: " + str(cX))
                
                #SA_position(color_block,str(cX),shrubimagenumber)
   
    for pic, contour in enumerate(contoursr):

            area = cv2.contourArea(contour)
            if(area>4000):
                print(area)
                
                M = cv2.moments(contour)
                if M["m00"] != 0:
                  cX = int(M["m10"] / M["m00"])
                  cY = int(M["m01"] / M["m00"])
                else:
                   cX, cY = 0, 0
                img =cv2.drawContours(img,contour,-1,(0,0,255),15)
                print("Red Square has been detected")
                color_block = 'H'
                
                #print("X Coordinate of Red: " + str(cX))
                
                #SA_position(color_block,str(cX),shrubimagenumber)

             

              
    for pic, contour in enumerate(contoursb):

            area = cv2.contourArea(contour)
            if(area>4000):
                print(area)
                M = cv2.moments(contour)
                if M["m00"] != 0:
                  cX = int(M["m10"] / M["m00"])
                  cY = int(M["m01"] / M["m00"])
                else:
                  cX, cY = 0, 0
                img =cv2.drawContours(img,contour,-1,(255,0,0),15)
                print("Blue Square has been detected")
                color_block = 'W'
                
                #print("X Coordinate of Blue: " + str(cX))
                
                #SA_position(color_block,str(cX),shrubimagenumber)
    if(color_block == 'X'):
        LEDSetup()
        print("No Square Detected")
    elif(color_block == 'H'):
        glowLED_RED()
    elif(color_block == 'W'):
        glowLED_BLUE()
    elif(color_block == 'L'):
        glowLED_GREEN()
        
    SA[imgno] =  color_block 
    imgno = imgno - 1
    cv2.imwrite("ColorTrack.jpg",img)

####################

        
def trashdetect():
    LEDSetup()
    global camera      
    camera.resolution = (800, 600)
    camera.start_preview()
    time.sleep(5)
    image = camera.capture("/home/pi/TrashDetect1.jpg", resize=(640, 480))
    trashhere = 0
    img = cv2.imread(image)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    yellow_lower = np.array([22,60,200],np.uint8)
    yellow_upper = np.array([60,255,255],np.uint8)
    yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

    (_,contoursy,hierarchy)=cv2.findContours(yellow,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contoursy):
            area = cv2.contourArea(contour)
            if(area>4000):
                    print("Yellow Block Detected")
                    trashhere = 1
                    glowLED_YELLOW()
                    img =cv2.drawContours(img,contour,-1,(0,0,255),15)
                    
    cv2.imwrite("TrashTrack.jpg",img)
    return trashhere
     
def shrubdecode(x):
    global SA
    SA = list()
    SA.append(x[2])
    SA.append(x[3])
    SA.append(x[1])
    SA.append(x[4])
    SA.append(x[0])
    SA.append(x[5])
    print(SA)    

number = 0
def aruco_detect(feed):          
    
    global number
    flag = 0
    img = cv2.imread(feed)
    cv2.imwrite("Feed.jpg", img)
    id_aruco_trace = 0                  
    det_aruco_list = {}    
    det_aruco_list = arl.detect_Aruco(img)
    
    if det_aruco_list:
        img3 = arl.mark_Aruco(img,det_aruco_list)
        id_aruco_trace = arl.calculate_Robot_State(img3,det_aruco_list) #Returns the ID of the Aruco
        wanted = list(id_aruco_trace.keys())
        print("The Aruco Detected is :"+ str(wanted[0]))        
        if(id_aruco_trace != 0):
            number = number + 1
            flag = 1
        
        cv2.imwrite( str(number)+"Feed.jpg", img3)
    
        decode(wanted[0])
    
    return flag 
                     
'''
* Function Name: <identify>
* Input: < binary equivalent of aruco ids >
* Output: < interpretation of the binary values>
* Logic: <Identifies the position of supply , trash , presence of queen ant hill according to the binary values that are interpretted using aruco ids>
* Example Call: <identify(value)>
'''
def identify(K1):
                global AH , QAH , SAH , AH_intermediate 
                print(K1)
                AH = [[0,0],[0,0],[0,0],[0,0],[-1]]
                QAH_Aruco=AH_Aruco1=AH_Aruco2=QAH_detection=0 
                A0=K1[0]
                A1=K1[1]
                A2=K1[2]
                A3=K1[3]
             
                S1=A0[0]+A1[0]+A2[0]+A3[0]  #first character of decoded Arucos
                S2=A0[1]+A1[1]+A2[1]+A3[1]  #second character of decoded Arucos
                S3=A0[2]+A1[2]+A2[2]+A3[2]  #third character of decoded Arucos
                S4=A0[3]+A1[3]+A2[3]+A3[3]  #fourth character of decoded Arucos
                S5=A0[4]+A1[4]+A2[4]+A3[4]  #fifth character of decoded Arucos
                
                for i in S1:
                    QAH_Aruco=QAH_Aruco+1
                    if(i=='Q'):
                        QAH_detection=1     #Flag to denote if there's a QAH or not
                        print("QAH IS: AH" + str(S2[QAH_Aruco-1]))
                        QAH=S2[QAH_Aruco-1]
                        break 
                
                if(QAH_detection==0):       #There's no QAH
                    QAH=-1
                    print("There is no QAH")

                
                #For service 2
                
                for i in S3:
                    AH_Aruco1=AH_Aruco1+1
                    if(i=='H'):
                        b=int(S2[AH_Aruco1-1])
                        AH[b][1]='H'
                    if(i=='L'):
                        b=int(S2[AH_Aruco1-1])
                        AH[b][1]='L'
                    if(i=='W'):
                        b=int(S2[AH_Aruco1-1])
                        AH[b][1]='W'
                    if(i=='X'):
                        b=int(S2[AH_Aruco1-1])
                        if(S5[AH_Aruco1-1]=='T'):
                         AH[b][1]='T'
                        else:
                         AH[b][1]='X'    
                
                #For Service 1
            
                for i in S4:
                    
                    AH_Aruco2=AH_Aruco2+1
                    
                    if(i=='H'):
                        a=int(S2[AH_Aruco2-1])
                        AH[a][0]='H'
                    if(i=='L'):
                        a=int(S2[AH_Aruco2-1])
                        AH[a][0]='L'  
                    if(i=='W'):
                        a=int(S2[AH_Aruco2-1])
                        AH[a][0]='W'
                    if(i=='X'):
                        a=int(S2[AH_Aruco2-1])
                        if(S5[AH_Aruco2-1]=='T'):
                         AH[a][0]='T'  
                        else:
                         AH[a][0]='X'
                         
                    AH[4][0] = QAH
                #print(AH)
                
                AH_intermediate = intermediate_array(AH)
                
                #print(AH_intermediate)
                PAH = intermediate_array(AH_intermediate)
                SAH = sort_array(PAH)
                #print(SAH)
                return AH



'''
* Function Name: <intermediate_array>
* Input: < array of services including supply types and trash>
* Output: < array of services without specific supply requirements>
* Logic: < replaces 'L' , 'H ' , 'W' with 'S'>
* Example Call: <intermediate_array(value)>
''' 
def intermediate_array(AH):
    
    inter_arr = [[x.replace('L','S').replace('H','S').replace('W','S') for x in l] for l in AH]
    #print(inter_arr)
    return inter_arr

'''
* Function Name: <sort_array>
* Input: < intermediate array that has 'L' , 'H' , 'W' replaced by 'S'>
* Output: < alphabetically sorted array>
* Logic: < alphabetically sorts the intermediate array >
* Example Call: <sort_array(value)>
'''

def sort_array(inter_arr):

     inter_arr = [[x.replace('T','Z') for x in l] for l in inter_arr]
     for x in inter_arr: 
                     x.sort()
     inter_arr = [[x.replace('Z','T') for x in l] for l in inter_arr]
     return inter_arr                     
'''
* Function Name: <decode>
* Input: < decimal equivalent of aruco ids>
* Output: < binary equivalent of aruco ids>
* Logic: < converts the decimal value of aruco ids to binary >
* Example Call: <decode(value)>
'''
counter = 0
all_aruco = []
def decode(arucoid):
    
    global counter
    global all_aruco
    
    binary = format(arucoid,'08b')
    #bit 7 for identifying QAH
    if(binary[0]=="0"):
        Operation = "R"
    elif(binary[0]=="1"):
        Operation = "Q"
        
    #bit 5 and 6 for identifying AH number
    if(binary[1:3]=="00"):
        Operation = Operation + str(0)
    elif(binary[1:3]=="01"):
        Operation = Operation + str(1)
    elif(binary[1:3]=="10"):
        Operation = Operation + str(2)
    elif(binary[1:3]=="11"):
        Operation = Operation + str(3)
        
    #bit 3 and 4 for identifying service 2
    if(binary[3:5]=="00"):
        Operation = Operation + "X"
    elif(binary[3:5]=="01"):
        Operation = Operation + "H"
    elif(binary[3:5]=="10"):
        Operation = Operation + "L"
    elif(binary[3:5]=="11"):
        Operation = Operation + "W"
        
    #bit 1 and 2 for identifying service 1
    if(binary[5:7]=="00"):
        Operation = Operation + "X"
    elif(binary[5:7]=="01"):
        Operation = Operation + "H"
    elif(binary[5:7]=="10"):
        Operation = Operation + "L"
    elif(binary[5:7]=="11"):
        Operation = Operation + "W"
    print(Operation)   
    #bit 0 for identifying trash
    if(binary[7]=="0"):
        Operation =  Operation + "N"
    elif(binary[7]=="1"):
        Operation =  Operation + "T"
    counter = counter + 1
    all_aruco.append(Operation)
    if(counter==4):
        identify(all_aruco)
  
#######################################################################################################################################################################
##################################################### MOTOR FUNCTIONS #################################################################################################
'''
* Function Name: <LeftyF(x)>
* Input: < Inputs x = Time Delay>
* Output: <Left Backward Movement>
* Logic: <Pins for Left Backward movement set High >
* Example Call: <LeftyB(2)>
'''
def LeftyF(x):               #Left Forward Movement Used for Aruco Detection
  left.start(20)   
  right.start(15)                          
  GPIO.output(ForwardL, GPIO.HIGH)
  GPIO.output(BackwardL, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.HIGH)
  right.ChangeDutyCycle(18)
  #print("Right Wheel Backwards")
  left.ChangeDutyCycle(32)
  #print("Aruco Fetch")
  time.sleep(x)
  GPIO.output(ForwardL, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.LOW)
  return 1
'''
* Function Name: <LeftyB(x)>
* Input: < Inputs x = Time Delay>
* Output: <Left Backward Movement>
* Logic: <Pins for Left Backward movement set High >
* Example Call: <LeftyB(2)>
'''
def LeftyB(x):          #Left Backward Movement Used for Aruco Detection
  left.start(20)
  right.start(20)
  GPIO.output(ForwardL, GPIO.LOW)
  GPIO.output(BackwardL, GPIO.HIGH)
  GPIO.output(ForwardR, GPIO.HIGH)
  GPIO.output(BackwardR, GPIO.LOW)
  left.ChangeDutyCycle(25)
  right.ChangeDutyCycle(25)
  #print("Aruco Fetch")
  time.sleep(x)
  GPIO.output(BackwardL, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)
  
  
'''
* Function Name: <RightyF(x)>
* Input: < Inputs x = Time Delay>
* Output: <Right Forward Movement>
* Logic: <Pins for Right Forward movement set High >
* Example Call: <RightyF(2)>
'''
def RightyF(x):     #Right Forward Movement Used for Aruco Detection                              
  right.start(15)   
  left.start(20)                          
  GPIO.output(ForwardR, GPIO.HIGH)
  GPIO.output(BackwardR, GPIO.LOW)
  GPIO.output(ForwardL, GPIO.LOW)
  GPIO.output(BackwardL, GPIO.HIGH)
  
  right.ChangeDutyCycle(18)
  left.ChangeDutyCycle(32)
  #print("Aruco Fetch")
  #print("Right Forward")
  time.sleep(x)
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(BackwardL, GPIO.LOW)
  return 1
  
'''
* Function Name: <RightyB(x)>
* Input: < Inputs x = Time Delay>
* Output: <Right Backward Movement>
* Logic: <Pins for Right Backward movement set High >
* Example Call: <RightyF(2)>
'''
def RightyB(x):      #Right Backward Movement Used for Aruco Detection
  right.start(20)
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.HIGH)
  right.ChangeDutyCycle(50)
  #print("Right Wheel Backwards")
  time.sleep(x)
  GPIO.output(BackwardR, GPIO.LOW)


def RightTurn():     
  right.start(20)
  left.start(20)
  GPIO.output(ForwardR, GPIO.HIGH)
  GPIO.output(BackwardL, GPIO.HIGH)
  GPIO.output(BackwardR, GPIO.LOW)
  GPIO.output(ForwardL, GPIO.LOW)
  right.ChangeDutyCycle(15)
  left.ChangeDutyCycle(28)
  
  print("Right Wheel Turn")

def LeftTurn():     
  right.start(20)
  left.start(20)
  GPIO.output(ForwardL, GPIO.HIGH)
  GPIO.output(BackwardR, GPIO.HIGH)
  GPIO.output(BackwardL, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)
  right.ChangeDutyCycle(15)
  left.ChangeDutyCycle(28)
  print("Left Wheel Turn")
  
'''
* Function Name: <ahead()>
* Input: < NONE>
* Output: <Move Ahead>
* Logic: <Set Left and Right Forward Pins High>
* Example Call: <ahead()>
'''  
def ahead():          #Forward Movement Used for Instantaneous Ahead

        left.start(25)
        right.start(20)
        GPIO.output(ForwardR, GPIO.HIGH)
        GPIO.output(ForwardL, GPIO.HIGH)
        GPIO.output(BackwardR, GPIO.LOW)
        GPIO.output(BackwardL, GPIO.LOW)       
        #print("Moving Forward")
        left.ChangeDutyCycle(32) #
        right.ChangeDutyCycle(20) #34

def back(x):          #Forward Movement Used for Instantaneous Ahead
        left.start(25)
        right.start(25)
        GPIO.output(ForwardR, GPIO.LOW)
        GPIO.output(ForwardL, GPIO.LOW)
        GPIO.output(BackwardR, GPIO.HIGH)
        GPIO.output(BackwardL, GPIO.HIGH)  
        left.ChangeDutyCycle(32.5) #34
        right.ChangeDutyCycle(20) #32
        time.sleep(x)

sl = 48
sr = 25
Kp = 12 #9
error = 0
Kd = 6
def ahead2():          #Forward Movement Used for Instantaneous Ahead
        global sl ,sr,Kp,Kd,P,D
        left.start(15)
        right.start(10)
        GPIO.output(ForwardR, GPIO.HIGH)
        GPIO.output(ForwardL, GPIO.HIGH)
        GPIO.output(BackwardR, GPIO.LOW)
        GPIO.output(BackwardL, GPIO.LOW)       
        #print("Moving Forward")
        try:
          left.ChangeDutyCycle(sl - Kp*P - Kd*D) #
        except: 
          left.ChangeDutyCycle(80)
        try: 
          right.ChangeDutyCycle(sr + Kp*P + Kd*D) #34 
        except:
          (right.ChangeDutyCycle(15))

sl = 30
sr = 20
Kp = 4 #9
error = 0
Kd = 2
def ahead3():          #Forward Movement Used for Instantaneous Ahead
        global sl ,sr,Kp,Kd,P,D
        left.start(10)
        right.start(10)
        GPIO.output(ForwardR, GPIO.HIGH)
        GPIO.output(ForwardL, GPIO.HIGH)
        GPIO.output(BackwardR, GPIO.LOW)
        GPIO.output(BackwardL, GPIO.LOW)       
        #print("Moving Forward")
        try:
          left.ChangeDutyCycle(sl - Kp*P - Kd*D) #
        except: 
          left.ChangeDutyCycle(95)
        try: 
          right.ChangeDutyCycle(sr + Kp*P + Kd*D) #34 
        except:
          (right.ChangeDutyCycle(95))
          
        
def front(x):          #Forward Movement Used for Instantaneous Ahead
        left.start(25)
        right.start(15)
        GPIO.output(ForwardR, GPIO.HIGH)
        GPIO.output(ForwardL, GPIO.HIGH)
        GPIO.output(BackwardR, GPIO.LOW)
        GPIO.output(BackwardL, GPIO.LOW)  
             
        #print("Moving Forward")
        left.ChangeDutyCycle(38)
        right.ChangeDutyCycle(24)
        time.sleep(x)
        
'''
* Function Name: <forwardL()>
* Input: < NONE >
* Output: <Instantaneous left wheel forward>
* Logic: <Pins for Left forward movement set High at that instant >
* Example Call: <forwardL()>
'''  
def forwardL():     #Left Forward Movement Used for Aligning
  left.start(20)    
  GPIO.output(BackwardL, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.LOW)
  GPIO.output(ForwardR, GPIO.LOW)                         
  GPIO.output(ForwardL, GPIO.HIGH)
  left.ChangeDutyCycle(27)  
  print("Moving Left Forward")
  
'''
* Function Name: <forwardR()>
* Input: < NONE >
* Output: <Instantaneous right wheel forward>
* Logic: <Pins for right forward movement set High at that instant >
* Example Call: <forwardR()>
'''  

def forwardR():          #Right Forward Movement Used for Aligning                        
  right.start(20)     
  GPIO.output(BackwardL, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.LOW)
  GPIO.output(ForwardL, GPIO.LOW)                          
  GPIO.output(ForwardR, GPIO.HIGH)
  right.ChangeDutyCycle(20)    ##30
  print("Moving Right Forward")
  

'''
* Function Name: <forward(x)>
* Input: < x is the time for which forward function will run>
* Output: <Forward motion (line following)>
* Logic: < taking input from line sensor forward(x) function calls ahead(), forwardL(), forwardR() as and when required>
* Example Call: <forward(1.5)>
'''

def forward(x): #to follow black line
    global P,D,error
    P = D = 0
    prev_error = 0
    while(1):
        s = serial.Serial("/dev/ttyUSB0",9600) #Establish Serial Communication
        s.baudrate=9600
        t = s.readline() #Readline
        val = str(t).strip("b'").strip("\\n").strip("\\r") #Strip Unnecessary Values
        #print(t)
        print(val)  #print value
        
        if(val==str(1)):   #Align if Bot Off
            P = error = -2
            ahead2()
                
        if(val==str(3)): #Align if Bot Off
            P = error = 2
            ahead2()
    
                   
        if(val==str(2)):   #Move Forward
            P = error = 0
            ahead2()
        
        if(val==str(4)):#Stop if Off the Line 
            P = error = 0.25
            ahead2()
        
        if(val==str(5)):
            break
        
        if(val==str(6)):
            break
        
        D = error - prev_error
        prev_error = error

        
def fortect(x): #to follow black line
    global P,D,error
    P = D = 0
    prev_error = 0
    
    while(1):
        s = serial.Serial("/dev/ttyUSB0",9600) #Establish Serial Communication
        s.baudrate=9600
        t = s.readline() #Readline
        val = str(t).strip("b'").strip("\\n").strip("\\r") #Strip Unnecessary Values
        #print(t)
        print(val)  #print value
        
        if(val==str(1)):   #Align if Bot Off
            P = error = -2
            ahead3()
            #camera_capture(x)
                
        if(val==str(3)): #Align if Bot Off
            P = error = 2
            ahead3()
            #camera_capture(x)
                   
        if(val==str(2)):   #Move Forward
            P = error = 0
            ahead3()
            #camera_capture(x)
        
        if(val==str(4)):#Stop if Off the Line 
            P = error = 0.25
            ahead3()
            #camera_capture(x)
        
        if(val==str(5)):
            break
        
        if(val==str(6)):
            break
        
        D = error - prev_error
        prev_error = error

'''

* Function Name: <DoubleTrashDrop>
* Input: <NONE >
* Output: < none>
* Logic: <Motor calls to drop two trashes one by one at different sides of the TDZ. >
* Example Call: <DoubleTrashDrop()>   


'''

def DoubleTrashDrop():
    global arm,arm2  
    if(arm == 2 or arm2 == 2):
      if(LeftyF(0.9)):
        stop()
        Communication(L_Down)
        time.sleep(7)
        RightyF(0.9)
        
    if(arm == 1 or arm2 == 1):   
      if(RightyF(0.9)):
        stop()
        Communication(R_Down)
        time.sleep(7)
        LeftyF(0.9)
        
    arm = arm2 = 0
  
'''

* Function Name: <StartCN>
* Input: <NONE >
* Output: < none>
* Logic: <Takes the AB to CN from Start point>
* Example Call: <StartCN()>   



'''
def StartCN():
    front(0.3)
    forward(1)
    front(0.1)
    forward(1)
    front(0.25)

'''

* Function Name: <AHopp>
* Input: <NONE >
* Output: < none>
* Logic: <Takes the AB to the opposite AH from a particular AH>
* Example Call: <AHopp()>   




'''

def AHopp():
    U180()
    forward(1)
    front(0.2)

'''

* Function Name: <CNTDZ>
* Input: <NONE >
* Output: < none>
* Logic: <Takes the AB from CN to TDZ>
* Example Call: <CNTDZ()>   


'''
def CNTDZ():
    forward(2)
    front(0.2)
'''

* Function Name: <CNAH>
* Input: <x: AH number >
* Output: < none>
* Logic: <Takes the AB from CN to AH>
* Example Call: <CNAH(1,)>   

'''

def CNAH(x):
 if(x==0):
    Left90()
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)
    
 if(x==3):
    Left90()
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)

 if(x==1):
    Right90()
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)

 if(x==2):
    Right90()
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)
    
 stop()

'''

* Function Name: <AHSA>
* Input: <x: AH number ,para: denotes if the AB needs to take a UTurn or not>
* Output: < none>
* Logic: <Takes the AB from a particular AH to SA>
* Example Call: <AHSA(1,2)>   



'''
def AHSA(x,para):
  if(para == 0):
    U180()

  if(x==0):
    forward(2)
    front(0.35)
    Left90()
    forward(1)
    front(0.35)
    Right90()
    forward(1)
    front(0.35)

  if(x==1):
    forward(2)
    front(0.35)
    Right90()
    forward(1)
    front(0.35)
    Left90()
    forward(1)
    front(0.35)
    
  if(x==2):
    forward(2)
    front(0.35)
    Left90()
    forward(1)
    front(0.35)
    Left90()
    forward(1)
    front(0.35)

  if(x==3):
    forward(2)
    front(0.35)
    Right90()
    forward(1)
    front(0.35)
    Right90()
    forward(1)
    front(0.35)

'''

* Function Name: <AHTDZ>
* Input: <x: AH number ,para: denotes if the AB needs to take a UTurn or not>
* Output: < none>
* Logic: <Takes the AB from a particular AH to TDZ>
* Example Call: <AHTDZ(1,2)>   



'''

def AHTDZ(x,para):

  if(para == 0):
    U180()
    
  if(x==0):
    forward(2)
    front(0.38)
    Left90()
    forward(1)
    front(0.38)
    Left90()
    forward(2)
    front(0.3)

  if(x==1):
    forward(2)
    front(0.38)
    Right90()
    forward(1)
    front(0.38)
    Right90()
    forward(2)
    front(0.3)

  if(x==2):
    forward(2)
    front(0.38)
    Left90()
    forward(1)
    front(0.38)
    Right90()
    forward(2)
    front(0.3)

  if(x==3):
    forward(2)
    front(0.38)
    Right90()
    forward(1)
    front(0.38)
    Left90()
    forward(2)   
    front(0.3)
    
  return 1

'''

* Function Name: <TDZSA>
* Input: <NONE>
* Output: < none>
* Logic: <Takes the AB from TDZ to SA>
* Example Call: <TDZSA()>   

'''
def TDZSA():
    Left90()
    forward(1)
    front(0.3)
    forward(1)
    front(0.35)

'''

* Function Name: <CNSA>
* Input: <NONE>
* Output: < none>
* Logic: <Takes the AB from CN to SA>
* Example Call: <CNSA()>   

'''  

def CNSA():  
    U180()
    forward(1)
    front(0.35)

'''

* Function Name: <AHAH>
* Input: <x: start AH ,y: destination AH ,para: if U_Turn needs to be taken or not>
* Output: < none>
* Logic: <Takes the AB from one AH to another AH>
* Example Call: <AHAH(1,1,2)>   

'''
def AHAH(x,y,para):
 flag = 1
 if(para == 0):
    U180()
    
 if(x==0 and y==1):
    forward(2)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)

 elif(x==0 and y==2):
    forward(2)
    front(0.3)
    Left90()
    forward(1)
    front(0.2)
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)

 elif(x==3 and y==1):
    forward(2)
    front(0.3)
    Right90()
    #stop(5)
    #print("Stopped")

    forward(1)
    front(0.2)
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)

 elif(x==3 and y==2):
    forward(2)
    front(0.3)
    Right90()
    forward(1)
    front(0.25)
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)
    
 elif(x==1 and y==0):
    forward(2)
    front(0.3)
    Right90()
    forward(1)
    front(0.2)
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)

 elif(x==1 and y==3):
    forward(2)
    front(0.3)
    Right90()
    forward(1)
    front(0.25)
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)

 elif(x==2 and y==0):
    forward(2)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)
    forward(1)
    front(0.3)
    Right90()
    forward(1)
    front(0.3)

 elif(x==2 and y==3):
    forward(2)
    front(0.3)
    Left90()
    forward(1)
    front(0.25)
    forward(1)
    front(0.3)
    Left90()
    forward(1)
    front(0.3)
 
 else : 
    forward(2)
    front(0.2)
    forward(2)
    front(0.3)
    
 stop()
 return flag

'''
* Function Name: <SAPU>
* Input: <X: LOCATION OF SHRUB>
* Output: < none>
* Logic: <Takes AB to a particular shrub (S1/2/3/4/5/6) from SA(node near Start)>
* Example Call: <SAPU(1)>
'''

def SAPU(x):
    if(x == 1 or x == 2 or x == 3):
        Right90()
    elif(x == 4 or x == 5 or x == 6):
        Left90()
    if(x==1 or x == 6):
            forward(2)
            front(0.25)
            forward(2)
            front(0.25)
            forward(2)
            front(0.3)
    if(x==2 or x==5):
            forward(2)
            front(0.25)
            forward(2)
            front(0.3)
    if(x==3 or x==4):
            forward(2)
            front(0.3)
    #front(0.15)
    stop()
    return 1


'''
* Function Name: <PUCN>
* Input: <X: LOCATION OF SHRUB>
* Output: < none>
* Logic: <Takes AB to CN from particular shrub (S1/2/3/4/5/6) >
* Example Call: <PUCN(1)>
'''

def PUCN(x):
        
    if(x==1 or x == 6):
            forward(2)
            front(0.25)
            forward(2)
            front(0.25)
            forward(2)
            front(0.3)
    if(x==2 or x==5):
            forward(2)
            front(0.25)
            forward(2)
            front(0.3)
    if(x==3 or x==4):
            forward(2)
            front(0.3)
            
    if(x == 1 or x == 2 or x == 3):
        front(0.1)
        Left90()
        forward(1)
        front(0.3)
    elif(x == 4 or x == 5 or x == 6):
        front(0.1)
        Right90()
        forward(1)
        front(0.3)
    


'''
* Function Name: <STravel>
* Input: <X: start shrub, Y: end_shrub>
* Output: < none>
* Logic: <Takes AB to a particular shrub (S1/2/3/4/5/6) from a  particular shrub>
* Example Call: <STravel(1,2)>
'''   

def STravel(x,y):
    if ((x == 3 and y == 1) or (x == 4 and y == 6)):
        forward(2)
        front(0.25)
        forward(2)
        front(0.4)

    elif ((x == 1 and y == 3) or (x == 6  and y == 4)):
        if(x == 1 or x == 2 or x == 3):
            if(x == 1):
              front(0.3)
            Left90()
            Left90()
            LeftyF(0.2)
    
        elif(x == 4 or x == 5 or x == 6):
            if(x == 6):
              front(0.3)
            Right90()
            Right90()
            RightyF(0.2)
        
        forward(2)
        front(0.2)
        forward(2)
        front(0.3)

        
    elif((x == 3 and y == 2) or (x == 2 and y == 1) or (x == 4 and y == 5) or (x == 5 and y == 6)):

        forward(2)
        front(0.3)
        if(y == 1 or y == 6):
          front(0.45)

         
        
    elif((x == 2 and y == 3) or (x == 1 and y == 2) or (x == 5 and y == 4) or (x == 6 and y == 5)):
        if(x == 1 or x == 2 or x == 3):
            if(x == 1):
              front(0.45)
            else: front(0.25)
            Left90()
            Left90
    
        elif(x == 4 or x == 5 or x == 6):
          if(x == 6):
              front(0.45)
          else: front(0.25)
          Right90()
          Right90()
          
        forward(2)
        front(0.3)
    
    else:
        print("Not Hghhhhhhhhere")
        if(x == 1 or x == 2 or x == 3):
            if(x == 1):
              front(0.25)
            else:front(0.25)
            Left90()
            Left90() ##############
            
    
        elif(x == 4 or x == 5 or x == 6):
            if(x == 6):
              front(0.35)
            else:front(0.25)
            Right90()
            Right90()
        
        for counter in range(0,abs(x-y)+1):
          print(str(counter) + "this is node")
          #front(0.15)
          forward(2)
          front(0.2)
          print(str(counter) + "counter is this")
    front(0.2)  
    stop()    
    return 1

'''
* Function Name: <Right90>
* Input: <none>
* Output: < none>
* Logic: <Takes a 90 degrees right turn>
* Example Call: <Right90()>
'''   


                    
def Right90():
    RightTurn()
    RightyF(0.6)
    while(1):
        flag=0
        RightTurn()  
        s = serial.Serial("/dev/ttyUSB0",9600) #Establish Serial Communication
        s.baudrate=9600
        t = s.readline() #Readline
        
        val = str(t).strip("b'").strip("\\n").strip("\\r") #Strip Unnecessary Values
        print(val+"Turn")
        print("Taking a Right")  #
        while(val == str(2) or val == str(6)):   #Align if Bot Off
            stop()
            flag=1
            break
        while(val==str(4) or (val == str(5)) ): 
            RightTurn()
            t = s.readline()
            val = str(t).strip("b'").strip("\\n").strip("\\r")
        if(flag==1):
          break
'''
* Function Name: <forw>
* Input: <X: >
* Output: < none>
* Logic: <>
* Example Call: <forw(1)>
'''   

def forw(x): #to follow black line                                  
    while(1):
    
        s = serial.Serial("/dev/ttyUSB0",9600) #Establish Serial Communication
        s.baudrate=9600
      
        t = s.readline() #Readline
        
        val = str(t).strip("b'").strip("\\n").strip("\\r") #Strip Unnecessary Values
        #print(t)
        print(val)  #print value
        
        while(val==str(1) and (time.time() < x)):   #Align if Bot Off
            forwardL()
            t = s.readline()
            
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            #print(t)
            print(val)        
            
            
            
        while(val==str(3)and(time.time() < x)): #Align if Bot Off
            forwardR()
            t = s.readline()
            
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            #print(t)
            print(val)  
    
                   
        while(val==str(2)and (time.time() < x)):   #Move Forward
            ahead()
            t = s.readline()
            
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            #print(t)
            print(val)  
        
        while(val==str(4)and (time.time() < x)):#Stop if Off the Line 
            
            t = s.readline()
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            ahead()
            
        while(val==str(5)and (time.time() < x)):#Stop if Off the Line 
            
            t = s.readline()
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            ahead()
        while(val==str(6)and (time.time() < x)):#Stop if Off the Line 
            
            t = s.readline()
            val = str(t).strip("b'").strip("\\n").strip("\\r")
            ahead()
        
        if(time.time() > x):   #Stop if TimeOut is exceeded 
            print("IN Stop")
            stop()
            print(val)
            break
'''
* Function Name: <Left90>
* Input: <none>
* Output: < none>
* Logic: <Takes a 90 degree left turn>
* Example Call: <Left90()>
'''   

def Left90():
    LeftTurn()
    LeftyF(0.6)

    while(1):
        flag=0
        LeftTurn()
        s = serial.Serial("/dev/ttyUSB0",9600) #Establish Serial Communication
        s.baudrate=9600
      
        t = s.readline() #Readline
        
        val = str(t).strip("b'").strip("\\n").strip("\\r") #Strip Unnecessary Values
        print(val+"In Left Turn")
        print("Taking a Left")  #
        while(val == str(2) or val == str(6)):   #Align if Bot Off
            stop()
            flag=1
            break
        while(val==str(4) or val == str(5) ): 
            LeftTurn()
            t = s.readline()
            val = str(t).strip("b'").strip("\\n").strip("\\r")
        if(flag==1):
          break
'''
* Function Name: <U180>
* Input: <none>
* Output: < none>
* Logic: <Takes a 180 degree Uturn>
* Example Call: <U180()>
'''   
          
def U180():
    Left90()
    Left90()


'''
* Function Name: <stop()>
* Input: <NONE>
* Output: <Stopping both motors >
* Logic: <Setting ForwardR() and ForwardL() pins low>
* Example Call: <stop()>
'''
def stop():  
                                 
  GPIO.output(ForwardR, GPIO.LOW)
  GPIO.output(ForwardL, GPIO.LOW)
  GPIO.output(BackwardR, GPIO.LOW)
  GPIO.output(BackwardL, GPIO.LOW)


#########################################################################MOTOR FUNCTIONS END##########################################################################################
#################################################################MISCELLANEOUS FUNCTIONS#####################################################################
'''
* Function Name: <intialmove()>
* Input: <NONE>
* Output: <None>
* Logic: <first function that gets called in main. It goes to the Arucos one by one and detects them. Then it goes back to SA and detects the SA123 and SA456 one by one.
*It captures images using pi cam and performs shape and color detection.
* Example Call: <initialmove()>
'''

def VideoProcessing():
    # initialize the camera and grab a reference to the raw camera capture
    global camera,stopvideo
    camera.resolution = (640, 480)
    camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=(640, 480))
     
    # allow the camera to warmup
    time.sleep(0.1)
     
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            image = frame.array
            aruco_detect(image)
            # show the frame
            cv2.imshow("Frame", image)
            key = cv2.waitKey(1) & 0xFF
     
            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)
            
            # if the `q` key was pressed, break from the loop
            if(stopvideo == 4):
                  break


shrubdetected = 0


def initialmove():
    
    global shrubdetected,number
    
    front(0.05)
    forward(1)
    front(0.1)
    
    timeout1 = time.time() + 8  
    forw(timeout1)
    
    camera_capture(11)

    
    forward(1)
    front(0.1)
    
    timeout1 = time.time() + 2  
    forw(timeout1)
    
    camera_capture(12)
 

    forward(1)
    front(0.1)
    Left90()

    timeout1 = time.time() + 2  
    forw(timeout1)
    
    camera_capture(13)


    forward(1)
    front(0.2)

    timeout1 = time.time() + 2 
    forw(timeout1)
    
    camera_capture(14)
    forward(1) 
    front(0.3)

    Detect()
    
    
def Detect():
    global SA
    SAPU(6)
    front(0.1)
    Right90()
    Right90()
    shrubcam()
    forward(1)
    front(0.2)
    shrubcam()
    forward(1)
    front(0.2)
    shrubcam()
    forward(1)
    front(0.2)
    shrubcam()
    forward(1)
    front(0.2)
    shrubcam()
    forward(1)
    front(0.2)
    shrubcam()
    forward(1)
    front(0.2)
    Left90()
    Left90()
    forward(1)
    front(0.1)
    forward(1)
    front(0.1)
    forward(1)
    front(0.1)
    Right90()
    print(SA)
    shrubdecode(SA)
    position = 2
        
    
'''
* Function Name: <opp(QAH)>
* Input: <QAH number>
* Output: <opp_QAH >
* Logic: <computes the AH which is opposite to the QAH>
* Example Call: <opp(1)>
'''
def opp(QAH):

    if(QAH==0):
        opp_QAH = 3
    elif(QAH==1):
        opp_QAH = 2
    elif(QAH==2):
        opp_QAH = 1
    elif(QAH==3):
        opp_QAH = 0
    return opp_QAH

## RightPickup = a
## RightDrop = b
## LP = c
## LD = d
## DD = f
## RPLD = g
## RDLP = f

## Servocam = p
## Servocam = q
## Servocam = r
## Servocam = s
## Servocam = t
## Servocam = u
## Servocam = v


######################################################################## ARM MOVEMENT AND COMMUNICATION############################################################
'''
* Function Name: <Communication>
* Input: <ch: character to be sent to Arduino>
* Output: <none>
* Logic: <Sends a character to Arduino which interprets and accordingly moves the servo motors(arm)>
* Example Call: <Communication('a')>
'''

def Communication(ch):

    outgoing_data = ch
    #print("outgoing_data Rpi:" + outgoing_data)    
    time.sleep(2)
    s.write(outgoing_data.encode())
    #print("DATA SENT TO ARDUINO")

'''
* Function Name: <singlepickuppositiondecode>
* Input: <current: AH number >
* Output: <SA_priority[b]: position from where the block must be picked up>
* Logic: <Function to know the position of the block >
* Example Call: <singlepickuppositiondecode(current))>
'''


def Tpickup():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    
    if(SAH[current] == ['S','TT']):
        Tpos = AH[current].index('T')
        SAH[current] == ['D','D']
    
    elif(SAH[previous_current] == ['S','TT']):
        Tpos = AH[previous_current].index('T')
        SAH[previous_current] == ['D','D']
  
    elif(SAH[current] == ['S','T']):
        Tpos = AH[current].index('T')
           
    a = armpickup_decide(Tpos)
    return a


def armpickup_decide(Tpos):
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    flag = 0
    if((Tpos == 0 and arm == 0 and arm2 == 0) ):
        #Trash is at S1 and both arms are free
        Communication(R_Up)
        time.sleep(7)
        #Right arm occupied now
        arm = 1
        
    elif(Tpos == 1 and arm == 0 and arm2 == 0):
        #Trash is at S2 and both arms are free
        Communication(L_Up)
        time.sleep(7)
        #Left arm occupied now
        arm = 2
        
    elif(Tpos == 0 and arm2 == 1):
        #Trash is at S1 and Right arm is occupied ie left arm is free
        if(para != 1):
            U180()
            flag = 1
        Communication(L_Up)
        time.sleep(7)
        arm = 2  #Both arms occupied
        
    elif(Tpos == 0 and arm2 == 2):
        #Trash is at S1 and Left arm is occupied ie right arm is free
        ############
        if(para == 1):
            U180()
            #Left90()
            flag = 1
        Communication(R_Up)
        time.sleep(7)
        arm = 1 #Both arms occupied
        
    elif(Tpos == 1 and arm2 == 1):
        #########
        if(para == 1):
            U180()
            #Left90()
            flag = 1
        #Trash is at S2 and right arm is occupied ie left arm is free
        Communication(L_Up)
        time.sleep(7)
        #print("Expected tpos and arm")
        arm = 2
        
    elif(Tpos == 1 and arm2 == 2):
        #Trash is at S2 and left arm is occupied ie right arm is free
        if(para != 1):
            U180()
            flag = 1
        Communication(R_Up)
        time.sleep(7)
        arm == 1
    
    else:
      c = arm
      arm = arm2 
      arm2 = c
      armpickup_decide(not(Tpos))
       
    return flag


SA =          ['L','L','W','W','H','H']
SA_priority = ['3','4','2','5','1','6']

def singlepickuppositiondecode():
    global SA,position ,previous_current,current,spos1,spos2,arm ,para,arm2,SA
    a = AH_intermediate[current].index('S')
    print(a)
    try:
        b=SA.index(AH[current][a])
    except:
         b = SA.index('X')
    SA[SA.index(AH[current][a])] = 'Y'
    print(AH_intermediate)
    #AH_intermediate[current][a] = 'X'
    return int(SA_priority[b])

def SSpickup():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2,SA,knowledge
    try:
        b=SA.index(AH[current][0])
    except:
        b = SA.index('X')
    z = b
    SA[SA.index(AH[current][0])] = 'Y'
    knowledge = 1 
    print(AH_intermediate)
    return int(SA_priority[z])
    

def doublepickuppositiondecode(variable):
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2,SA,knowledge
    if(variable == 1):
        a = AH_intermediate[current].index('S')
        try:
            b = [i for i, x in enumerate(SA) if x == AH[current][a]]
        except:
            b = SA.index('X')
            
    
    if(variable == 2):
        try:
            b = [i for i, x in enumerate(SA) if x == AH[current][knowledge]]
        except:
            b = SA.index('X')
    print(b)
    print(SA_priority[1])
    
    #b = SA.index(AH[current][a])
    if(len(b)==1):
        SA[int(b[0])] = 'Y'
        return int(SA_priority[b[0]])
    
    elif(len(b)==2):
        
        if((spos1 == 1) or (spos1 == 6) or (spos1 == 2) or (spos1 == 5)):
            
            
            print("Spos1 is " + str(spos1))
            
            if(abs(spos1 - int(SA_priority[b[0]])) < abs(spos1 - int(SA_priority[b[1]]))):
                SA[int(b[0])] = 'Y'
                return int(SA_priority[b[0]])
            elif(abs(spos1 - int(SA_priority[b[1]])) < abs(spos1 - int(SA_priority[b[0]]))):
                SA[int(b[1])] = 'Y'
                return int(SA_priority[b[1]])
            elif(abs(spos1 - int(SA_priority[b[1]])) == abs(spos1 - int(SA_priority[b[0]]))):
                if(spos1 == 2):
                    SA[SA_priority.index('1')] = 'Y'
                    return 1
                
                elif(spos1 == 5):
                    SA[SA_priority.index('6')] = 'Y'
                    return 6
                
        elif(spos1 == 3 or spos1 == 4):
            if(spos1 == 3):
                if(int(SA_priority[b[0]]) == 2 or int(SA_priority[b[1]]) == 2):
                    
                    SA[SA_priority.index('2')] = 'Y'
                    return 2
                
                elif(int((SA_priority[b[0]]) == 1) or (int(SA_priority[b[1]]) == 1)):
                    SA[SA_priority.index('2')] = 'Y'
                    return 1
                else:
                    if(abs(spos1 - int(SA_priority[b[0]])) < abs(spos1 - int(SA_priority[b[1]]))):
                        SA[int(b[0])] = 'Y'
                        return int(SA_priority[b[0]])
                                   
                    elif(abs(spos1 - SA_priority[b[1]]) < abs(spos1 - SA_priority[b[0]])):
                        SA[int(b[1])] = 'Y'
                        return int(SA_priority[b[1]])
            if(spos1 == 4):
                if(int(SA_priority[b[0]] == 5) or (int(SA_priority[b[1]]) == 5)):
                    SA[SA_priority.index('5')] = 'Y'
                    return 5
                elif((int(SA_priority[b[0]] == 6) or (int(SA_priority[b[1]]) == 6))):
                    SA[SA_priority.index('6')] = 'Y'
                    return 6
                else:
                    if(abs(spos1 - int(SA_priority[b[0]])) < abs(spos1 - int(SA_priority[b[1]]))):
                        SA[int(b[0])] = 'Y'
                        return int(SA_priority[b[0]])
                    elif(abs(spos1 - int(SA_priority[b[1]])) < abs(spos1 - int(SA_priority[b[0]]))):
                        SA[int(b[1])] = 'Y'
                        return int(SA_priority[b[1]])                     
'''
* Function Name: <drop>
* Input: <a_indicator:a_indicator indicates which arm the block is picked up in , current:AH number>
* Output: <turn: indicates whether the AB has to take a turn and drop the shrub or without turn>
* Logic: <dropping the shrub in the AH depending on its service location >
* Example Call: <drop(1,2)>
'''

increment2 = 0
def simultaneous():
    #print("Simultaneous")
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2,increment2
    turn = 0
    x = current
    #print("hi")
    #print(x)
    #print(position)
    #print(increment2)
    
    if(position == 1 or position == 2):
      x = current

    if((position == 3 or position == 4)): 
      increment2 = increment2 + 1
      
    if((position == 3 or position == 4) and (increment2%2 == 1)):
      x = previous_current
      
    #print("hi")
    #print(x) 
    #print(position)
    #print(increment2)
     
    droppos = AH_intermediate[x].index('S')
    
    if(arm == 1 or arm2 ==1):
        #Right arm is occupied
        #We need to drop shrub
        if(droppos == 0):
            #We need to drop shrub at S1
            Communication("h") #R_Down,L_Up RP,LD = g & RD,LP = h
            time.sleep(7)
        elif(droppos == 1):
            #Drop at S2
            U180()
            turn = 1
            Communication("h")
            time.sleep(7)
        arm = 2
        arm2 = 0
        
    elif(arm == 2 or arm2 == 2):
        #Left arm is occupied
        #We need to drop shrub
        if(droppos == 0):
            #We need to drop shrub at S0
            U180()
            turn = 1
            Communication("g")
            time.sleep(7)
        elif(droppos == 1):
            Communication("g")
            time.sleep(7)   
        arm = 1
        arm2 = 0
    
    return turn 
        
    
increment = 0

def drop(armcheck):
    
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2,increment
    left = 2
    right = 1
    turn = 0
    x = current
    if(position == 1 or position == 2):
      x = current

    if((position == 3 or position == 4)): 
      increment = increment + 1
      
    if((position == 3 or position == 4) and (increment%2 == 1)):
      x = previous_current
    
    if(armcheck == left and AH_intermediate[x].index('S') == 0):
        #Drop the left arm
        U180()
        turn = 1
        Communication(L_Down)
        time.sleep(7)
        
    elif(armcheck == left and AH_intermediate[x].index('S') == 1):
        #Drop the left arm
        Communication(L_Down)
        time.sleep(7)
        
    elif(armcheck == right and AH_intermediate[x].index('S') == 0):
        #Drop the right arm
        Communication(R_Down)
        time.sleep(7)
        
    elif(armcheck == right and AH_intermediate[x].index('S') == 1):
        #Drop the right arm
        U180()
        turn = 1
        Communication(R_Down)
        time.sleep(7)

    if(armcheck == arm):
        arm = arm2
        arm2 = 0

    if(armcheck == arm2):
        arm2 = 0
          
    return turn

def doubledrop():
    
    if(spos1 == 1 or spos1 == 2 or spos1 == 3):
        Communication("f")
        time.sleep(7)
        arm = arm2 = 0
        return 0
    
    else:
        U180()
        Communication("f")
        time.sleep(7)
        arm = arm2 = 0
        return 1
    
'''
* Function Name: <armorient1()>
* Input: <spos1>
* Output: <arm: the arm in which the shrub is picked up>
* Logic: <this function denotes using which arm the shrub1 should be picked up>
* Example Call: <armorient1(spos)>
'''

def armorient1():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2 
    if((spos1 == 1) or (spos1 == 2) or (spos1 == 3)):
        arm = 1 #right arm is occupied now
        #send data to arduino for right arm
        Communication(R_Up)
        print("Right arm pick up 1.Communication('a')")
    if (spos1 == 4 or spos1 == 5 or spos1 == 6):
        arm = 2 #left arm is occupied now
        #send data to arduino for left arm
        Communication(L_Up)
        print("Left Arm se uthaya")
    return arm
'''
* Function Name: <armorient2()>
* Input: <spos1,spos2,arm>
* Output: <darm = 3 denotes double arm service is done>
* Logic: <this function denotes using which arm the shrub2 should be picked up, when there's already a shrub in the other hand>
* Example Call: <armorient2(3,1,2)>
'''

def armorient2():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2 
    #print("In Arm orient2")

    if(arm == 1):
       arm2 = 2 
    if(arm == 2):
       arm2 = 1
    
    #call After double pickup ie after STravel
    if(((spos1 == 3) and ((spos2==1) or (spos2==2)) or ((spos1 == 2) and ((spos2==1))))):
       #right arm is occupied now, actually both now
       #send data to arduino for right arm
       Communication(L_Up)
       #print("Right arm is occupied.Left pick up 2. Communication('a')")
    elif(((spos1 == 4) and ((spos2==5) or (spos2==6)) or ((spos1 == 5) and ((spos2==6))))):
        #left arm is occupied now, actually both now
        #send data to arduino for left arm
        Communication(R_Up)
        #print("Left arm is occupied.right pick up 2.Communication('b')")
        
    else:
        #This can directly pickup from the available arm
        if(arm2 == 2):
         #Arm 1 signifies right arm is occupied
         Communication(L_Up)
         #print("left arm pickup 2.Communication('b')")
         
        elif(arm2 == 1):
         #Arm 2 signifies left arm is occupied
         Communication(R_Up)
         #print("right arm pickup 2. Communication('a')")
        

def endget():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2 
    
    if(position == 3 or position == 4):
        orient(arm,spos1)
        PUCN(spos1)
        print("PUCN(y)")
        CNAH(current)
        print("CNAH(current)")
        if(position == 3 or arm2 != 0):
            z1 = para = drop(arm)
            z2 = 0
            position = 1 
            if(position == 4):
              glowLED_YELLOW()
              z2 = para = Tpickup()
              if(z1+z2 == 2):
                 U180()
              if(z1+z2 == 1):
                 para = 1

        else: para = simultaneous()
        
        TrashAccum()
        position = 2
          
        prev_current = current
        SAH[current] = ['D','D']
    if(position == 1):
        AHSA(previous_current,para)
        
    forward(1)
    data = "z"
    s.write(data.encode())
        
def SS():
    
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    if(position == 1):
        AHSA(previous_current,para)
        
    if(position == 3 or position == 4):
       orient(arm,spos1)
       PUCN(spos1)
       CNAH(previous_current)
       if(position == 3 or arm2 != 0):
           z1=para = drop(arm)
           z2 = 0
           if(position == 4):
              glowLED_YELLOW()
              z2 = para = Tpickup()
              if(z1+z2 == 2):
                 U180()
              if(z1+z2 == 1):
                 para = 1
       else: para = simultaneous()      
       AHSA(previous_current,para)
        
    if(position == 1 or position == 2 or position == 3 or position ==4):
        
        x = SSpickup()
        print('x')
        print(x)
        if(SAPU(x)):
            spos1 = x
            arm = armorient1()
            time.sleep(7)
        
        spos2 = doublepickuppositiondecode(2) 
        
        print('spos2')
        print(spos2)    
        if(STravel(spos1,spos2)):
            orient2()
            armorient2()
            time.sleep(7)
            
        orient(arm2,spos2)
        PUCN(spos2)
        CNAH(current)
        para = doubledrop()
        position = 1        
        previous_current = current
        SAH[current] = ['D','D']

def ST():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
        
    if(position == 1):
        AHSA(previous_current,para)
        
    if(position == 1 or position == 2):
        x = singlepickuppositiondecode()
        if(SAPU(x)):
          spos1 = x
          arm = armorient1()
          time.sleep(7)
          position = 4
          SAH[current] = ['S','TT']    

    elif(position == 3 or position == 4):
    
          spos2 = doublepickuppositiondecode(1) 
          if(STravel(spos1,spos2)):
            orient2()
            armorient2()
            time.sleep(7)
          orient(arm2,spos2)
          PUCN(spos2)
          CNAH(previous_current)
          print("check")
          print(position)
          print(arm)
          print(arm2)
          
          if(position == 3 or arm2 != 0 ):
              z1 = para = drop(arm)    
              z2 = 0
              '''
              if(position == 4):
                 glowLED_YELLOW()
                 z2 = para = Tpickup()
              if(z1+z2 == 2):
                 U180() 
              if(z1+z2 == 1):
                 para = 1
              '''
          else: simultaneous()  

          if(arm2 != 0 ):
              AHAH(previous_current,current,para)
              para = z1 = drop(arm)
              glowLED_YELLOW()
              position = 1
              para = z2 = Tpickup() 
              if(z1+z2 == 2):
                 U180()
              if(z1+z2 == 1):
                 para = 1
          else:
              AHAH(previous_current,current,para)
              para = simultaneous()  
          
          position = 1
          SAH[current] = ['D','D']      
    previous_current = current

def SX():
   
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    if(position == 1):
        AHSA(previous_current,para)
        
    if(position == 1 or position==2):
        x = singlepickuppositiondecode()
        print(str(x) + "value of x" )
        if(SAPU(x)):
            spos1 = x
            arm = armorient1()    
            time.sleep(7)
    
        position = 3
        ##end: SAPU
        
    elif(position== 3 or position == 4):
      spos2 = doublepickuppositiondecode(1) 
      if(STravel(spos1,spos2)):
        orient2()
        armorient2()
        time.sleep(7)
      orient(arm2,spos2)
      PUCN(spos2)
      CNAH(previous_current)
      
      if(position == 3 or arm2 != 0):
          z1 = para = drop(arm)
          z2 = 0
          if(position == 4):
              glowLED_YELLOW()
              z2 = para = Tpickup()
              if(z1+z2 == 2):
                 U180()
              if(z1+z2 == 1):
                 para = 1
      else: para = simultaneous()        
      AHAH(previous_current,current,para)
      para = drop(arm) #should be drop(arm)
      position = 1
      ##end: opposite
    
    SAH[current] = ['D','D']
    previous_current = current
          
def QueenTrash():
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    U180()
    forward(1)
    front(0.35)
    CNAH(QAH)
    glowLED_YELLOW()
    para = Tpickup()
    if(AHTDZ(current,para)):
        DoubleTrashDrop()
        TDZSA()
        position = 2
    
def TT():
      global position ,previous_current,current,spos1,spos2,arm ,para,arm2
      print("TT")
      print(position)
      if(position == 3 or position == 4):
           orient(arm,spos1)
           PUCN(spos1)
           CNAH(previous_current)
      
      if(positon != 1 ):
        if((position == 3 or arm2 != 0)):
            z1 = para = drop(arm)
            z2 = 0
            if(position == 4):
               glowLED_YELLOW()
               z2 = para = Tpickup()
            if(z1+z2 == 2):
               U180()
            if(z1+z2 == 1):
               para = 1
        else: para = simultaneous()
            
      if(position == 1 or position == 3 or position == 4):
        if(AHAH(previous_current,current,para)):
            x = 2
            
      if(position == 1 or position == 3 or position == 4 or position == 5):
        
          if(trashdetect):
              trashflag = 0
          else:
              trashflag = 1
              
          if(trashflag == 0):
             glowLED_YELLOW()
        
          else:
             glowLED_YELLOW()
          
          front(0.2)
          stop()
          para = armpickup_decide(trashflag) 
          time.sleep(7)
          position = 1

def TrashAccum():
    serveshrub = 0
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2,shrubdetected 
    if(['S','T'] in SAH):
        current = SAH.index(['S','T'])
        if(position == 1):
            AHAH(previous_current ,current ,para)
            serveshrub = 1
            glowLED_YELLOW()
            para = Tpickup()
        elif(position == 3 or position ==4):
            ST()
            
    if(['S','TT'] in SAH):
        current = SAH.index(['S','TT'])
        if(position == 1):
            AHAH(previous_current ,current ,para)
            glowLED_YELLOW()
            para = Tpickup()
            para = not(para)
            
        elif(position == 3 or position ==4):
           orient(arm,spos1)
           PUCN(spos1)
           CNAH(current)
           
           if(position == 3 or arm2 != 0):
               z1=para = drop(arm)
               z2 = 0
               if(position == 4):
                  glowLED_YELLOW()
                  z2 = para = Tpickup()
                  if(z1+z2 == 2):
                     U180()
                  if(z1+z2 == 1):
                     para = 1
           else: para = simultaneous()
        previous_current = current
        position = 1

    
    if(['T','T'] in SAH):
        current = SAH.index(['T','T'])
        TT()
          
    if(AHTDZ(current,para)):
        DoubleTrashDrop()
        SAH[current] = ['D','D']
        TDZSA()
        position = 2
        
    if(serveshrub == 1):
        x = singlepickuppositiondecode()
        if(SAPU(x)):
          spos1 = x
          arm = armorient1()
          if(arm == 1):
            arm2 = 2
          if(arm == 2):
            arm2 = 1   
          time.sleep(7)
          position = 3
        
    previous_current = current
    trash = 1
 
def orient(a_indicator,spos):
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    if((spos == 1 or spos == 2 or spos == 3 ) and ( a_indicator == 1)):
        Left90()
        Left90()
        stop()
    if((spos == 4 or spos == 5 or spos == 6 ) and ( a_indicator == 2)):
        Right90()
        Right90()
        stop()      
    else:
        stop()
        
def orient2():
    
  global position ,previous_current,current,spos1,spos2,arm ,para,arm2
  if(spos1 in range(1,4) and spos2 in range(1,4) and (spos1 > spos2)):
     Left90()
     Left90()
  elif(spos1 in range(4,7) and spos2 in range(4,7) and (spos1 < spos2) ):
     Right90()
     Right90()
    

def algoss():
        global position ,previous_current,current,spos1,spos2,arm ,para,arm2
        previous_current = QAH
        shrub = 0

        
        if(SAH[1]==['T','T']):
            current = opposite
            TT()
            TrashAccum()
            
        algotxxx()

def algotxxx():
    #position 1 is AH
    #position 2 is SA
    #position 3 is SAPU
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2
    
    if (['S','S'] in SAH):
            current = SAH.index(['S','S'])
            SS()
            if(SAH[opp(previous_current)]==['T','T']):  
                current = opp(previous_current)
                TT()
                TrashAccum()
             
    if (['S','S'] in SAH):
            current = SAH.index(['S','S'])
            SS()

            if(SAH[opp(previous_current)]==['T','T']):  
                current = opp(previous_current)
                TT()
                TrashAccum()
                
    if (['S','S'] in SAH):
        current = SAH.index(['S','S'])
        SS()
          
    if(['S','X'] in SAH):
        current = SAH.index(['S','X'])
        SX()

    if(['S','X'] in SAH):
        current = SAH.index(['S','X'])
        SX()

    if(['S','X'] in SAH):
        current = SAH.index(['S','X'])
        SX()
            
    if(['S','T'] in SAH):
        current = SAH.index(['S','T'])
        ST()
        TrashAccum()
    
    if(['T','T'] in SAH):
        current = SAH.index(['T','T'])
        TT()
        TrashAccum()
                

def algostsx():
        global position ,previous_current,current,spos1,spos2,arm ,para,arm2 , QAH
        previous_current = int(QAH)
        opposite = opp(int(QAH))
        
        if(SAH[opposite]==['S','X']):
            current = opposite
            SX()
        
        if(SAH[opposite]==['S','T']):
            current = opposite
            ST()
            TrashAccum()
            
        if(['S','X'] in SAH):
            current = SAH.index(['S','X'])
            SX()

        if(['S','T'] in SAH):
            current = SAH.index(['S','T'])
            ST()
            TrashAccum()
            
        if(SAH[opposite] == ['T','T']):
          current = opposite
          TT()
          TrashAccum()
                
        if(['S','S'] in SAH):
            current = SAH.index(['S','S'])
            SS()


        if(['S','S'] in SAH):
            current = SAH.index(['S','S'])
            SS()

            
        if(['S','S'] in SAH):
            current = SAH.index(['S','S'])
            SS()
                
        if(['T','T'] in SAH):
            current = SAH.index(['T','T'])  
            TT()
            TrashAccum()
            
           
if __name__ == "__main__":
    global position ,previous_current,current,spos1,spos2,arm ,para,arm2 , QAH
    
    s = serial.Serial('/dev/ttyUSB0', 9600)


    decode(210)
    decode(32)
    decode(17)
    decode(120)
    position = 2
    LEDSetup()
    time.sleep(2)
    #initialmove()
    
    Communication("m")
    time.sleep(3)
    
    if(AH[4][0]=="-1"):
        algotxxx()           
       
    elif ((SAH[int(QAH)])== ['S','S']):
        current = int(QAH)
        previous_current = current
        SS()
        algoss()

    elif((SAH[int(QAH)]) == ['S','T']):
        current = int(QAH)
        previous_current = current
        QueenTrash()
        SX()              ### Trash is served therefore SX 
        algostsx()
  
    elif((SAH[int(QAH)]) == ['S','X']):
        current = int(QAH)
        previous_current = current
        SX()
        algostsx()

    elif((SAH[int(QAH)]) == ['T','T']):
        current = int(QAH)
        previous_current = current
        U180()
        forward(1)
        front(0.1)
        CNAH(QAH)
        position = 5
        TT()
        TrashAccum()
        if(position == 3 or position == 4):
            algostsx()
        else: algotxxx()
        
    elif((SAH[int(QAH)]) == ['X','X']):
        algotxxx()
        
    endget()
    
