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

# Get Motor Direction
def motorDirection(direction):
    match direction:
        case 0:
            return 0,0,0,0
        case 1:
            return -1,0,0,1
        case 2:
            return -1,-1,1,1
        case 3:
            return 0,-1,1,0
        case 4:
            return 1,-1,1,-1
        case 5:
            return 1,0,0,-1
        case 6:
            return 1,1,-1,-1
        case 7:
            return 0,1,-1,0
        case 8:
            return -1,1,-1,1

def pointForward(angle):
    if 2 < angle < 181:
        return 7 + (round((angle+2)/15))
    elif 358 > angle > 180:
        return (20 - (round((angle+2)/30)))*-1
    else:
        return 0

def getPos(distance,fieldWidth):
    if distance > (fieldWidth+80):
        return 1
    elif distance < (fieldWidth-80):
        return 2
    else:
        return 0

def irToPos(fp,bp,fs,bs):
    if fp > 0:
        match fp:
            case 1: return 1,fs[0]
            case 2: return 2,fs[0]
            case 3: return 3,fs[1]
            case 4: return 4,fs[1]
            case 5: return 5,fs[2]
            case 6: return 6,fs[3]
            case 7: return 7,fs[3]
            case 8: return 8,fs[4]
            case 9: return 9,fs[4]
    elif bp > 0:
        match bp:
            case 1: return 9,bs[4]
            case 2: return 8,bs[4]
            case 3: return 7,bs[3]
            case 4: return 6,bs[3]
            case 5: return 5,bs[2]
            case 6: return 4,bs[1]
            case 7: return 3,bs[1]
            case 8: return 2,bs[0]
            case 9: return 1,bs[0]
    else:
        return 0,0

def moveBall(pos,strength):
    match pos:
        case 0:
            return 0
        case 1:
            return 6
        case 2:
            return 6
        case 3:
            if strength > 130:
                return 7
            else:
                return 8
        case 4:
            if strength > 100:
                return 1
            else:
                return 8
        case 5:
            return 2
        case 6:
            if strength > 100:
                return 3
            else:
                return 4
        case 7:
            if strength > 130:
                return 5
            else:
                return 4
        case 8:
            return 6
        case 9:
            return 6
        case _:
            return 0

def curve(dist,field):
    p=getPos(dist,field)
    match p:
        case 0: return 0
        case 1: return 5
        case 2: return-5