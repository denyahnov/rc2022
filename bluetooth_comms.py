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

from recode import comms
        
# Coast Motors
def coast():
    topRight.off(brake=False)
    bottomRight.off(brake=False)
    topLeft.off(brake=False)
    bottomLeft.off(brake=False)

if comms.Begin(comms,0) != 0: # Begin Bluetooth Comms
    comms.state = 0 
    comms_thread = threading.Thread(target=comms.loop)
    comms_thread.start()
leds.set_color('LEFT', 'AMBER')
leds.set_color('RIGHT', 'AMBER')
sound.set_volume(20)
sound.play_tone(650,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
print("Battery:",round(battery.measured_volts,2))

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
        print(comms.state + " | " + comms.teammate + "             ",end='\r')
        comms.state+=1
except Exception:
    print("Error")
    print_exc()
    comms.enabled = False
    coast() # Stop Motors
    sleep(1)
except:
    print("Interrupted")
    comms.enabled = False
    coast() # Stop Motors
    sleep(1)
print("Ended")
comms.enabled = False
coast() # Stop Motors
sleep(1)