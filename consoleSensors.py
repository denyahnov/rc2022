#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor
from ev3dev2.sensor.lego import UltrasonicSensor

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

# Reset Values
centerAngle = compass.value(0)
num = 1

# Get Compass Angle relative to the Goal Angle
def getAngle(angle):
    output = angle - centerAngle
    if output < 0:
        output += 360
    return output

print("Testing Sensors...")

try:
    while True:
        input()
        print('\n---Test #' + str(num) + '---')
        print('Sensor Values:')
        print('IR-Front: '+ str(irFront.value(0)))
        print('IR-Back: '+ str(irBack.value(0)))
        print('Compass: '+ str(compass.value(0)))
        print('Goal Heading: ' + str(centerAngle))
        print('Relative Compass Heading: ' + str(getAngle(compass.value(0))))
        print('Ultrasonic: '+ str(ultrasonic.value(0)) + '\n')
        
        centerValues = [irFront.value(2),irFront.value(3)]
        sideValues = [irFront.value(1),irFront.value(4)]
        backValues = [irBack.value(1),irBack.value(2),irBack.value(3),irBack.value(4)]
        
        print('IR Strength:')
        print('IR-Center: '+ str(max(centerValues)))
        print('IR-Side: '+ str(max(sideValues)))
        print('IR-Back: '+ str(max(backValues)))
        print('--------------')

        num += 1
except:
    print('Exited')