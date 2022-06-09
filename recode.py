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
irFront = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
irBack = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")
compass = Sensor(INPUT_3, driver_name = "ht-nxt-compass")
ultrasonic = UltrasonicSensor(INPUT_4)

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"
compass.mode = "COMPASS"
ultrasonic.mode = "US-DIST-CM"

# Initialize Brick Functions
buttons = Button()
screen = Display()
leds = Leds()

# Variables
fieldWidth=(1800)/2
speed=30
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
        fp=irFront.value(0) # Front Pos
        bp=irBack.value(0) # Back Pos
        fs=[irFront.value(1),irFront.value(2),irFront.value(3),irFront.value(4),irFront.value(5)] # Front Strength
        bs=[irBack.value(1),irBack.value(2),irBack.value(3),irBack.value(4),irBack.value(5)] # Back Strength
        prox=max([irFront.value(3),irBack.value(3)]) # Center Proximity
        ang=getAngle(compass.value(),goal) # Compass Angle
        dist=ultrasonic.value() # Ultrasonic Distance
        usBlocked=robotNotBlocking(dist,ultrasonicThread.distance) # Ultrasonic Blocked by Object

        position=irToPos(fp,bp,fs,bs)[0] # Ball Position
        strength=irToPos(fp,bp,fs,bs)[1] # Ball Strength
        direction=moveBall(position,strength) # Decide Motor Direction
        drift=pointForward(ang) # Point 'North'
        if ballPossesion(prox): c=curve(dist,fieldWidth) # Curve Towards Goal
        else: c=0
        x=drift+c

        # Calc Motor Speeds
        a=(motorDirection(direction)[0]*speed)
        b=(motorDirection(direction)[1]*speed)
        c=(motorDirection(direction)[2]*speed)
        d=(motorDirection(direction)[3]*speed)s

        # Move Motors
        topRight.on(SpeedPercent(a))
        bottomRight.on(SpeedPercent(b))
        topLeft.on(SpeedPercent(c))
        bottomLeft.on(SpeedPercent(d))
except:
    print("Ended")
coast() # Stop Motors
ultrasonicThread.running = False # Kill Thread
sleep(1)