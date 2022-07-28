from turtle import *
import time 

screen = getscreen()
bgcolor('gray')
title('IR Sensor Visualiser')

tu = Turtle()
tu.shape('circle')

tu.goto(0,0)
tu.dot(20,'black')

tu.goto(0,0)
tu.dot(20,'red')

tu.goto(0,50)
tu.dot(20,'red')

tu.goto(50,0)
tu.dot(20,'red')

tu.goto(0,-50)
tu.dot(20,'red')

tu.goto(-50,0)
tu.dot(20,'red')

tu.goto(0,50)
tu.dot(20,'red')

tu.goto(0,0)
tu.dot(20,'black')

time.sleep(5)