#!/usr/bin/env python3

# Check if an Object is Blocking Ultrasonic
def robotNotBlocking(oldDistance, newDistance):
    # Get Distance Change
    distanceChange = abs(oldDistance - newDistance)

    # Check for Rapid Increase in Distance from Wall
    if (distanceChange > 30):
        return False
    else:
        return True

# Get Compass Angle relative to the Goal Angle
def getAngle(angle, centerAngle):
    output = angle - centerAngle

    if output < 0:
        output += 360

    return output

# Check if Robot has Possesion of the Ball
def ballPossesion(centerStrength):
    if 150 < centerStrength < 300:
        return True
    else:
        return False

# 8-Direction Motor Movement
#  1  2  3
#  8  0  4
#  7  6  5
def motorDirection(direction):
    if direction == 0:
        return 0,0,0,0
    elif direction == 1:
        return -1,0,0,1
    elif direction == 2:
        return -1,-1,1,1
    elif direction == 3:
        return 0,-1,1,0
    elif direction == 4:
        return 1,-1,1,-1
    elif direction == 5:
        return 1,0,0,-1
    elif direction == 6:
        return 1,1,-1,-1
    elif direction == 7:
        return 0,1,-1,0
    elif direction == 8:
        return -1,1,-1,1

# Points towards 'North'
def pointForward(angle):
    if 2 < angle < 181:
        return (round((angle+2)/7.5))*-1
    elif 358 > angle > 180:
        return 25 - (round((angle+2)/15))
    else:
        return 0

# Get robot position on field
def getPos(distance,fieldWidth):
    if distance > (fieldWidth+80):
        return 1
    elif distance < (fieldWidth-80):
        return 2
    else:
        return 0

# Convert IR Inputs to a Pos Value and Strength Value
def irToPos(fp,bp,fs,bs):
    if 1 < fp < 9:
        i=(fp*30)-150
        if i < 0: i+=360
        return i,max(fs)
    elif 1 < bp < 9:
        i=(bp*30)+30
        if i < 0: i+=360
        return i,max(bs)
    elif fp > 0:
        i=(fp*30)-150
        if i < 0: i+=360
        return i,max(fs)
    elif bp > 0:
        i=(bp*30)+30
        if i < 0: i+=360
        return i,max(bs)
    else:
        return -1,-1

# Convert IR position to Motor Direction
def moveBall(pos,strength,dist,fieldWidth):
    if 314 < pos < 330:
        return 1
    elif 329 < pos < 361 or -1 < pos < 30:
        return 2
    elif 29 < pos < 45:
        return 3
    elif 44 < pos < 90:
        return 4
    elif 89 < pos < 135:
        return 7
    elif 134 < pos < 215:
        if getPos(dist,fieldWidth) == 1:
            return 4
        else:
            return 8
    elif 214 < pos < 270:
        return 5
    elif 269 < pos < 315:
        return 8
    else:
        return 0

# Curve towards Goal
def curve(dist,field):
    p=getPos(dist,field)
    if p== 0: return 0
    elif p== 1: return 5
    elif p== 2: return-5