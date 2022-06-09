#!/usr/bin/env python3

# Import EV3DEV
from ev3dev2.button import *
from ev3dev2.console import *
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.display import *
from ev3dev2.leds import *
print("ev3dev2 Imported")

import threading
import ctypes
from time import sleep
from utils import *
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

# Initialize Brick Functions
buttons = Button()
screen = Display()
leds = Leds()

# Variables
fieldWidth=(1800)/2
speed=30
goal=compass.value()

class ultrasonicThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.distace=ultrasonic.value()
    def run(self):
        try:
            while True:
                self.distance=ultrasonic.value()
                sleep(0.2)
        finally:
            print('Killed Thread')
    def get_thread_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

# Coast Motors
def coast():
    topRight.off(brake=False)
    bottomRight.off(brake=False)
    topLeft.off(brake=False)
    bottomLeft.off(brake=False)
    
thread = ultrasonicThread('Thread 1')
thread.start()

try:
    while not buttons.right.pressed:
        sleep(0.05)
    while True:
        fp=irFront.value(0)
        bp=irBack.value(0)
        fs=[irFront.value(1),irFront.value(2),irFront.value(3),irFront.value(4),irFront.value(5)]
        bs=[irBack.value(1),irBack.value(2),irBack.value(3),irBack.value(4),irBack.value(5)]
        ang=getAngle(compass.value(),goal)
        dist=ultrasonic.value()
        usBlocked=robotNotBlocking(dist,ultrasonicThread.distance)

        position=irToPos(fp,bp,fs,bs)[0]
        strength=irToPos(fp,bp,fs,bs)[1]
        direction=moveBall(position,strength)
        drift=pointForward(ang)
        if ballPossesion(): c=curve(dist,fieldWidth)
        else: c=0

        x=speed+drift+c

        a=motorDirection(direction)[0]*x
        b=motorDirection(direction)[1]*x
        c=motorDirection(direction)[2]*x
        d=motorDirection(direction)[3]*x

        topRight.on(SpeedPercent(a))
        bottomRight.on(SpeedPercent(b))
        topLeft.on(SpeedPercent(c))
        bottomLeft.on(SpeedPercent(d))
except:
    pass
coast()
thread.raise_exception()
thread.join()