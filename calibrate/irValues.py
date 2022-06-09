#!/usr/bin/env python3
from ev3dev2.sensor import INPUT_1, INPUT_2, Sensor
from ev3dev2.button import Button

# Initialize Sensors
irFront = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
irBack = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")

# Initialize Buttons
buttons = Button()

# Set Sensor Modes
irFront.mode = "AC-ALL"
irBack.mode = "AC-ALL"

print("Outputting Values...")

while True:
    # Close Program
    if buttons.backspace:
        print("Exiting...")
        break

    input()
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