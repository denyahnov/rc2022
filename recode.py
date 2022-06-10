#!/usr/bin/env python3

# Import ev3dev2
from ev3dev2.button import *
from ev3dev2.console import *
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.display import *
from ev3dev2.led import *
print("ev3dev2 Imported")

# Other Imports
from utils import *
from threading import Thread
from time import sleep
print("utils Imported")

# Initialize Motors
topLeft = LargeMotor(OUTPUT_C)
topRight = LargeMotor(OUTPUT_A)
bottomLeft = LargeMotor(OUTPUT_D)
bottomRight = LargeMotor(OUTPUT_B)

# Initialize Sensors
iF = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
iB = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")
compass = Sensor(INPUT_3, driver_name = "ht-nxt-compass")
ultrasonic = UltrasonicSensor(INPUT_4)

# Set Sensor Modes
iF.mode = "AC-ALL"
iB.mode = "AC-ALL"
compass.mode = "COMPASS"
ultrasonic.mode = "US-DIST-CM"

# Initialize Brick Functions
buttons = Button()
screen = Display()
leds = Leds()

# Variables
fieldWidth=(180)/2
speed=70
goal=compass.value()

class ultrasonicThread():
    distance=ultrasonic.value()
    running=True
    def run(self):
        while self.running:
            self.distance=ultrasonic.value()
            sleep(0.2)
        print("Ended Thread")
        
# Coast Motors
def coast():
    topRight.off(brake=False)
    bottomRight.off(brake=False)
    topLeft.off(brake=False)
    bottomLeft.off(brake=False)
    
# Start Thread
thread = Thread(target=ultrasonicThread)
thread.start()

try:
    while not buttons.right:
        sleep(0.05)
    while True:
        if buttons.backspace or buttons.left:
            break
        fp=iF.value(0) # Front Pos
        bp=iB.value(0) # Back Pos
        fs=[iF.value(1),iF.value(2),iF.value(3),iF.value(4),iF.value(5)] # Front Strength
        bs=[iB.value(1),iB.value(2),iB.value(3),iB.value(4),iB.value(5)] # Back Strength
        prox=max([iF.value(3),iB.value(3)]) # Center Proximity
        ang=getAngle(compass.value(),goal) # Compass Angle
        dist=ultrasonic.value() # Ultrasonic Distance
        usBlocked=robotNotBlocking(dist,ultrasonicThread.distance) # Ultrasonic Blocked by Object

        position=irToPos(fp,bp,fs,bs)[0] # Ball Position
        strength=irToPos(fp,bp,fs,bs)[1] # Ball Strength
        direction=moveBall(position,strength,dist,fieldWidth) # Decide Motor Direction
        drift=pointForward(ang) # Point 'North'
        if ballPossesion(prox): c=curve(dist,fieldWidth) # Curve Towards Goal
        else: c=0

        # Calc Motor Speeds
        a=(motorDirection(direction)[0]*speed) + drift
        b=(motorDirection(direction)[1]*speed) + drift
        c=(motorDirection(direction)[2]*speed) + drift
        d=(motorDirection(direction)[3]*speed) + drift

        # Move Motors
        topRight.on(SpeedPercent(ms(a)))
        bottomRight.on(SpeedPercent(ms(b)))
        topLeft.on(SpeedPercent(ms(c)))
        bottomLeft.on(SpeedPercent(ms(d)))
except:
    print("Error")
    coast() # Stop Motors
    ultrasonicThread.running = False # Kill Thread
    sleep(1)
print("Ended")
coast() # Stop Motors
ultrasonicThread.running = False # Kill Thread
sleep(1)