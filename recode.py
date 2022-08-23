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
paused = True

# Variables
fieldWidth=(1700)/2 # Min [650-700], Max [1000]
topspeed=90
speed=60
slowspeed=30
sp=speed
goal=compass.value()
ultrasonic_values=[]
outliers=0

# COMM STATES:
# -1 : Offline
#  0 : Idle
#  1 : Attacking
#  2 : Defending

class comms():
    address = '00:16:53:42:2B:99'
    port = 1000
    client = None
    state = -1
    teammate = -1
    enabled = True
    server = False
    def Begin(self):
        try:
            self.client = CommClient(self.address,self.port)
            self.server = False
            return 1
        except:
            server = CommServer(self.address,self.port)
            self.client = server.accept_client()
            self.server = True
            return 2
        return 0
    def loop(self):
        while self.enabled:
            self.client.send(str(self.state))
            self.teammate = int(self.client.recv(1024))
        
# Coast Motors
def coast():
    topRight.off(brake=False)
    bottomRight.off(brake=False)
    topLeft.off(brake=False)
    bottomLeft.off(brake=False)

#if comms.Begin(comms) != 0: comms.state=0 # Begin Bluetooth Comms
leds.set_color('LEFT', 'AMBER')
leds.set_color('RIGHT', 'AMBER')
sound.set_volume(20)
sound.play_tone(650,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
print("Battery:",battery.measured_voltage)

try:
    while not buttons.right: sleep(0.05)
    while buttons.right: sleep(0.05)
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

        fp = iF.value(0) # Front Pos
        bp = iB.value(0) # Back Pos

        fs = [iF.value(1),iF.value(2),iF.value(3),iF.value(4),iF.value(5)] # Front Strength
        bs = [iB.value(1),iB.value(2),iB.value(3),iB.value(4),iB.value(5)] # Back Strength

        ang = getAngle(compass.value(),goal) # Compass Angle

        try: 
            ultrasonic_values, outliers = ultrasonicValue(ultrasonic.value(),ultrasonic_values,outliers) # Get Average Ultrasonic Values
            dist = sum(ultrasonic_values)/len(ultrasonic_values)
        except: 
            dist = 0 # Cant Get Distance

        stalled = topLeft.is_stalled

        x = irToPos(fp,bp,fs,bs)

        position = x[0] # Ball Position
        strength = x[1] # Ball Strength
        
        #if comms.teammate == 1: comms.state=2; position=-1
        direction = moveBall(position,strength,dist,fieldWidth,False,2) # Decide Motor Direction

        drift = pointForward(ang,speed) # Point 'North'

        if 129 < iF.value(3): 
            cv = curve(dist,fieldWidth,topspeed) # Curve Towards Goal
            if sp < topspeed: sp*=1.03
            if sp > topspeed: sp=topspeed
        else:
            cv = 0
            if sp > speed: sp*=0.99
            if sp < speed: sp=speed

        if direction == 0: 
            direction=center(dist,fieldWidth); sp=slowspeed

        if cv != 0: drift=0
        
        f=motorDirection(direction)
        
        # Calc Motor Speeds
        a=(f[0]*sp) + drift + cv
        b=(f[1]*sp) + drift + cv
        c=(f[2]*sp) + drift + cv
        d=(f[3]*sp) + drift + cv

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
except:
    print("Interrupted")
    coast() # Stop Motors
    sleep(1)
print("Ended")
coast() # Stop Motors
sleep(1)
