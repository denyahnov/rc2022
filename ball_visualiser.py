#!/usr/bin/env python3

from turtle import *
from utils import *
# from ev3dev2.sensor import *

# iF = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
# iB = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")

# iF.mode = "AC-ALL"
# iB.mode = "AC-ALL"

prevPos=0

def addDot(tu,pos=[0,0],color='red',size=20):
    x = pos[0]
    y = pos[1]
    
    tu.goto(x,y)
    tu.dot(size,color)
    
def ps(ballPos=0):
    if ballPos == 0 or ballPos == 12: return [0,50]
    if ballPos == 1: return [25,45]
    if ballPos == 2: return [45,25]
    if ballPos == 3: return [50,0]
    if ballPos == 4: return [45,-25]
    if ballPos == 5: return [25,-45]
    if ballPos == 6: return [0,-50]
    if ballPos == 7: return [-25,-45]
    if ballPos == 8: return [-45,-25]
    if ballPos == 9: return [-50,0]
    if ballPos == 10: return [-45,25]
    if ballPos == 11: return [-25,45]
    return [0,0]

if __name__ == "__main__":
    screen = getscreen()
    bgcolor('gray')
    title('IR Sensor Visualiser')

    tu = Turtle()
    
    tu.pu()
    tu.ht()
    tu.speed(0)
    tu.shape('circle')

    while True:     
        fp=int(input()) # Front Pos
        bp=0 # Back Pos

        fs=[0] # Front Strength
        bs=[0] # Back Strength

        x=irToPos(fp,bp,fs,bs)

        position=x[0] # Ball Position
        strength=x[1] # Ball Strength
        
        if position != prevPos:
            resetscreen()

            addDot(tu,ps(position))
            addDot(tu,[0,0],'black',60)
        prevPos=position