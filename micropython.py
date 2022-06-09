#!/usr/bin/env pybricks-micropython
import threading
import time

# Convert to Executable:
# "sed -i 's/\r//g' <file>"

# Import EV3DEV
from ev3dev2.button import *
from ev3dev2.console import *
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
global state
global bluetoothWorking

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
sound = Sound()
buttons = Button()
leds = Leds()

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"
compass.mode = "COMPASS"
ultrasonic.mode = "US-DIST-CM"

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
        topRight.on(SpeedPercent((speed*1)+leftDrift))
        bottomRight.on(SpeedPercent(0+leftDrift))
        topLeft.on(SpeedPercent(0+rightDrift))
        bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 2):
        # Forward
        topRight.on(SpeedPercent((speed*1)+leftDrift))
        bottomRight.on(SpeedPercent((speed*1)+leftDrift))
        topLeft.on(SpeedPercent((speed*-1)+rightDrift))
        bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 3):
        # Top Right
	    topRight.on(SpeedPercent(0+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent(0+rightDrift))
    if (direction == 4):
        # Right
	    topRight.on(SpeedPercent((speed*-1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 5):
        # Bottom Right
	    topRight.on(SpeedPercent((speed*-1)+leftDrift))
	    bottomRight.on(SpeedPercent(0+leftDrift))
	    topLeft.on(SpeedPercent(0+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 6):
        # Backwards
	    topRight.on(SpeedPercent((speed*-1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
    if (direction == 7):
        # Bottom Left
	    topRight.on(SpeedPercent(0+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent(0+rightDrift))
    if (direction == 8):
        # Left
	    topRight.on(SpeedPercent((speed*1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 9):
        # Spin Right
	    topRight.on(SpeedPercent((speed*-1)+leftDrift))
	    bottomRight.on(SpeedPercent((speed*-1)+leftDrift))
	    topLeft.on(SpeedPercent((speed*-1)+rightDrift))
	    bottomLeft.on(SpeedPercent((speed*-1)+rightDrift))
    if (direction == 10):
        # Spin Left
        topRight.on(SpeedPercent((speed*1)+leftDrift))
        bottomRight.on(SpeedPercent((speed*1)+leftDrift))
        topLeft.on(SpeedPercent((speed*1)+rightDrift))
        bottomLeft.on(SpeedPercent((speed*1)+rightDrift))
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
        elif 2 < backVal < 4:   # Back Right 
            if backProximity > 110: # Ball is Close
                var1 = 7
            else:
                var1 = 6
        elif 2 < backVal < 4:   # Back Left 
            if backProximity > 110: # Ball is Close
                var1 = 5
            else:
                var1 = 6
    else:                       # Can't Find Ball
        centerRobot()

# Play Defence and Stay in Goal
def goalie():
    pass

# Thread for Bluetooth Communication
def bluetooth(brickType):
    global frontVal
    global backVal
    global state
    global centerStrength
    global bluetoothWorking

    bluetoothWorking = False

    try:
        if brickType == 'client':
            brick = BluetoothMailboxServer()
            brick.wait_for_connection()
        elif brickType == 'server':
            brick = BluetoothMailboxClient()
            brick.connect('ev3dev')

        bluetoothWorking = True

        robot1 = NumericMailbox('ROBOT1', brick)
        robot2 = NumericMailbox('ROBOT2', brick)

        while not ended:
            # Read Teammate State
            teammate = robot2.read()

            # Get Current Robot State
            if ballPossesion(centerStrength):
                state = 1 # Has Ball
            elif teammate == 1:
                state = 2 # Teammate has Ball
            elif frontVal != 0 and backVal != 0:
                state = 3 # Neither have Ball
            else:
                state = 0 # Cant Find Ball 

            # Update State
            robot1.send(state)

        brick.close()
    except:
        print("Could not connect Bluetooth")
        bluetoothWorking = False    

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

# Start Bluetooth Thread
bluetoothComms=threading.Thread(target=bluetooth('client'))
#bluetoothComms=threading.Thread(target=bluetooth('server'))
bluetoothComms.start()

# Start Sensor Thread
updateValues=threading.Thread(target=updateSensors)
updateValues.start()

print("Ready!")

# Main Loop
while True:
    # Close Program
    if buttons.backspace:
        # Coast Motors and Stop Thread
        print("Exiting...")
        direct(11,0,0,0)
        ended = True
        leds.set_color('LEFT', 'GREEN')
        leds.set_color('RIGHT', 'GREEN')
        time.sleep(0.1)
        break

    # Pause Program
    if buttons.left:
        if run == True:
            run = False
            leds.set_color('LEFT', 'AMBER')
            leds.set_color('RIGHT', 'AMBER')
            sound(500,0.5,play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
            print("Paused")
        else:
            run = True
            leds.set_color('LEFT', 'GREEN')
            leds.set_color('RIGHT', 'GREEN')
            sound(700,0.5,play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
            print("Started")
        direct(11,0,0,0)
        while buttons.left:
            time.sleep(0.01)   

    # If Running
    if run == True: 
        # Run Functions
        if bluetoothWorking:
            if state == 1: # Has Ball
                var2 = 80
                #curve()
                var3 = 0
                var4 = 0
                turnStraight()
            if state == 2: # Goalie
                goalie()
            elif state == 3: # Attack Ball
                # Neutral Speed
                var2 = 50
                turnStraight()
        
            if state != 2:
                # Chase Ball
                goToBall()   
        else: # Bluetooth Not Working
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
            
        # Prevent Large Speed
        if (var2 + var3 + var4) > 100:
            var2 = 100
            var3 = 0
            var4 = 0

        direct(var1,var2,var3,var4)

    # If Paused
    else:
        # Coast Motors
        direct(11,0,0,0)