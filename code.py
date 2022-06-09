#!/usr/bin/env python3
import threading
import time

# Convert to Executable:
# "sed -i 's/\r//g' <file>"

# Import EV3DEV
from ev3dev2.button import *
from ev3dev2.console import *
from ev3dev2.display import *
from ev3dev2.fonts import *
from ev3dev2.led import *
from ev3dev2.motor import *
from ev3dev2.port import *
from ev3dev2.power import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.sound import *
print("ev3dev imported")

# Import Utils
from utils import *
print("utils imported")

# Initialize Bluetooth Connection
# https://www.inf.ed.ac.uk/teaching/courses/sdp/SDP2018/sdp_ev3.pdf

# Global Variables
global var1
global var2
global var3
global var4
global oldDistance
global newDistance
global currentAngle
global frontVal
global backVal
global centerStrength
global frontProximity
global backProximity
global ended

# Customization
robotSize = 180    # Diameter (mm)
compensation = 2   # Forward Angle Leeway (degrees)
centerValue = 80   # Distance from Center where still considered Center (mm)
tickrate = 30      # Tickrate (ONLY FOR EV3 SIM)
fieldSize = 600    # Field Width in MM (1800 MM Standard)

# Variables
centerAngle = 0    # Goal Angles
currentAngle = 0   # Current Angle
oldDistance = [0]  # Previous Wall Distances (5)
newDistance = 0    # Current Wall Distance

# Field Size
centerDistance = (fieldSize-robotSize)/2;

# Movement Variables
var1 = 0   # Direction
var2 = 40  # Speed (%)
var3 = 0   # Left Curve
var4 = 0   # Right Curve

run = False
ended = False

# Initialize Motors
topLeft = LargeMotor(OUTPUT_C)
topRight = LargeMotor(OUTPUT_A)
bottomLeft = LargeMotor(OUTPUT_D)
bottomRight = LargeMotor(OUTPUT_B)

# Initialize Sensors
irFront = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
irBack = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")
compass = Sensor(INPUT_3, driver_name = "ht-nxt-compass")
ultrasonic = UltrasonicSensor(INPUT_4)

# Initialize Brick Functions
#sound = Sound()
buttons = Button()
screen = Display()
leds = Leds()

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"
compass.mode = "COMPASS"
ultrasonic.mode = "US-DIST-CM"

# Get Screen Size
width = screen.xres
height = screen.yres

# Change Lighting/Sound
def brickMode(mode):
    if mode == 'Running':
        leds.set_color('LEFT', 'GREEN')
        leds.set_color('RIGHT', 'GREEN')
        #sound(700,0.5,play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
    elif mode == 'Paused':
        leds.set_color('LEFT', 'AMBER')
        leds.set_color('RIGHT', 'AMBER')
        #sound(500,0.5,play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
    elif mode == 'Reset':
        leds.set_color('LEFT', 'GREEN')
        leds.set_color('RIGHT', 'GREEN')

# Create 8-Direction Movement + Turning
def direct(direction,speed,leftDrift,rightDrift):
    if (direction == 0):
        # Stop Motors
        topRight.stop()
        bottomRight.stop()
        topLeft.stop()
        bottomLeft.stop()
    if (direction == 1):
        # Top Left
        topRight.on(SpeedPercent((speed*-1)+leftDrift))
        bottomRight.on(SpeedPercent(0+leftDrift))
        topLeft.on(SpeedPercent(0+rightDrift))
        bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 2):
        # Forward
        topRight.on(SpeedPercent((speed*-1)+leftDrift))
        bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
        topLeft.on(SpeedPercent((speed*1)+rightDrift))
        bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 3):
        # Top Right
	    topRight.on(SpeedPercent(0+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent(0+rightDrift))
    if (direction == 4):
        # Right
	    topRight.on(SpeedPercent((speed*1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 5):
        # Bottom Right
	    topRight.on(SpeedPercent((speed*1)+leftDrift))
	    bottomRight.on(SpeedPercent(0+leftDrift))
	    topLeft.on(SpeedPercent(0+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 6):
        # Backwards
	    topRight.on(SpeedPercent((speed*1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 7):
        # Bottom Left
	    topRight.on(SpeedPercent(0+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent(0+rightDrift))
    if (direction == 8):
        # Left
	    topRight.on(SpeedPercent((speed*-1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 9):
        # Spin Right
	    topRight.on(SpeedPercent((speed*1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 10):
        # Spin Left
        topRight.on(SpeedPercent((speed*-1)+leftDrift))
        bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
        topLeft.on(SpeedPercent((speed*-1)+rightDrift))
        bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 11):
        # Coast Motors
        topRight.off(brake=False)
        bottomRight.off(brake=False)
        topLeft.off(brake=False)
        bottomLeft.off(brake=False)

# Straighten Robot Angle
def turnStraight():
    global var1
    global var2
    global var3
    global var4

    global currentAngle

    if compensation < currentAngle < 181:
        # Calculate Acceleration
        accel = 7 + (round((currentAngle+compensation)/15))

        # Turn Right
        var3 = accel
        var4 = accel
    elif (360 - compensation) > currentAngle > 180:
        # Calculate Acceleration
        accel = 20 - (round((currentAngle+compensation)/30))

        # Turn Left
        var3 = accel * -1
        var4 = accel * -1
    else:
        # Aiming Straight
        var3 = 0
        var4 = 0

# Curve Towards Goal
def curve():
    global var1
    global var2
    global var3
    global var4

    global newDistance

    if robotNotBlocking(oldDistance[0], newDistance):
        if newDistance > (centerDistance + centerValue):
            var2 = 90
            var3 = -4
            var4 = -2
        elif newDistance < (centerDistance - centerValue):
            var2 = 90
            var3 = 2
            var4 = 4
        else:
            var3 = 0
            var4 = 0
            turnStraight()
    else:
        var3 = 0
        var4 = 0

# Robot Moves to Center of Field
def centerRobot():
    global var1
    global var2
    global var3
    global var4

    global newDistance

    turnStraight()

    if robotNotBlocking(oldDistance[0],newDistance):
        if newDistance > (centerDistance + 12):
            var1 = 4
        elif newDistance < (centerDistance - 12):
            var1 = 8
        else:
            if not topLeft.is_stalled:
                var1 = 6
                var2 = 10
            else:
                var1 = 0
                var2 = 0
    else:
        if not topLeft.is_stalled:
            var1 = 6
            var2 = 10
        else:
            var1 = 0
            var2 = 0
       
# Find Ball Position
def goToBall():
    global var1
    global var2
    global var3
    global var4

    global frontVal
    global backVal

    global frontProximity
    global backProximity

    if (frontProximity > backProximity) and (frontVal != 0):
        if 4 < frontVal < 6:    # Directly In-Front
            var1 = 2
        if 3 < frontVal < 5:    # Top Left
            if (frontProximity > 100): # Ball is Close
               var1 = 1
            else:
               var1 = 8
        if 5 < frontVal < 7:    # Top Right
            if (frontProximity > 100): # Ball is Close
               var1 = 3
            else:
               var1 = 4
        elif 2 < frontVal < 4:  # Left Side
            if (frontProximity > 130):
                var1 = 7
            else:
                var1 = 8
        elif 0 < frontVal < 3:  # Back Left
            var1 = 6
        elif 6 < frontVal < 8:  # Right Side
            if (frontProximity > 130):
                var1 = 5
            else:
                var1 = 4
        elif 7 < frontVal < 10: # Back Right
            var1 = 6
    elif (backVal != 0):
        if 3 < backVal < 7:     # Directly Behind
            if backProximity > 110: # Ball is Close
                if newDistance > (centerDistance + centerValue):
                    var1 = 4
                else:
                    var1 = 8
            else:
                var1 = 6
        elif 0 < backVal < 4:   # Back Right 
            if backProximity > 110: # Ball is Close
                var1 = 7
            else:
                var1 = 6
        elif 6 < backVal < 10:   # Back Left 
            if backProximity > 110: # Ball is Close
                var1 = 5
            else:
                var1 = 6
    else:                       # Can't Find Ball
        var1=0
        #centerRobot()

# Thread for Sensor Values
def updateSensors():
    global oldDistance
    global newDistance
    global currentAngle
    global frontVal
    global backVal
    global centerStrength
    global frontProximity
    global backProximity
    global ended

    print("Updating Sensors!")

    while not ended:
        # Update Variables
        oldDistance.append(newDistance)
        if len(oldDistance) > 10:
            oldDistance.pop(0)
        newDistance = ultrasonic.value(0)
        currentAngle = getAngle(compass.value(0), centerAngle)
        frontVal = irFront.value(0)
        frontProximity = max([irFront.value(1),irFront.value(2),irFront.value(3),irFront.value(4),irFront.value(5)])
        backProximity = max([irBack.value(1),irBack.value(2),irBack.value(3),irBack.value(4),irBack.value(5)])
        backVal = irBack.value(0)
        centerStrength = irFront.value(3)
       
# Thread for Display
def updateScreen():
    global var1
    global var2
    global oldDistance
    global newDistance
    global currentAngle
    global frontVal
    global backVal
    global centerStrength
    global ended

    print("Updating Screen!")

    # Font Variables
    fontsize = 12

    # Screen Cennter Position
    centerX = int(width)/2
    centerY = int(height)/2

    while not ended:
        # Update UI
        screen.clear()
        screen.text_pixels("Direction: " + str(var1),False,0,0,'Blue',load('helvB12'))
        screen.text_pixels("Motor Speed: " + str(var2),False,0,fontsize,'Blue',load('helvB12'))
        screen.text_pixels("IR Values: " + str(frontVal) + "," + str(backVal),False,0,fontsize*2,'Blue',load('helvB12'))
        screen.text_pixels("IR Proximity: " + str(centerStrength),False,0,fontsize*3,'Blue',load('helvB12'))
        screen.text_pixels("CurrentAngle: " + str(currentAngle),False,0,fontsize*4,'Blue',load('helvB12'))
        screen.text_pixels("CenterAngle: " + str(centerAngle),False,0,fontsize*5,'Blue',load('helvB12'))
        screen.text_pixels("WallDistance: " + str(newDistance),False,0,fontsize*6,'Blue',load('helvB12'))
        screen.text_pixels("OldDistances:",False,0,fontsize*7,'Blue',load('helvB12'))
        screen.text_pixels(str(oldDistance),False,0,fontsize*8,'Blue',load('helvB12'))
        
        if run == False:
            # If Paused
            screen.text_pixels("Paused",False,0,fontsize*9,'Blue',load('helvBO24'))

        # Update Screen every 100 ms
        screen.update()
        time.sleep(0.1)

# Reset Values
centerAngle = compass.value(0)
topLeft.reset()
topRight.reset()
bottomLeft.reset()
bottomRight.reset()
leds.reset()

# Run Program
run = False
ended = False
leds.set_color('LEFT', 'RED')
leds.set_color('RIGHT', 'RED')

# Start Sensor Thread
updateValues=threading.Thread(target=updateSensors)
updateValues.start()

# Start Screen Thread
updateDisplay=threading.Thread(target=updateScreen)
updateDisplay.start()

print("Ready!")

try:
    # Main Loop
    while True:
        # Close Program
        if buttons.backspace:
            # Coast Motors and Stop Thread
            print("Exiting...")
            direct(11,0,0,0)
            ended = True
            brickMode('Reset')
            time.sleep(0.1)
            break

        # Pause Button Pressed
        if buttons.left:
            if run == True:
                run = False
                brickMode('Paused')
                print("Paused")
            else:
                run = True
                brickMode('Running')
                print("Started")
            direct(11,0,0,0)
            while buttons.left:
                time.sleep(0.01)   

        # If Program is Not Paused
        if run == True:              
            # Run Functions
            if ballPossesion(centerStrength):
                var2 = 80
                #curve()
                var3 = 0
                var4 = 0
                turnStraight()
            else:
                # Neutral Speed
                var2 = 50
                turnStraight()

            # Chase Ball
            goToBall()
        
            direct(var1,var2,var3,var4)
        # If Paused
        else:
            # Coast Motors
            direct(11,0,0,0)
except:
    ended=False
    direct(11,0,0,0)
    time.sleep(0.1)