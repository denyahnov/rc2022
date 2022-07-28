from turtle import *
import time 

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

screen = getscreen()
bgcolor('gray')
title('IR Sensor Visualiser')

tu = Turtle()
tu.pu()
tu.speed(0)
tu.shape('circle')

while True:
    clearscreen()
    for i in range(13):
        addDot(tu,ps(i-1))
    addDot(tu,[0,0],'black',60)
    input()