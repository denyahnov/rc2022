#!/usr/bin/env python3
from ev3dev2.sensor import INPUT_1, INPUT_2, Sensor
from utils import irToPos

# Initialize Sensors
irFront = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
irBack = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"

print("Ready to Calibrate...")
try:
    f=open('calibrations.txt','r+')
except:
    f=open('calibrations.txt','w+')

try:
    while True:
        i=input("Predicted Ball Position: ")
        fp=irFront.value(0)
        bp=irBack.value(0)
        fs=[irFront.value(1),irFront.value(2),irFront.value(3),irFront.value(4),irFront.value(5)]
        bs=[irBack.value(1),irBack.value(2),irBack.value(3),irBack.value(4),irBack.value(5)]
        position=irToPos(fp,bp,fs,bs)[0]
        strength=irToPos(fp,bp,fs,bs)[1]
        x=f'{i},{position},{strength}'
        print(x)
        f.write(x+'\n')
except:
    pass
f.close()