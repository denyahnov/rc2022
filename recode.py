#!/usr/bin/env python3

# Import ev3dev2
from ev3dev2.button import *
from ev3dev2.console import *
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.led import *
from ev3dev2.sound import *
from ev3dev2.power import *
print("ev3dev2 Imported")

# Other Imports
from traceback import print_exc
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
sound = Sound()
leds = Leds()
battery = PowerSupply()
paused = False

# Variables
fieldWidth=(1000)/2
topspeed=60
speed=40
slowspeed=20
sp=speed
goal=compass.value()

class ultrasonicThread():
    distance=ultrasonic.value()
    running=True
    def ulthread():
        try:
            print("Running Thread")
            while ultrasonicThread.running:
                ultrasonicThread.distance=ultrasonic.value()
                sleep(0.2)
            print("Ended Thread")
        except:
            print("Thread Error")
        
# Coast Motors
def coast():
    topRight.off(brake=False)
    bottomRight.off(brake=False)
    topLeft.off(brake=False)
    bottomLeft.off(brake=False)
    
# Start Thread
#thread = Thread(target=ultrasonicThread.ulthread)
#thread.start()

leds.set_color('LEFT', 'AMBER')
leds.set_color('RIGHT', 'AMBER')
sound.set_volume(20)
sound.play_tone(650,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
print("Battery:",battery.measured_voltage)

try:
    while not buttons.right:
        sleep(0.05)
    while buttons.right:
        sleep(0.03)
    leds.set_color('LEFT', 'GREEN')
    leds.set_color('RIGHT', 'GREEN')
    while True:
        if buttons.right:
            coast()
            paused = not paused
            sound.play_tone(450,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE) if paused else sound.play_tone(650,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
            while buttons.right:
                sleep(0.05)
        if buttons.backspace or buttons.left:
            break
        if paused: continue
        fp=iF.value(0) # Front Pos
        bp=iB.value(0) # Back Pos
        fs=[iF.value(1),iF.value(2),iF.value(3),iF.value(4),iF.value(5)] # Front Strength
        bs=[iB.value(1),iB.value(2),iB.value(3),iB.value(4),iB.value(5)] # Back Strength
        ang=getAngle(compass.value(),goal) # Compass Angle
        try: dist=ultrasonic.value() # Ultrasonic Distance
        except: dist=0 # Cant Get Distance
        stalled=topLeft.is_stalled
        usBlocked=robotNotBlocking(dist,ultrasonicThread.distance) # Ultrasonic Blocked by Object

        position=irToPos(fp,bp,fs,bs)[0] # Ball Position
        strength=irToPos(fp,bp,fs,bs)[1] # Ball Strength
        direction=moveBall(position,strength,dist,fieldWidth,False) # Decide Motor Direction
        drift=pointForward(ang,speed) # Point 'North'
        if 129 < iF.value(3): 
            #sound.play_tone(520,0.5,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
            cv=curve(dist,fieldWidth,topspeed) # Curve Towards Goal
            cv=0
            if sp < topspeed: sp*=1.03
            if sp > topspeed: sp=topspeed
        else:
            cv=0
            if sp > speed: sp*=0.99
            if sp < speed: sp=speed
        if direction == 0: direction=center(dist,fieldWidth); sp=slowspeed
        if cv != 0: drift=0
        #if drift < 0: sp+=5
        
        # Calc Motor Speeds
        a=(motorDirection(direction)[0]*sp) + drift + cv
        b=(motorDirection(direction)[1]*sp) + drift + cv
        c=(motorDirection(direction)[2]*sp) + drift + cv
        d=(motorDirection(direction)[3]*sp) + drift + cv

        # Move Motors
        topRight.on(SpeedPercent(ms(a)))
        bottomRight.on(SpeedPercent(ms(b)))
        topLeft.on(SpeedPercent(ms(c)))
        bottomLeft.on(SpeedPercent(ms(d)))
except Exception:
    print("Error")
    print_exc()
    coast() # Stop Motors
    sleep(1)
    ultrasonicThread.running = False # Kill Thread
    sleep(1)
except:
    print("Interrupted")
    coast() # Stop Motors
    sleep(1)
print("Ended")
coast() # Stop Motors
sleep(1)
ultrasonicThread.running = False # Kill Thread
sleep(1)