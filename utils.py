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
        return 7 + (round((angle+2)/15))
    elif 358 > angle > 180:
        return (20 - (round((angle+2)/30)))*-1
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
    if fp > 0:
        if fp == 1: return 1,fs[0]
        elif fp == 2: return 2,fs[0]
        elif fp == 3: return 3,fs[1]
        elif fp == 4: return 4,fs[1]
        elif fp == 5: return 5,fs[2]
        elif fp == 6: return 6,fs[3]
        elif fp == 7: return 7,fs[3]
        elif fp == 8: return 8,fs[4]
        elif fp == 9: return 9,fs[4]
        else: return 0,0
    elif bp > 0:
        if bp == 1: return 9,bs[4]
        elif bp == 2: return 8,bs[4]
        elif bp == 3: return 7,bs[3]
        elif bp == 4: return 6,bs[3]
        elif bp == 5: return 5,bs[2]
        elif bp == 6: return 4,bs[1]
        elif bp == 7: return 3,bs[1]
        elif bp == 8: return 2,bs[0]
        elif bp == 9: return 1,bs[0]
        else: return 0,0
    else:
        return 0,0

# Convert IR position to Motor Direction
def moveBall(pos,strength):
    if pos == 0:
        return 0
    elif pos == 1:
        return 6
    elif pos == 2:
        return 6
    elif pos == 3:
        if strength > 130:
            return 7
        else:
            return 8
    elif pos == 4:
        if strength > 100:
            return 1
        else:
            return 8
    elif pos == 5:
        return 2
    elif pos == 6:
        if strength > 100:
            return 3
        else:
            return 4
    elif pos == 7:
        if strength > 130:
            return 5
        else:
            return 4
    elif pos == 8:
        return 6
    elif pos == 9:
        return 6
    else:
        return 0

# Curve towards Goal
def curve(dist,field):
    p=getPos(dist,field)
    if p== 0: return 0
    elif p== 1: return 5
    elif p== 2: return-5