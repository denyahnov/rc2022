#!/usr/bin/env python3
import time

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor, I2cSensor
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.display import Display
from ev3dev2.button import Button

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

# Initialize Buttons
buttons = Button()

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"
compass.mode = "COMPASS"
ultrasonic.mode = "US-DIST-CM"

# Reset Values
topLeft.reset()
topRight.reset()
bottomLeft.reset()
bottomRight.reset()
centerAngle = compass.value(0)

# Get Compass Angle relative to the Goal Angle
def getAngle(angle):
    output = angle - centerAngle
    if output < 0:
        output += 360
    return output

print("Outputting Values...")

while True:
    # Close Program
    if buttons.backspace:
        print("Exiting...")
        break

    if buttons.left:
        while buttons.left:
            time.sleep(0.001)
        content = '\nIR-Values:'
        content += '\nFront0: ' + str(irFront.value(0))
        content += '\nFront1: ' + str(irFront.value(1))
        content += '\nFront2: ' + str(irFront.value(2))
        content += '\nFront3: ' + str(irFront.value(3))
        content += '\nFront4: ' + str(irFront.value(4))
        content += '\nFront5: ' + str(irFront.value(5))
        content += '\n'
        content += '\nBack0: ' + str(irBack.value(0))
        content += '\nBack1: ' + str(irBack.value(1))
        content += '\nBack2: ' + str(irBack.value(2))
        content += '\nBack3: ' + str(irBack.value(3))
        content += '\nBack4: ' + str(irBack.value(4))
        content += '\nBack5: ' + str(irBack.value(5))

        print(content)

        